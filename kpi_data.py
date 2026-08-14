from __future__ import annotations

from numbers import Number
from pathlib import Path
from typing import BinaryIO

import pandas as pd


REQUIRED_COLUMNS = ("Job", "Name", "KPI")
NOT_APPLICABLE_TOKENS = {"NA", "N/A", "不适用"}


def _text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _is_not_applicable(value: object) -> bool:
    return _text(value).upper() in NOT_APPLICABLE_TOKENS


def parse_month_header(value: object) -> pd.Timestamp | None:
    """Convert Excel date headers, datetime headers, or strings such as 2026/2."""
    if isinstance(value, (pd.Timestamp,)):
        return value.to_period("M").to_timestamp()

    if hasattr(value, "year") and hasattr(value, "month"):
        try:
            return pd.Timestamp(value).to_period("M").to_timestamp()
        except (TypeError, ValueError):
            pass

    if isinstance(value, Number) and not isinstance(value, bool):
        try:
            parsed = pd.to_datetime(
                float(value), unit="D", origin="1899-12-30", errors="raise"
            )
            return parsed.to_period("M").to_timestamp()
        except (TypeError, ValueError, OverflowError):
            return None

    text = _text(value)
    if not text:
        return None
    try:
        parsed = pd.to_datetime(text, errors="raise")
        return parsed.to_period("M").to_timestamp()
    except (TypeError, ValueError):
        return None


def classify_kpi(kpi: str) -> tuple[str, str]:
    key = kpi.lower().replace(" ", "")
    if "原因" in key or "reason" in key:
        return "reason", "未准时原因"
    if any(token in key for token in ("未准时", "次数", "count", "数量")):
        return "count", "异常次数"
    if any(token in key for token in ("l/t", "leadtime", "周期", "时长", "天数")):
        return "duration", "L/T"
    if any(token in key for token in ("ontime", "准时", "准确率", "交付")):
        return "rate", "准时交付"
    if any(token in key for token in ("一次通过", "rft", "bom", "pap", "tf", "3d")):
        return "rate", "RFT"
    return "rate", "其他比率"


def target_for_kpi(kpi: str, metric_type: str) -> float | None:
    key = kpi.lower().replace(" ", "")
    if metric_type == "reason":
        return None
    if metric_type == "count":
        return 2.0
    if metric_type == "duration":
        return None
    if any(
        token in key
        for token in ("bom", "3d", "goprod", "开发准时", "sotpace", "ontime")
    ):
        return 1.0
    if any(token in key for token in ("pap", "tf", "样品一次", "rft")):
        return 0.95
    return 0.95


