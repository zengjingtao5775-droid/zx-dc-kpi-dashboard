from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from google_source import download_google_sheet
from kpi_data import load_kpi_data, period_detail


APP_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = APP_DIR / "data" / "DCKPI Dashboard.xlsx"
GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1msT7WcjkYva2yojVNrET2xJfqRS00xH85j1D85Ne36Q/edit?usp=sharing"
)
DECATHLON_BLUE = "#0082C3"
DECATHLON_DARK_BLUE = "#005A9C"
PALE_BLUE = "#EFF8FD"
GREEN = "#54B435"
DARK_GREEN = "#1F7A3D"
YELLOW = "#F2C94C"
ORANGE = "#F2994A"
PINK = "#F36FB4"
ME_PURPLE = "#7B61FF"
RED = "#EB5757"
BLUE = DECATHLON_BLUE
DESIGNER_BLUE = "#2EA8E5"
INK = "#12324A"
MUTED = "#5E7482"
DATA_SCHEMA_VERSION = 7

ROLE_STYLE = {
    "IE": {"zh": "工程", "en": "IE", "color": PINK},
    "PIS": {"zh": "产品导入", "en": "PIS", "color": GREEN},
    "Modelist": {"zh": "版师", "en": "Modelist", "color": ORANGE},
    "Designer": {"zh": "设计", "en": "Designer", "color": DESIGNER_BLUE},
    "Design": {"zh": "设计", "en": "Designer", "color": DESIGNER_BLUE},
    "ME": {"zh": "IE", "en": "IE", "color": ME_PURPLE},
}
st.set_page_config(
    page_title="ZX DC KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp { background: #EFF8FD; color: #12324A; }
      [data-testid="stSidebar"] { background: #005A9C; }
      [data-testid="stSidebar"] * { color: #F4FBFF; }
      [data-testid="stSidebar"] .stButton button,
      [data-testid="stSidebar"] .stDownloadButton button,
      [data-testid="stSidebar"] [data-testid="stLinkButton"] a {
        background: #EAF7FF; color: #005A9C; border: 0;
      }
      [data-testid="stSidebar"] .stButton button *,
      [data-testid="stSidebar"] .stDownloadButton button *,
      [data-testid="stSidebar"] [data-testid="stLinkButton"] a * {
        color: #005A9C !important;
      }
      [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #F4FBFF; border-color: #A7D8F2;
      }
      [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        color: #164B68 !important;
      }
      [data-testid="stMetric"] {
        background: white; border: 1px solid #D6EAF5; border-radius: 14px;
        padding: 18px 20px; box-shadow: 0 5px 16px rgba(0,130,195,.07);
        height: 112px; box-sizing: border-box;
        display: flex; flex-direction: column; justify-content: center;
      }
      [data-testid="stMetricLabel"] { color: #5E7482; }
      [data-testid="stMetricValue"] { color: #12324A; }
      .hero-panel {
        background: linear-gradient(135deg, #0082C3 0%, #005A9C 100%);
        border-radius: 18px; padding: 26px 30px; margin-bottom: 22px;
        box-shadow: 0 12px 28px rgba(0,90,156,.18);
      }
      .dashboard-title { font-size: 2.15rem; font-weight: 750; color: #FFFFFF; }
      .dashboard-subtitle {
        color: #FFFFFF; margin-top: 7px; line-height: 1.45;
        font-size: 1rem; font-weight: 650;
        overflow-wrap: anywhere;
      }
      .dashboard-subtitle-zh {
        display: block; color: #D7F1FF; font-size: .82rem; font-weight: 500;
        margin-top: 2px;
      }
      .team-structure { font-size: .92rem; opacity: .98; }
      .module-summary {
        display: flex; align-items: center; justify-content: space-between;
        gap: 18px; margin: 12px 0 14px; padding: 12px 18px;
        background: #FFFFFF; border: 1px solid #D6EAF5; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,130,195,.05);
      }
      .module-summary-label { color: #5E7482; font-size: .88rem; }
      .module-summary-value { color: #12324A; font-size: 1.65rem; font-weight: 700; }
      .module-summary-zh { font-size: .78rem; opacity: .82; }
      .role-chip { display: inline-flex; align-items: center; margin-right: 12px; }
      .role-dot {
        display: inline-block; width: 10px; height: 10px; border-radius: 3px;
        margin-right: 5px; box-shadow: 0 0 0 1px rgba(255,255,255,.65);
      }
      .st-key-selected_kpi_module {
        width: 100% !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] {
        display: block !important; width: 100% !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(11, minmax(0, 1fr)) !important;
        gap: 4px !important; width: 100% !important;
        overflow: visible !important; padding-bottom: 3px !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button {
        width: 100% !important; min-height: 4.1rem !important;
        padding: .66rem .35rem !important;
        border-width: 2px !important; border-radius: 10px !important;
        font-size: .82rem !important; font-weight: 700 !important;
        justify-content: center !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button p {
        font-size: .75rem !important; line-height: 1.16 !important;
        white-space: pre-line !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(1),
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(2) {
        border-color: #F2994A !important; background: #FFF3E8 !important; color: #A95108 !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(3),
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(4),
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(5),
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(6) {
        border-color: #7B61FF !important; background: #F3F0FF !important; color: #5239C7 !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(7) {
        border-color: #2EA8E5 !important; background: #EAF7FF !important; color: #005A9C !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(n+8) {
        border-color: #54B435 !important; background: #EEF9EA !important; color: #1F7A3D !important;
      }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(1)[kind="pillsActive"],
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(2)[kind="pillsActive"] { background: #F2994A !important; color: white !important; }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(3)[kind="pillsActive"],
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(4)[kind="pillsActive"],
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(5)[kind="pillsActive"],
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(6)[kind="pillsActive"] { background: #7B61FF !important; color: white !important; }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(7)[kind="pillsActive"] { background: #2EA8E5 !important; color: white !important; }
      .st-key-selected_kpi_module [data-testid="stButtonGroup"] [role="radiogroup"] button:nth-child(n+8)[kind="pillsActive"] { background: #54B435 !important; color: white !important; }
      .st-key-ui_language [data-testid="stButtonGroup"] { justify-content: flex-end; }
      .st-key-ui_language button { min-width: 92px; font-weight: 700; }
      .section-note {
        background: #EAF7FF; border-left: 4px solid #0082C3; border-radius: 8px;
        padding: 11px 14px; color: #164B68; margin: 6px 0 14px;
      }
      .status-chip {
        display: inline-block; border-radius: 999px; padding: 4px 10px;
        background: #EAF7FF; color: #005A9C; font-size: .82rem; font-weight: 650;
      }
      h1, h2, h3 { color: #12324A; }
      div[data-testid="stPlotlyChart"] {
        background: white; border: 1px solid #D6EAF5; border-radius: 14px;
        padding: 8px; box-shadow: 0 5px 16px rgba(0,130,195,.05);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

language_space, language_col = st.columns([5, 1.35])
with language_col:
    language = st.segmented_control(
        "Language / 语言",
        options=["zh", "en"],
        format_func=lambda value: "中文" if value == "zh" else "English",
        default="zh",
        key="ui_language",
        label_visibility="collapsed",
        width="stretch",
    ) or "zh"

IS_ZH = language == "zh"


def tr(zh: str, en: str) -> str:
    return zh if IS_ZH else en


KPI_ENGLISH = {
    "3D 交付产品100%准确": "3D Delivery Accuracy",
    "BOM 一次通过率": "BOM RFT",
    "GO PROD ontime": "GO PROD on time",
    "PAP 一次通过率": "PAP RFT",
    "SOT PACE中的交付准确率": "SOT PACE Delivery Accuracy",
    "TF 一次通过率": "TF RFT",
    "开发准时完成率": "Development On-time Completion Rate",
    "未准时提交的原因": "Late Submission Reason",
    "未准时提交的次数": "Late Submission Count",
    "样品一次通过率": "Sample RFT",
}
KPI_CHINESE = {
    "3D RFT": "3D 一次通过率",
    "TP BOM RFT": "TP BOM 一次通过率",
    "TP BOM ON TIME": "TP BOM 准时交付",
    "TP PAP RFT": "TP PAP 一次通过率",
    "TP PAP ON TIME": "TP PAP 准时交付",
    "Marker RFT": "MARKER 一次通过率",
    "Marker ON TIME": "MARKER 准时交付",
    "SOT RFT": "SOT 一次通过率",
    "SOT ON TIME": "SOT 准时交付",
    "SSS RFT": "SSS 一次通过率",
    "SSS ON TIME": "SSS 准时交付",
    "PPS RFT": "PPS 一次通过率",
    "PPS ON TIME": "PPS 准时交付",
}
KPI_GROUP_ENGLISH = {
    "准时交付": "On-time Delivery",
    "异常次数": "Exception Count",
    "未准时原因": "Late Submission Reason",
}


def display_kpi(value: object) -> str:
    text = str(value)
    return KPI_CHINESE.get(text, text) if IS_ZH else KPI_ENGLISH.get(text, text)


def display_kpi_group(value: object) -> str:
    text = str(value)
    return text if IS_ZH else KPI_GROUP_ENGLISH.get(text, text)


@st.cache_data(show_spinner=False)
def load_bytes(
    file_bytes: bytes, schema_version: int
) -> tuple[pd.DataFrame, dict[str, object]]:
    _ = schema_version
    return load_kpi_data(BytesIO(file_bytes))


@st.cache_data(show_spinner=False, ttl=300)
def fetch_google_bytes(
    google_sheet_url: str, refresh_token: int
) -> tuple[bytes, str]:
    _ = refresh_token
    content = download_google_sheet(google_sheet_url)
    synced_at = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return content, synced_at


def percent(value: float | None) -> str:
    return "—" if value is None or pd.isna(value) else f"{value:.1%}"


def format_axis(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=28, r=24, t=55, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, Microsoft YaHei, sans-serif", color=INK),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", font_color=INK),
    )
    fig.update_xaxes(gridcolor="#E9EFEB", zeroline=False)
    fig.update_yaxes(gridcolor="#E9EFEB", zeroline=False)
    return fig


def empty_chart(message: str) -> None:
    st.info(message, icon="ℹ️")


def role_key(job: object) -> str:
    value = str(job)
    lower_value = value.lower()
    for key in ROLE_STYLE:
        if key.lower() in lower_value:
            return key
    return value


def role_info(job: object) -> dict[str, str]:
    key = role_key(job)
    return ROLE_STYLE.get(
        key,
        {"zh": "职位", "en": "Role", "color": DECATHLON_DARK_BLUE},
    )


def job_legend_label(job: object) -> str:
    key = role_key(job)
    info = role_info(job)
    return info["zh"] if IS_ZH else info["en"]


def job_plain_label(job: object) -> str:
    key = role_key(job)
    info = role_info(job)
    if key in ROLE_STYLE:
        return info["zh"] if IS_ZH else info["en"]
    return str(job)


def job_color(job: object) -> str:
    return role_info(job)["color"]


def job_color_map(jobs: pd.Series | list[object]) -> dict[str, str]:
    return {job_legend_label(job): job_color(job) for job in pd.Series(jobs).dropna().unique()}


def format_kpi_value(value: float, metric_type: str) -> str:
    if pd.isna(value):
        return "—"
    if metric_type == "rate":
        return f"{value:.1%}"
    return f"{value:g}"


def build_raw_monthly_table(data: pd.DataFrame) -> pd.DataFrame:
    column_names = {
        "Job": tr("职位", "Role"),
        "Name": tr("员工", "Employee"),
        "KPI": tr("二级KPI", "KPI"),
        "KPIGroup": tr("KPI分类", "KPI Category"),
        "MetricType": tr("数据类型", "Data Type"),
    }
    month_columns = sorted(data["Month"].drop_duplicates())
    display_source = data.copy()
    display_source["DisplayValue"] = display_source.apply(
        lambda row: (
            row["Reason"]
            if row["MetricType"] == "reason"
            else format_kpi_value(row["Value"], row["MetricType"])
        ),
        axis=1,
    )
    table = (
        display_source.pivot_table(
            index=["Job", "Name", "KPI", "KPIGroup", "MetricType"],
            columns="Month",
            values="DisplayValue",
            aggfunc="first",
        )
        .reset_index()
        .sort_values(["Name", "KPI"])
        .reset_index(drop=True)
    )
    table = table.rename(
        columns={
            **column_names,
            **{month: month.strftime("%Y/%m") for month in month_columns},
        }
    )
    metric_type_column = column_names["MetricType"]
    job_column = column_names["Job"]
    kpi_column = column_names["KPI"]
    group_column = column_names["KPIGroup"]
    table[metric_type_column] = table[metric_type_column].map(
        {
            "rate": tr("比率", "Rate"),
            "count": tr("次数", "Count"),
            "duration": tr("周期", "Duration"),
            "reason": tr("原因", "Reason"),
        }
    ).fillna(table[metric_type_column])
    table[job_column] = table[job_column].map(job_plain_label)
    table[kpi_column] = table[kpi_column].map(display_kpi)
    table[group_column] = table[group_column].map(display_kpi_group)
    return table


def build_reason_table(data: pd.DataFrame) -> pd.DataFrame:
    reasons = data[
        data["MetricType"].eq("reason") & data["Reason"].ne("")
    ][["Month", "Job", "Name", "Reason"]].copy()
    if reasons.empty:
        return pd.DataFrame()

    counts = (
        data[data["MetricType"].eq("count")]
        .groupby(["Month", "Job", "Name"], as_index=False)
        .agg(Count=("Value", "sum"))
    )
    reasons = reasons.merge(counts, on=["Month", "Job", "Name"], how="left")
    reasons["Month"] = reasons["Month"].dt.strftime("%Y/%m")
    reasons["Count"] = reasons["Count"].fillna(0).map(lambda value: f"{value:g}")
    display = reasons.rename(
        columns={
            "Month": "月份",
            "Job": "职位",
            "Name": "员工",
            "Count": "未准时次数",
            "Reason": "未准时提交原因",
        }
    )[["月份", "职位", "员工", "未准时次数", "未准时提交原因"]]
    display["职位"] = display["职位"].map(job_plain_label)
    return (
        display.sort_values(["月份", "职位", "员工"], ascending=[False, True, True])
        .reset_index(drop=True)
    )


def build_attention_table(latest: pd.DataFrame) -> pd.DataFrame:
    attention = latest[latest["Target"].notna()].copy()
    attention = attention[
        (
            attention["MetricType"].eq("count")
            & attention["Value"].gt(attention["Target"])
        )
        | (
            ~attention["MetricType"].eq("count")
            & attention["Value"].lt(attention["Target"])
        )
    ].copy()
    if attention.empty:
        return pd.DataFrame()

    attention["Severity"] = attention.apply(
        lambda row: (
            row["Value"] - row["Target"]
            if row["MetricType"] == "count"
            else row["Target"] - row["Value"]
        ),
        axis=1,
    )
    attention["实际值"] = attention.apply(
        lambda row: format_kpi_value(row["Value"], row["MetricType"]), axis=1
    )
    attention["目标值"] = attention.apply(
        lambda row: format_kpi_value(row["Target"], row["MetricType"]), axis=1
    )
    attention["差距"] = attention.apply(
        lambda row: (
            f"超出 {row['Severity']:g} 次"
            if row["MetricType"] == "count"
            else f"低于目标 {row['Severity']:.1%}"
        ),
        axis=1,
    )
    attention["建议动作"] = attention["KPIGroup"].map(
        {
            "异常次数": "核对逾期原因、责任人和补救日期",
            "RFT": "复盘首轮失败原因并完善交付前检查清单",
            "准时交付": "检查排期、前置依赖和交付节点",
        }
    ).fillna("确认未达标原因并制定改善措施")
    reason_lookup = (
        latest[
            latest["MetricType"].eq("reason") & latest["Reason"].ne("")
        ]
        .groupby(["Job", "Name"])["Reason"]
        .agg("；".join)
        .to_dict()
    )
    attention["未准时提交原因"] = attention.apply(
        lambda row: (
            reason_lookup.get((row["Job"], row["Name"]), "未填写")
            if row["MetricType"] == "count"
            else "—"
        ),
        axis=1,
    )
    display = (
        attention.sort_values("Severity", ascending=False)
        .rename(columns={"Job": "职位", "Name": "员工", "KPI": "二级KPI"})
        [
            [
                "职位",
                "员工",
                "二级KPI",
                "实际值",
                "目标值",
                "差距",
                "未准时提交原因",
                "建议动作",
            ]
        ]
        .reset_index(drop=True)
    )
    display["职位"] = display["职位"].map(job_plain_label)
    return display


def render_rate_module(
    module_data: pd.DataFrame,
    title: str,
    latest_month: pd.Timestamp,
    period_label: str,
    period_month_labels: list[str],
) -> None:
    """Render one job-specific KPI module without mixing unrelated roles."""
    module_data = module_data[
        module_data["MetricType"].eq("rate")
    ].copy()
    if module_data.empty:
        st.markdown(
            f"""
            <div class="module-summary">
              <div>
                <div class="module-summary-label">{tr("统计周期", "Selected Period")}</div>
                <div>{period_label}</div>
              </div>
              <div style="text-align:right">
                <div class="module-summary-label">{tr("期间平均", "Period Average")}</div>
                <div class="module-summary-value">—</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        empty_chart(
            tr(
                f"当前筛选范围没有“{title}”数据。",
                f'No data is available for "{title}" in the selected range.',
            )
        )
        return

    period_value = float(module_data["Value"].mean())
    targets = sorted(module_data["Target"].dropna().unique())

    st.markdown(
        f"""
        <div class="module-summary">
          <div>
            <div class="module-summary-label">{tr("统计周期", "Selected Period")}</div>
            <div>{period_label}</div>
          </div>
          <div style="text-align:right">
            <div class="module-summary-label">{tr("期间平均", "Period Average")}</div>
            <div class="module-summary-value">{percent(period_value)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    module_data["MonthLabel"] = module_data["Month"].dt.strftime("%Y/%m")
    module_data["JobPlain"] = module_data["Job"].map(job_plain_label)
    module_data["DisplayKPI"] = module_data["KPI"].map(display_kpi)
    module_data["Series"] = module_data.apply(
        lambda row: f"{row['DisplayKPI']} · {row['Name']}", axis=1
    )
    fig = px.line(
        module_data,
        x="MonthLabel",
        y="Value",
        color="Series",
        markers=True,
        custom_data=["JobPlain", "Name", "DisplayKPI", "Target"],
        color_discrete_sequence=px.colors.qualitative.Safe,
        title=f"{title} · {period_label}",
        labels={
            "Value": tr("达成率", "Achievement Rate"),
            "MonthLabel": tr("月份", "Month"),
            "Series": tr("KPI / 员工", "KPI / Employee"),
        },
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate=(
            "<b>KPI：%{customdata[2]}</b><br>"
            f"{tr('职位', 'Role')}：%{{customdata[0]}}<br>"
            f"{tr('员工', 'Employee')}：%{{customdata[1]}}<br>"
            f"{tr('月份', 'Month')}：%{{x}}<br>"
            f"{tr('达成率', 'Achievement Rate')}：%{{y:.1%}}<br>"
            f"{tr('目标', 'Target')}：%{{customdata[3]:.0%}}<extra></extra>"
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=period_month_labels,
            y=[None] * len(period_month_labels),
            mode="lines",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    for target in targets:
        fig.add_hline(
            y=float(target),
            line_dash="dash",
            line_color=INK,
            opacity=0.55,
            annotation_text=f"{tr('目标', 'Target')} {target:.0%}",
            annotation_position="top left",
        )
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=period_month_labels,
    )
    max_value = float(module_data["Value"].max())
    fig.update_yaxes(
        tickformat=".0%",
        range=[0.5, max(1.04, max_value * 1.04)],
    )
    st.plotly_chart(
        format_axis(fig, 370),
        config={"displayModeBar": False},
    )


def render_employee_rate_modules(
    module_data: pd.DataFrame,
    title: str,
    latest_month: pd.Timestamp,
    period_label: str,
    period_month_labels: list[str],
    employee_names: list[str] | None = None,
) -> None:
    """Keep fixed employee panels so TP trends never share one chart."""
    rate_data = module_data[module_data["MetricType"].eq("rate")].copy()
    names = employee_names or sorted(rate_data["Name"].dropna().unique())
    if not names:
        render_rate_module(
            module_data,
            title,
            latest_month,
            period_label,
            period_month_labels,
        )
        return

    if len(names) <= 1:
        st.markdown(f"#### {names[0]}")
        render_rate_module(
            rate_data[rate_data["Name"].eq(names[0])],
            title,
            latest_month,
            period_label,
            period_month_labels,
        )
        return

    columns = st.columns(2)
    for index, name in enumerate(names):
        with columns[index % 2]:
            st.markdown(f"#### {name}")
            render_rate_module(
                rate_data[rate_data["Name"].eq(name)],
                title,
                latest_month,
                period_label,
                period_month_labels,
            )


with st.sidebar:
    st.markdown(f"## {tr('数据与筛选', 'Data & Filters')}")
    data_source = st.radio(
        tr("数据来源", "Data Source"),
        ["google", "upload", "builtin"],
        format_func=lambda value: {
            "google": tr("Google 表格自动同步", "Google Sheets Auto Sync"),
            "upload": tr("上传 Excel", "Upload Excel"),
            "builtin": tr("内置模板", "Built-in Template"),
        }[value],
    )

    uploaded = None
    if data_source == "google":
        st.caption(tr("每 5 分钟自动同步", "Auto-refresh every 5 minutes"))
        st.link_button(tr("打开 Google 表格", "Open Google Sheet"), GOOGLE_SHEET_URL, width="stretch")
        if "google_refresh_token" not in st.session_state:
            st.session_state["google_refresh_token"] = 0
        if st.button(tr("立即刷新", "Refresh Now"), width="stretch"):
            st.session_state["google_refresh_token"] += 1
            st.rerun()
    elif data_source == "upload":
        st.caption(tr("自动读取工作表2", "The app reads Sheet 2 automatically"))
        uploaded = st.file_uploader(tr("上传 KPI Excel", "Upload KPI Excel"), type=["xlsx", "xlsm"])
    else:
        st.caption(tr("使用项目内保存的 Excel 数据。", "Use the Excel file included with the app."))

    with SAMPLE_FILE.open("rb") as sample:
        st.download_button(
            tr("下载模板", "Download Template"),
            data=sample.read(),
            file_name="DCKPI Dashboard.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

try:
    if data_source == "google":
        file_bytes, synced_at = fetch_google_bytes(
            GOOGLE_SHEET_URL, st.session_state["google_refresh_token"]
        )
        source_label = tr("Google 表格", "Google Sheets")
    elif data_source == "upload":
        if uploaded is None:
            st.info(tr("请上传 Excel 文件。", "Please upload an Excel file."))
            st.stop()
        file_bytes = uploaded.getvalue()
        synced_at = datetime.now(ZoneInfo("Asia/Shanghai")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        source_label = tr("上传的 Excel", "Uploaded Excel")
    else:
        file_bytes = SAMPLE_FILE.read_bytes()
        synced_at = tr("项目内置文件", "Built-in file")
        source_label = tr("内置模板", "Built-in Template")

    data, source_info = load_bytes(file_bytes, DATA_SCHEMA_VERSION)
    source_info["source_label"] = source_label
    source_info["synced_at"] = synced_at
except Exception as exc:
    st.error(tr(f"数据读取失败：{exc}", f"Failed to load data: {exc}"))
    st.stop()

with st.sidebar:
    if data_source == "google":
        st.success(
            tr(
                f"Google 表格已连接\n\n最近同步：{source_info['synced_at']}",
                f"Google Sheets connected\n\nLast sync: {source_info['synced_at']}",
            )
        )
    else:
        st.info(tr("当前数据源：", "Current source: ") + str(source_info["source_label"]))

all_months = sorted(
    set(data["Month"].drop_duplicates().tolist())
    | set(source_info.get("reporting_months", []))
)
latest_available = max(all_months)
roster = pd.DataFrame(source_info.get("roster", []))
if roster.empty:
    roster = data[["Job", "Name"]].drop_duplicates().copy()

with st.sidebar:
    st.divider()
    st.markdown(f"### {tr('时间与团队', 'Period & Team')}")
    period_mode = st.radio(
        tr("统计周期", "Period"),
        ["last_12", "ytd", "custom"],
        format_func=lambda value: {
            "last_12": tr("最近12个月", "Last 12 Months"),
            "ytd": tr("本年累计", "Year to Date"),
            "custom": tr("自定义", "Custom"),
        }[value],
        horizontal=False,
    )

    if period_mode == "ytd":
        start_month = pd.Timestamp(latest_available.year, 1, 1)
        end_month = latest_available
    elif period_mode == "last_12":
        start_month = latest_available - pd.DateOffset(months=11)
        end_month = latest_available
    else:
        month_labels = [month.strftime("%Y/%m") for month in all_months]
        if len(month_labels) > 1:
            start_label, end_label = st.select_slider(
                tr("月份范围", "Month Range"),
                options=month_labels,
                value=(month_labels[0], month_labels[-1]),
            )
        else:
            start_label = end_label = month_labels[0]
            st.caption(f"{tr('月份', 'Month')}: {start_label}")
        start_month = pd.to_datetime(start_label, format="%Y/%m")
        end_month = pd.to_datetime(end_label, format="%Y/%m")

    st.caption(
        f"{tr('当前选择', 'Selected')}: "
        f"{start_month:%Y/%m}–{end_month:%Y/%m}"
    )

    preferred_job_order = ["Modelist", "ME", "IE", "Designer", "PIS"]
    job_options = sorted(
        roster["Job"].unique(),
        key=lambda job: (
            preferred_job_order.index(role_key(job))
            if role_key(job) in preferred_job_order
            else len(preferred_job_order),
            str(job),
        ),
    )
    selected_jobs = st.multiselect(
        tr("职位", "Role"),
        job_options,
        default=job_options,
        format_func=job_plain_label,
    )
    available_names = sorted(
        roster[roster["Job"].isin(selected_jobs)]["Name"].unique()
    )
    selected_names = st.multiselect(
        tr("员工", "Employee"), available_names, default=available_names
    )

filtered = data[
    data["Month"].between(start_month, end_month)
    & data["Job"].isin(selected_jobs)
    & data["Name"].isin(selected_names)
].copy()

if filtered.empty:
    st.warning(
        tr(
            "当前筛选没有数据，请调整月份、职位或员工。",
            "No data matches the current filters. Adjust the month, role, or employee.",
        )
    )
    st.stop()

latest_month = filtered["Month"].max()
period_start = pd.Timestamp(start_month).to_period("M").to_timestamp()
period_end = pd.Timestamp(end_month).to_period("M").to_timestamp()
period_label = (
    f"{period_start:%Y/%m}"
    if period_start == period_end
    else f"{period_start:%Y/%m}–{period_end:%Y/%m}"
)
period_month_labels = [
    month.strftime("%Y/%m")
    for month in pd.date_range(period_start, period_end, freq="MS")
]
previous_months = sorted(filtered.loc[filtered["Month"] < latest_month, "Month"].unique())
previous_month = previous_months[-1] if previous_months else None
latest_data = filtered[filtered["Month"].eq(latest_month)]
previous_data = (
    filtered[filtered["Month"].eq(previous_month)]
    if previous_month is not None
    else pd.DataFrame(columns=filtered.columns)
)

rate_latest = latest_data[latest_data["MetricType"].eq("rate")]
rft_latest = rate_latest[rate_latest["KPIGroup"].eq("RFT")]
ontime_latest = rate_latest[rate_latest["KPIGroup"].eq("准时交付")]
count_latest = latest_data[latest_data["MetricType"].eq("count")]

target_rows = latest_data[latest_data["Target"].notna()]
target_achievement = (
    float(target_rows["TargetMet"].astype(float).mean()) if not target_rows.empty else None
)
rft_value = float(rft_latest["Value"].mean()) if not rft_latest.empty else None
ontime_value = float(ontime_latest["Value"].mean()) if not ontime_latest.empty else None
overdue_value = float(count_latest["Value"].sum()) if not count_latest.empty else 0.0

previous_rft = previous_data[
    previous_data["MetricType"].eq("rate") & previous_data["KPIGroup"].eq("RFT")
]["Value"].mean()
rft_delta = (
    f"{rft_value - previous_rft:+.1%}"
    if rft_value is not None and pd.notna(previous_rft)
    else None
)

role_counts = (
    roster[
        roster["Job"].isin(selected_jobs) & roster["Name"].isin(selected_names)
    ][["Job", "Name"]]
    .drop_duplicates()
    .groupby("Job")["Name"]
    .nunique()
    .to_dict()
)
role_order = ["Modelist", "ME", "IE", "Designer", "PIS"]
role_summary_parts = []
for role in role_order:
    count = sum(
        value for job, value in role_counts.items() if role_key(job) == role
    )
    if count:
        role_name = role_info(role)["zh" if IS_ZH else "en"]
        role_summary_parts.append(
            '<span class="role-chip">'
            f'<span class="role-dot" style="background:{job_color(role)}"></span>'
            f"{role_name} {count}{tr('人', '')}</span>"
        )
for job, count in role_counts.items():
    if role_key(job) not in role_order:
        role_summary_parts.append(
            '<span class="role-chip">'
            f'<span class="role-dot" style="background:{job_color(job)}"></span>'
            f"{job_plain_label(job)} {count}{tr('人', '')}</span>"
        )
role_summary = "".join(role_summary_parts)

st.markdown(
    f"""
      <div class="hero-panel">
      <div class="dashboard-title">ZX DC KPI Dashboard</div>
      <div class="dashboard-subtitle">{tr(f'开发中心绩效监控 · 数据截止 {latest_month:%Y年%m月}', f'Development Center Performance · Data through {latest_month:%Y/%m}')}<br>
      <span class="team-structure">{tr('团队人员', 'Team')}：{role_summary}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        tr("KPI 看板", "KPI Dashboard"),
        tr("绩效明细", "Performance Detail"),
    ]
)

with tabs[0]:
    modelist_names = sorted(
        roster[
            roster["Job"].map(role_key).eq("Modelist")
            & roster["Name"].isin(selected_names)
        ]["Name"].unique()
    )
    module_options = [
        "TP RFT",
        "TP ON TIME",
        "MARKER RFT",
        "MARKER ON TIME",
        "SOT RFT",
        "SOT ON TIME",
        "3D RFT",
        "SSS RFT",
        "SSS ON TIME",
        "PPS RFT",
        "PPS ON TIME",
    ]

    def module_data_for(module_name: str) -> pd.DataFrame:
        role = filtered["Job"].map(role_key)
        if module_name == "3D RFT":
            return filtered[
                role.eq("Designer")
                & filtered["KPI"].str.contains("3D", case=False, na=False)
            ]
        if module_name == "TP RFT":
            return filtered[role.eq("Modelist") & filtered["KPIGroup"].eq("RFT")]
        if module_name == "TP ON TIME":
            rate_rows = filtered[
                role.eq("Modelist")
                & filtered["KPIGroup"].eq("准时交付")
                & filtered["KPI"].str.contains("TP", case=False, na=False)
            ]
            if not rate_rows.empty:
                return rate_rows
            return filtered[role.eq("Modelist") & filtered["MetricType"].eq("count")]
        if module_name in {"SSS RFT", "SSS ON TIME"}:
            kpi_group = "RFT" if module_name.endswith("RFT") else "准时交付"
            return filtered[
                role.eq("PIS")
                & filtered["KPI"].str.contains("SSS|样品", case=False, regex=True, na=False)
                & filtered["KPIGroup"].eq(kpi_group)
            ]
        if module_name in {"PPS RFT", "PPS ON TIME"}:
            kpi_group = "RFT" if module_name.endswith("RFT") else "准时交付"
            return filtered[
                role.eq("PIS")
                & filtered["KPI"].str.contains("PPS", case=False, na=False)
                & filtered["KPIGroup"].eq(kpi_group)
            ]
        family = "MARKER" if module_name.startswith("MARKER") else "SOT"
        kpi_group = "RFT" if module_name.endswith("RFT") else "准时交付"
        return filtered[
            role.eq("ME")
            & filtered["KPI"].str.contains(family, case=False, na=False)
            & filtered["KPIGroup"].eq(kpi_group)
        ]

    module_labels = {
        "3D RFT": tr("3D 一次通过率", "3D RFT"),
        "TP RFT": tr("TP 一次通过率", "TP RFT"),
        "TP ON TIME": tr("TP 准时交付", "TP ON TIME"),
        "SSS RFT": tr("SSS 一次通过率", "SSS RFT"),
        "SSS ON TIME": tr("SSS 准时交付", "SSS ON TIME"),
        "PPS RFT": tr("PPS 一次通过率", "PPS RFT"),
        "PPS ON TIME": tr("PPS 准时交付", "PPS ON TIME"),
        "MARKER RFT": tr("MARKER 一次通过率", "MARKER RFT"),
        "MARKER ON TIME": tr("MARKER 准时交付", "MARKER ON TIME"),
        "SOT RFT": tr("SOT 一次通过率", "SOT RFT"),
        "SOT ON TIME": tr("SOT 准时交付", "SOT ON TIME"),
    }
    module_button_labels = {}
    for option in module_options:
        option_data = module_data_for(option)
        rate_values = option_data.loc[option_data["MetricType"].eq("rate"), "Value"]
        count_values = option_data.loc[option_data["MetricType"].eq("count"), "Value"]
        if not rate_values.empty:
            summary_value = percent(float(rate_values.mean()))
        elif not count_values.empty:
            count_rows = option_data.loc[
                option_data["MetricType"].eq("count") & option_data["Target"].notna()
            ]
            summary_value = percent(
                float(count_rows["Value"].le(count_rows["Target"]).mean())
            )
        else:
            summary_value = "—"
        module_button_labels[option] = f"{module_labels[option]}\n{summary_value}"
    if st.session_state.get("selected_kpi_module") not in module_options:
        st.session_state["selected_kpi_module"] = module_options[0]
    selected_module = st.pills(
        tr("选择 KPI 模块", "Select KPI Module"),
        module_options,
        format_func=lambda value: module_button_labels[value],
        selection_mode="single",
        key="selected_kpi_module",
    ) or module_options[0]
    selected_module_data = module_data_for(selected_module)

    if selected_module == "3D RFT":
        module_data = filtered[
            filtered["Job"].map(role_key).eq("Designer")
            & filtered["KPI"].str.contains("3D", case=False, na=False)
        ]
        render_rate_module(
            module_data,
            module_labels[selected_module],
            latest_month,
            period_label,
            period_month_labels,
        )
    elif selected_module == "TP RFT":
        module_data = selected_module_data
        render_employee_rate_modules(
            module_data,
            module_labels[selected_module],
            latest_month,
            period_label,
            period_month_labels,
            modelist_names,
        )
    elif (
        selected_module == "TP ON TIME"
        and not selected_module_data.loc[
            selected_module_data["MetricType"].eq("rate")
        ].empty
    ):
        module_data = selected_module_data
        render_employee_rate_modules(
            module_data,
            module_labels[selected_module],
            latest_month,
            period_label,
            period_month_labels,
            modelist_names,
        )
    elif selected_module in {"PPS RFT", "PPS ON TIME"}:
        module_data = selected_module_data
        render_rate_module(
            module_data,
            module_labels[selected_module],
            latest_month,
            period_label,
            period_month_labels,
        )
    elif selected_module in {"SSS RFT", "SSS ON TIME"}:
        module_data = selected_module_data
        render_rate_module(
            module_data,
            module_labels[selected_module],
            latest_month,
            period_label,
            period_month_labels,
        )
    elif selected_module in {"MARKER RFT", "MARKER ON TIME", "SOT RFT", "SOT ON TIME"}:
        family = "MARKER" if selected_module.startswith("MARKER") else "SOT"
        kpi_group = "RFT" if selected_module.endswith("RFT") else "准时交付"
        module_data = filtered[
            filtered["Job"].map(role_key).eq("ME")
            & filtered["KPI"].str.contains(family, case=False, na=False)
            & filtered["KPIGroup"].eq(kpi_group)
        ]
        render_rate_module(
            module_data,
            module_labels[selected_module],
            latest_month,
            period_label,
            period_month_labels,
        )
    elif selected_module == "__unused_overall_attainment__":
        employee_source = filtered[
            filtered["MetricType"].eq("rate") & filtered["Target"].notna()
        ]
        if employee_source.empty:
            empty_chart("当前范围没有带目标值的比率类 KPI。")
        else:
            employee = (
                employee_source
                .assign(
                    Attainment=lambda frame: (
                        frame["Value"] / frame["Target"].replace(0, pd.NA)
                    ).clip(upper=1.0)
                )
                .groupby(["Job", "Name"], as_index=False)
                .agg(
                    Attainment=("Attainment", "mean"),
                    AverageRate=("Value", "mean"),
                    Months=("Month", "nunique"),
                )
                .sort_values("Attainment")
            )
            employee["Status"] = employee["Attainment"].ge(1).map(
                {True: "达标", False: "需关注"}
            )
            employee["JobLabel"] = employee["Job"].map(job_legend_label)
            employee["JobPlain"] = employee["Job"].map(job_plain_label)
            st.caption("目标达成指数最高显示为 100%；超额完成不再拉高综合指数。")
            fig_employee = px.bar(
                employee,
                x="Attainment",
                y="Name",
                color="JobLabel",
                orientation="h",
                text=employee["Attainment"].map(lambda value: f"{value:.0%}"),
                custom_data=["JobPlain", "Months", "AverageRate", "Status"],
                color_discrete_map=job_color_map(employee["Job"]),
                title=f"个人目标达成指数 · {period_label}",
                labels={
                    "Attainment": "目标达成指数",
                    "Name": "员工",
                    "JobLabel": "职位",
                },
            )
            fig_employee.update_traces(
                hovertemplate=(
                    "<b>员工：%{y}</b><br>"
                    "职位：%{customdata[0]}<br>"
                    "有数据月份：%{customdata[1]}<br>"
                    "期间平均达成率：%{customdata[2]:.1%}<br>"
                    "目标达成指数（封顶）：%{x:.1%}<br>"
                    "状态：%{customdata[3]}<extra></extra>"
                ),
                textposition="inside",
                insidetextanchor="middle",
                cliponaxis=False,
                textfont=dict(color="white", size=12),
            )
            fig_employee.add_vline(
                x=1,
                line_dash="dash",
                line_color=INK,
                annotation_text="目标线 100%",
                annotation_position="top",
            )
            fig_employee.update_xaxes(tickformat=".0%", range=[0, 1.08])
            st.plotly_chart(
                format_axis(fig_employee, 430),
                config={"displayModeBar": False},
            )
    else:
        st.caption(
            tr(
                "方框达标率 = 每人每月未准时提交次数 ≤ 2 的记录数 ÷ 全部有记录月份；下方图表展示实际次数及原因。",
                "Card compliance rate = employee-month records with ≤2 late submissions ÷ all recorded employee-months; the chart shows actual counts and reasons.",
            )
        )
        exception = filtered[
            filtered["MetricType"].eq("count")
            & filtered["Job"].map(role_key).eq("Modelist")
        ]
        if exception.empty:
            empty_chart(tr("当前范围没有 TP 准时提交数据。", "No TP on-time data is available for this period."))
        else:
            exception_monthly = (
                exception.groupby(["Month", "Job", "Name"], as_index=False)
                .agg(Value=("Value", "sum"))
                .sort_values("Month")
            )
            reason_monthly = (
                filtered[
                    filtered["MetricType"].eq("reason")
                    & filtered["Reason"].ne("")
                ]
                .groupby(["Month", "Job", "Name"], as_index=False)
                .agg(Reason=("Reason", "；".join))
            )
            exception_monthly = exception_monthly.merge(
                reason_monthly, on=["Month", "Job", "Name"], how="left"
            )
            exception_monthly["MonthLabel"] = exception_monthly[
                "Month"
            ].dt.strftime("%Y/%m")
            exception_monthly["Reason"] = exception_monthly["Reason"].fillna(
                tr("未填写", "Not provided")
            )
            exception_monthly["JobPlain"] = exception_monthly["Job"].map(
                job_plain_label
            )
            name_color_map = (
                exception_monthly.drop_duplicates("Name")
                .set_index("Name")["Job"]
                .map(job_color)
                .to_dict()
            )
            fig_exception = px.line(
                exception_monthly,
                x="MonthLabel",
                y="Value",
                color="Name",
                line_dash="Name",
                symbol="Name",
                markers=True,
                custom_data=["JobPlain", "Reason"],
                color_discrete_map=name_color_map,
                title=tr(
                    "TP 准时提交 · 未准时提交次数趋势（目标：每人每月 ≤ 2 次）",
                    "TP on time · Late Submission Trend (Target: ≤ 2 per employee/month)",
                ),
                labels={
                    "Value": tr("次数", "Count"),
                    "MonthLabel": tr("月份", "Month"),
                    "Name": tr("员工", "Employee"),
                },
            )
            fig_exception.update_traces(
                line=dict(width=3),
                marker=dict(size=9),
                hovertemplate=(
                    f"<b>{tr('员工', 'Employee')}：%{{fullData.name}}</b><br>"
                    f"{tr('职位', 'Role')}：%{{customdata[0]}}<br>"
                    f"{tr('月份', 'Month')}：%{{x}}<br>"
                    f"{tr('未准时提交次数', 'Late Submissions')}：%{{y:.0f}}<br>"
                    f"{tr('原因', 'Reason')}：%{{customdata[1]}}<extra></extra>"
                ),
            )
            fig_exception.add_trace(
                go.Scatter(
                    x=period_month_labels,
                    y=[None] * len(period_month_labels),
                    mode="lines",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig_exception.add_hline(
                y=2,
                line_dash="dash",
                line_color=RED,
                annotation_text=tr("目标红线：≤2次/月", "Target: ≤2/month"),
                annotation_position="top left",
            )
            fig_exception.update_xaxes(
                type="category",
                categoryorder="array",
                categoryarray=period_month_labels,
            )
            fig_exception.update_yaxes(
                dtick=1,
                range=[0, max(3, float(exception_monthly["Value"].max()) + 0.8)],
            )
            st.plotly_chart(
                format_axis(fig_exception, 430),
                config={"displayModeBar": False},
            )

if False:
    employee_source = filtered[
        filtered["MetricType"].eq("rate") & filtered["Target"].notna()
    ]
    if employee_source.empty:
        empty_chart("当前范围没有带目标值的比率类 KPI。")
    else:
        employee = (
            employee_source
            .assign(
                Attainment=lambda frame: (
                    frame["Value"] / frame["Target"].replace(0, pd.NA)
                ).clip(upper=1.0)
            )
            .groupby(["Job", "Name"], as_index=False)
            .agg(
                Attainment=("Attainment", "mean"),
                AverageRate=("Value", "mean"),
                Months=("Month", "nunique"),
            )
            .sort_values("Attainment")
        )
        employee["Status"] = employee["Attainment"].ge(1).map(
            {True: "达标", False: "需关注"}
        )
        employee["JobLabel"] = employee["Job"].map(job_legend_label)
        employee["JobPlain"] = employee["Job"].map(job_plain_label)
        attainment_range_max = 1.08
        st.caption("目标达成指数最高显示为 100%；超额完成不再拉高综合指数。")
        fig_employee = px.bar(
            employee,
            x="Attainment",
            y="Name",
            color="JobLabel",
            orientation="h",
            text=employee["Attainment"].map(lambda value: f"{value:.0%}"),
            custom_data=["JobPlain", "Months", "AverageRate", "Status"],
            color_discrete_map=job_color_map(employee["Job"]),
            title=f"个人目标达成指数 · {period_label}",
            labels={
                "Attainment": "目标达成指数",
                "Name": "员工",
                "JobLabel": "职位",
                "Months": "有数据月份",
                "AverageRate": "期间平均达成率",
                "Status": "状态",
            },
        )
        fig_employee.update_traces(
            hovertemplate=(
                "<b>员工：%{y}</b><br>"
                "职位：%{customdata[0]}<br>"
                "有数据月份：%{customdata[1]}<br>"
                "期间平均达成率：%{customdata[2]:.1%}<br>"
                "目标达成指数（封顶）：%{x:.1%}<br>"
                "状态：%{customdata[3]}<extra></extra>"
            )
        )
        fig_employee.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            cliponaxis=False,
            textfont=dict(color="white", size=12),
        )
        fig_employee.add_vline(
            x=1,
            line_dash="dash",
            line_color=INK,
            annotation_text="目标线 100%",
            annotation_position="top",
        )
        fig_employee.update_xaxes(tickformat=".0%", range=[0, attainment_range_max])
        st.plotly_chart(
            format_axis(fig_employee, 430),
            config={"displayModeBar": False},
        )

    st.markdown("### RFT 趋势")
    exception = filtered[filtered["MetricType"].eq("count")]
    if not exception.empty:
        exception_monthly = (
            exception.groupby(["Month", "Job", "Name"], as_index=False)
            .agg(Value=("Value", "sum"))
            .sort_values("Month")
        )
        reason_monthly = (
            filtered[
                filtered["MetricType"].eq("reason") & filtered["Reason"].ne("")
            ]
            .groupby(["Month", "Job", "Name"], as_index=False)
            .agg(Reason=("Reason", "；".join))
        )
        exception_monthly = exception_monthly.merge(
            reason_monthly, on=["Month", "Job", "Name"], how="left"
        )
        exception_monthly["MonthLabel"] = exception_monthly["Month"].dt.strftime(
            "%Y/%m"
        )
        exception_monthly["Reason"] = exception_monthly["Reason"].fillna("未填写")
        exception_monthly["JobPlain"] = exception_monthly["Job"].map(job_plain_label)
        name_color_map = (
            exception_monthly.drop_duplicates("Name")
            .set_index("Name")["Job"]
            .map(job_color)
            .to_dict()
        )
        fig_exception = px.line(
            exception_monthly,
            x="MonthLabel",
            y="Value",
            color="Name",
            line_dash="Name",
            symbol="Name",
            markers=True,
            custom_data=["JobPlain", "Reason"],
            color_discrete_map=name_color_map,
            title="RFT 未准时提交次数趋势（目标：每人每月 ≤ 2 次）",
            labels={"Value": "次数", "MonthLabel": "月份", "Name": "员工"},
        )
        fig_exception.update_traces(
            line=dict(width=3),
            marker=dict(size=9),
            hovertemplate=(
                "<b>员工：%{fullData.name}</b><br>"
                "职位：%{customdata[0]}<br>"
                "月份：%{x}<br>"
                "未准时提交：%{y:.0f} 次<br>"
                "原因：%{customdata[1]}<extra></extra>"
            )
        )
        fig_exception.add_hline(
            y=2,
            line_dash="dash",
            line_color=RED,
            annotation_text="目标红线：≤2次/月",
            annotation_position="top left",
        )
        fig_exception.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=period_month_labels,
        )
        fig_exception.update_yaxes(
            dtick=1,
            rangemode="tozero",
            range=[0, max(3, float(exception_monthly["Value"].max()) + 0.8)],
        )
        st.plotly_chart(
            format_axis(fig_exception, 350),
            config={"displayModeBar": False},
        )
    else:
        empty_chart("当前范围没有“次数”类异常指标。")

    st.markdown(f"### 最新需关注清单 · {latest_month:%Y/%m}")
    attention_table = build_attention_table(latest_data)
    if attention_table.empty:
        st.success("最新月份所有有目标的 KPI 均已达标。", icon="✅")
    else:
        st.caption("自动汇总低于目标的比率 KPI，以及大于目标值的次数类 KPI。")
        st.dataframe(
            attention_table,
            width="stretch",
            hide_index=True,
            height=min(420, 38 * (len(attention_table) + 1)),
        )

if False:
    modelist_col, designer_col = st.columns([1.25, 0.75])

    with modelist_col:
        st.markdown("### Modelist（版师）：TP Qualification")
        modelist = latest_data[
            latest_data["Job"].str.contains("Modelist", case=False, na=False)
            & latest_data["MetricType"].eq("rate")
        ]
        modelist_pivot = modelist.pivot_table(
            index="Name", columns="KPI", values="Value", aggfunc="mean"
        )

        def find_column(keyword: str) -> str | None:
            return next(
                (column for column in modelist_pivot.columns if keyword in column.upper()),
                None,
            )

        pap_col = find_column("PAP")
        tf_col = find_column("TF")
        bom_col = find_column("BOM")
        if pap_col and tf_col and bom_col and not modelist_pivot.empty:
            bubble = modelist_pivot[[pap_col, tf_col, bom_col]].dropna().reset_index()
            fig_bubble = go.Figure()
            fig_bubble.add_trace(
                go.Scatter(
                    x=bubble[tf_col] * 100,
                    y=bubble[pap_col] * 100,
                    mode="markers+text",
                    text=bubble["Name"],
                    textposition="top center",
                    marker=dict(
                        size=(bubble[bom_col].clip(lower=0) * 38 + 18),
                        color=bubble[bom_col] * 100,
                        colorscale=[
                            [0, RED],
                            [0.65, YELLOW],
                            [0.95, GREEN],
                            [1, DARK_GREEN],
                        ],
                        cmin=50,
                        cmax=100,
                        showscale=True,
                        colorbar=dict(title="BOM<br>通过率"),
                        line=dict(width=2, color="white"),
                    ),
                    customdata=bubble[[bom_col]].to_numpy(),
                    hovertemplate=(
                        "<b>员工：%{text}</b><br>"
                        "TF 一次通过率：%{x:.1f}%<br>"
                        "PAP 一次通过率：%{y:.1f}%<br>"
                        "BOM 一次通过率：%{customdata[0]:.1%}<extra></extra>"
                    ),
                )
            )
            fig_bubble.update_layout(
                title=f"PAP × TF × BOM · {latest_month:%Y/%m}",
                xaxis_title="TF 一次通过率",
                yaxis_title="PAP 一次通过率",
            )
            fig_bubble.update_xaxes(range=[50, 102], ticksuffix="%")
            fig_bubble.update_yaxes(range=[50, 102], ticksuffix="%")
            st.plotly_chart(
                format_axis(fig_bubble, 470),
                config={"displayModeBar": False},
            )
        else:
            empty_chart("需要同时存在 PAP、TF、BOM 三项数据才能生成 Modelist 气泡图。")

    with designer_col:
        st.markdown("### Designer（设计）：3D 品质")
        designer = latest_data[
            latest_data["Job"].str.contains("Designer", case=False, na=False)
            & latest_data["MetricType"].eq("rate")
        ]
        if not designer.empty:
            pass_rate = float(designer["Value"].mean())
            pass_rate = min(max(pass_rate, 0), 1)
            fig_donut = go.Figure(
                go.Pie(
                    labels=["合格", "不合格"],
                    values=[pass_rate, 1 - pass_rate],
                    hole=0.55,
                    marker_colors=[GREEN, YELLOW],
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>占比：%{percent}<extra></extra>",
                    sort=False,
                    direction="clockwise",
                )
            )
            fig_donut.update_layout(
                title=f"3D 交付准确率 · {latest_month:%Y/%m}",
                showlegend=False,
                annotations=[
                    dict(
                        text=f"{pass_rate:.0%}",
                        x=0.5,
                        y=0.5,
                        font_size=28,
                        showarrow=False,
                    )
                ],
            )
            st.plotly_chart(
                format_axis(fig_donut, 470),
                config={"displayModeBar": False},
            )
        else:
            empty_chart("当前范围没有 Designer 的比率数据。")

    st.markdown("### PIS（产品导入）与 IE（工程）月度明细")
    focus = filtered[
        filtered["Job"].str.contains("PIS|IE", case=False, regex=True, na=False)
        & filtered["MetricType"].eq("rate")
    ]
    if not focus.empty:
        focus = focus.copy()
        focus["MonthLabel"] = focus["Month"].dt.strftime("%Y/%m")
        focus["JobLabel"] = focus["Job"].map(job_legend_label)
        focus["JobPlain"] = focus["Job"].map(job_plain_label)
        fig_focus = px.line(
            focus,
            x="MonthLabel",
            y="Value",
            color="KPI",
            facet_row="JobLabel",
            markers=True,
            custom_data=["JobPlain"],
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="PIS / IE KPI 趋势",
            labels={
                "Value": "达成率",
                "MonthLabel": "月份",
                "KPI": "二级KPI",
                "JobLabel": "职位",
            },
        )
        fig_focus.update_traces(
            hovertemplate=(
                "<b>KPI：%{fullData.name}</b><br>"
                "职位：%{customdata[0]}<br>"
                "月份：%{x}<br>"
                "达成率：%{y:.1%}<extra></extra>"
            )
        )
        fig_focus.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=period_month_labels,
        )
        fig_focus.update_yaxes(tickformat=".0%", range=[0, 1.08])
        fig_focus.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split("=")[-1]))
        st.plotly_chart(
            format_axis(fig_focus, 520),
            config={"displayModeBar": False},
        )

    lead_time = filtered[filtered["KPIGroup"].eq("L/T")]
    if lead_time.empty:
        st.warning(
            "L/T（Lead Time / 周期）暂未显示：当前工作表2没有周期或时长类 KPI。"
            "后续增加名称含“L/T、Lead Time、周期、时长或天数”的行后，系统会自动识别。",
            icon="⏱️",
        )

with tabs[1]:
    st.markdown(f"### {tr('月度绩效明细', 'Monthly Performance Data')} · {period_label}")
    st.caption(
        tr(
            "每个 KPI 独立成行，比率、次数和未准时提交原因不会混在一起。",
            "Each KPI stays on a separate row so rates, counts, and late-submission reasons remain clear.",
        )
    )
    raw_monthly = build_raw_monthly_table(filtered)
    st.dataframe(
        raw_monthly,
        width="stretch",
        hide_index=True,
        height=min(620, 38 * (len(raw_monthly) + 1)),
    )
    st.download_button(
        tr("下载筛选数据", "Download Filtered Data"),
        data=raw_monthly.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"ZX_KPI_data_{period_start:%Y%m}_{period_end:%Y%m}.csv",
        mime="text/csv",
    )

    st.markdown(f"### {tr('最新月份与期间表现', 'Latest & Period Performance')}")
    detail = period_detail(filtered)
    display = detail.copy()
    if not display.empty:
        if not IS_ZH:
            display["Status"] = display["Status"].replace(
                {"达标": "On Target", "需关注": "Needs Attention"}
            )
        for column in ("Latest", "PeriodAverage", "Target"):
            display[column] = display.apply(
                lambda row: (
                    f"{row[column]:g}"
                    if row.get("MetricType") in ("count", "duration")
                    and pd.notna(row[column])
                    else f"{row[column]:.1%}"
                    if pd.notna(row[column])
                    else "—"
                ),
                axis=1,
            )
        detail_columns = {
            "Job": tr("职位", "Role"),
            "Name": tr("员工", "Employee"),
            "KPI": tr("二级KPI", "KPI"),
            "KPIGroup": tr("分类", "Category"),
            "Latest": f"{latest_month:%Y/%m}",
            "PeriodAverage": tr("期间平均", "Period Average"),
            "Target": tr("目标", "Target"),
            "Months": tr("有数据月份", "Months with Data"),
            "Status": tr("状态", "Status"),
        }
        display = display.rename(columns=detail_columns)
        display = display[
            [
                detail_columns["Job"],
                detail_columns["Name"],
                detail_columns["KPI"],
                detail_columns["KPIGroup"],
                f"{latest_month:%Y/%m}",
                detail_columns["PeriodAverage"],
                detail_columns["Target"],
                detail_columns["Status"],
                detail_columns["Months"],
            ]
        ]
        display[detail_columns["Job"]] = display[detail_columns["Job"]].map(job_plain_label)
        display[detail_columns["KPI"]] = display[detail_columns["KPI"]].map(display_kpi)
        display[detail_columns["KPIGroup"]] = display[detail_columns["KPIGroup"]].map(display_kpi_group)
        st.dataframe(
            display,
            width="stretch",
            hide_index=True,
            height=min(620, 38 * (len(display) + 1)),
        )

    with st.expander(tr("标准化明细", "Standardized Data")):
        raw_display = filtered.copy()
        raw_display["Month"] = raw_display["Month"].dt.strftime("%Y/%m")
        raw_display["Value"] = raw_display.apply(
            lambda row: (
                row["Reason"]
                if row["MetricType"] == "reason"
                else
                f"{row['Value']:.1%}"
                if row["MetricType"] == "rate"
                else f"{row['Value']:g}"
            ),
            axis=1,
        )
        raw_columns = {
            "Month": tr("月份", "Month"),
            "Job": tr("职位", "Role"),
            "Name": tr("员工", "Employee"),
            "KPI": tr("二级KPI", "KPI"),
            "KPIGroup": tr("KPI分类", "KPI Category"),
            "MetricType": tr("数据类型", "Data Type"),
            "Value": tr("数值", "Value"),
        }
        raw_display = raw_display.rename(columns=raw_columns)
        raw_display[raw_columns["MetricType"]] = raw_display[raw_columns["MetricType"]].map(
            {
                "rate": tr("比率", "Rate"),
                "count": tr("次数", "Count"),
                "duration": tr("周期", "Duration"),
                "reason": tr("原因", "Reason"),
            }
        ).fillna(raw_display[raw_columns["MetricType"]])
        raw_display[raw_columns["Job"]] = raw_display[raw_columns["Job"]].map(job_plain_label)
        raw_display[raw_columns["KPI"]] = raw_display[raw_columns["KPI"]].map(display_kpi)
        raw_display[raw_columns["KPIGroup"]] = raw_display[raw_columns["KPIGroup"]].map(display_kpi_group)
        st.dataframe(
            raw_display[
                [
                    raw_columns["Month"],
                    raw_columns["Job"],
                    raw_columns["Name"],
                    raw_columns["KPI"],
                    raw_columns["KPIGroup"],
                    raw_columns["MetricType"],
                    raw_columns["Value"],
                ]
            ],
            width="stretch",
            hide_index=True,
        )