def load_kpi_data(
    source: str | Path | BinaryIO,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Read the second worksheet and reshape the wide monthly table to long form."""
    excel = pd.ExcelFile(source, engine="openpyxl")
    dashboard_sheets = [
        name
        for name in excel.sheet_names
        if "database for dashboard" in name.lower()
    ]
    if dashboard_sheets:
        sheet_name = dashboard_sheets[-1]
    elif "工作表2" in excel.sheet_names:
        sheet_name = "工作表2"
    elif len(excel.sheet_names) >= 2:
        sheet_name = excel.sheet_names[1]
    else:
        sheet_name = excel.sheet_names[0]

    preview = pd.read_excel(
        excel, sheet_name=sheet_name, header=None, keep_default_na=False
    )
    first_row_keys = [_text(value).lower() for value in preview.iloc[0, :3]]
    first_year_value = pd.to_numeric(
        pd.Series([preview.iat[0, 3]]), errors="coerce"
    ).iloc[0]
    first_month_value = pd.to_numeric(
        pd.Series([preview.iat[1, 3]]), errors="coerce"
    ).iloc[0]
    two_row_month_header = (
        first_row_keys == ["job", "name", "kpi"]
        and pd.notna(first_year_value)
        and 1900 <= int(first_year_value) <= 2200
        and pd.notna(first_month_value)
        and 1 <= int(first_month_value) <= 12
    )

    if two_row_month_header:
        selected_columns = [0, 1, 2]
        month_headers: list[pd.Timestamp] = []
        current_year: int | None = None
        for column_index in range(3, preview.shape[1]):
            year_value = pd.to_numeric(
                pd.Series([preview.iat[0, column_index]]), errors="coerce"
            ).iloc[0]
            if pd.notna(year_value) and 1900 <= int(year_value) <= 2200:
                current_year = int(year_value)
            month_value = pd.to_numeric(
                pd.Series([preview.iat[1, column_index]]), errors="coerce"
            ).iloc[0]
            if current_year is None or pd.isna(month_value):
                continue
            month_number = int(month_value)
            if not 1 <= month_number <= 12:
                continue
            selected_columns.append(column_index)
            month_headers.append(pd.Timestamp(current_year, month_number, 1))

        raw = preview.iloc[2:, selected_columns].copy()
        raw.columns = ["Job", "Name", "KPI", *month_headers]
    else:
        raw = pd.read_excel(excel, sheet_name=sheet_name, keep_default_na=False)
    if raw.shape[1] < 4:
        raise ValueError("数据表至少需要 Job、Name、2级KPI 和一个月份列。")

    first_three = list(raw.columns[:3])
    raw = raw.rename(
        columns={
            first_three[0]: "Job",
            first_three[1]: "Name",
            first_three[2]: "KPI",
        }
    )

    raw["Job"] = raw["Job"].map(_text)
    raw["Name"] = raw["Name"].map(_text)
    raw["KPI"] = raw["KPI"].map(_text)
    raw = raw[(raw["Job"] != "") & (raw["Name"] != "") & (raw["KPI"] != "")].copy()
    roster = (
        raw[["Job", "Name"]]
        .drop_duplicates()
        .sort_values(["Job", "Name"])
        .to_dict("records")
    )

    month_columns: dict[object, pd.Timestamp] = {}
    for column in raw.columns[3:]:
        parsed = parse_month_header(column)
        if parsed is not None:
            month_columns[column] = parsed
    if not month_columns:
        raise ValueError("未识别到月份列。月份表头请使用 Excel 日期或 YYYY/M 格式。")

    melted = raw.melt(
        id_vars=list(REQUIRED_COLUMNS),
        value_vars=list(month_columns),
        var_name="MonthColumn",
        value_name="RawValue",
    )
    melted["Month"] = melted["MonthColumn"].map(month_columns)
    melted["Value"] = pd.to_numeric(melted["RawValue"], errors="coerce")
    not_applicable_mask = melted["RawValue"].map(_is_not_applicable)
    reporting_months = sorted(
        melted.loc[melted["RawValue"].map(_text).ne(""), "Month"]
        .drop_duplicates()
        .tolist()
    )

    classifications = melted["KPI"].map(classify_kpi)
    melted["MetricType"] = classifications.map(lambda item: item[0])
    melted["KPIGroup"] = classifications.map(lambda item: item[1])
    reason_mask = melted["MetricType"].eq("reason")
    melted["Reason"] = (
        melted["RawValue"]
        .map(_text)
        .where(reason_mask & ~not_applicable_mask, "")
    )

    invalid_numeric = int(
        (
            ~reason_mask
            & ~not_applicable_mask
            & melted["RawValue"].notna()
            & melted["RawValue"].map(_text).ne("")
            & melted["Value"].isna()
        ).sum()
    )
    valid_reason = reason_mask & melted["Reason"].ne("")
    melted = melted[melted["Value"].notna() | valid_reason].copy()

    rate_mask = melted["MetricType"].eq("rate")
    percent_mask = rate_mask & melted["Value"].abs().gt(1.5)
    melted.loc[percent_mask, "Value"] = melted.loc[percent_mask, "Value"] / 100

    melted["Target"] = [
        target_for_kpi(kpi, metric_type)
        for kpi, metric_type in zip(melted["KPI"], melted["MetricType"])
    ]
    melted["TargetMet"] = melted.apply(
        lambda row: (
            row["Value"] <= row["Target"]
            if row["MetricType"] == "count" and pd.notna(row["Target"])
            else row["Value"] >= row["Target"]
            if pd.notna(row["Target"])
            else pd.NA
        ),
        axis=1,
    )

    duplicate_count = int(
        melted.duplicated(["Job", "Name", "KPI", "Month"], keep=False).sum()
    )
    melted = (
        melted.sort_values(["Month", "Job", "Name", "KPI"])
        .reset_index(drop=True)
        .drop(columns=["MonthColumn", "RawValue"])
    )

    info = {
        "sheet_name": sheet_name,
        "sheet_names": excel.sheet_names,
        "row_count": len(raw),
        "data_points": len(melted),
        "invalid_numeric": invalid_numeric,
        "duplicate_count": duplicate_count,
        "month_count": melted["Month"].nunique(),
        "employee_count": len({item["Name"] for item in roster}),
        "job_count": len({item["Job"] for item in roster}),
        "reason_count": int(melted["MetricType"].eq("reason").sum()),
        "not_applicable_count": int(not_applicable_mask.sum()),
        "reporting_months": reporting_months,
        "roster": roster,
    }
    return melted, info


def period_detail(data: pd.DataFrame) -> pd.DataFrame:
    data = data[data["MetricType"].ne("reason")].copy()
    if data.empty:
        return pd.DataFrame()

    latest_month = data["Month"].max()
    latest = (
        data[data["Month"].eq(latest_month)]
        .groupby(["Job", "Name", "KPI", "MetricType", "KPIGroup"], as_index=False)
        .agg(Latest=("Value", "mean"), Target=("Target", "mean"))
    )
    average = (
        data.groupby(["Job", "Name", "KPI"], as_index=False)
        .agg(PeriodAverage=("Value", "mean"), Months=("Month", "nunique"))
    )
    result = latest.merge(average, on=["Job", "Name", "KPI"], how="outer")

    def status(row: pd.Series) -> str:
        if pd.isna(row.get("Latest")) or pd.isna(row.get("Target")):
            return "—"
        if row["MetricType"] == "count":
            return "达标" if row["Latest"] <= row["Target"] else "需关注"
        return "达标" if row["Latest"] >= row["Target"] else "需关注"

    result["Status"] = result.apply(status, axis=1)
    return result.sort_values(["Job", "Name", "KPI"]).reset_index(drop=True)
