import unittest
from io import BytesIO
from pathlib import Path

import pandas as pd

from google_source import extract_google_sheet_id, google_sheet_export_url
from kpi_data import classify_kpi, load_kpi_data, parse_month_header, target_for_kpi


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "DCKPI Dashboard.xlsx"


class KPIDataTests(unittest.TestCase):
    def test_google_sheet_url(self):
        url = (
            "https://docs.google.com/spreadsheets/d/"
            "1msT7WcjkYva2yojVNrET2xJfqRS00xH85j1D85Ne36Q/edit?usp=sharing"
        )
        self.assertEqual(
            extract_google_sheet_id(url),
            "1msT7WcjkYva2yojVNrET2xJfqRS00xH85j1D85Ne36Q",
        )
        self.assertTrue(google_sheet_export_url(url).endswith("/export?format=xlsx"))

    def test_excel_serial_header(self):
        self.assertEqual(parse_month_header(46071), pd.Timestamp("2026-02-01"))

    def test_kpi_classification(self):
        self.assertEqual(classify_kpi("PAP 一次通过率"), ("rate", "RFT"))
        self.assertEqual(classify_kpi("未准时提交的次数"), ("count", "异常次数"))
        self.assertEqual(
            classify_kpi("未准时提交的原因"), ("reason", "未准时原因")
        )
        self.assertEqual(classify_kpi("MARKER RFT"), ("rate", "RFT"))
        self.assertEqual(classify_kpi("MARKER ON TIME"), ("rate", "准时交付"))
        self.assertEqual(classify_kpi("TP BOM ON TIME"), ("rate", "准时交付"))
        self.assertEqual(classify_kpi("TP TF RFT"), ("rate", "RFT"))
        self.assertEqual(classify_kpi("TP TF ON TIME"), ("rate", "准时交付"))
        self.assertEqual(classify_kpi("SOT RFT"), ("rate", "RFT"))
        self.assertEqual(classify_kpi("SOT ON TIME"), ("rate", "准时交付"))
        self.assertEqual(target_for_kpi("SOT ON TIME", "rate"), 1.0)
        self.assertEqual(target_for_kpi("未准时提交的次数", "count"), 2.0)

    def test_sample_workbook(self):
        data, info = load_kpi_data(SAMPLE)
        self.assertEqual(info["sheet_name"], "工作表2")
        self.assertEqual(info["job_count"], 4)
        self.assertEqual(info["employee_count"], 5)
        self.assertEqual(info["month_count"], 5)
        self.assertEqual(len(data), 74)
        self.assertEqual(info["reason_count"], 4)
        self.assertAlmostEqual(
            data.loc[data["KPI"].eq("样品一次通过率"), "Value"].min(),
            0.7143,
        )
        reasons = data[data["MetricType"].eq("reason")]
        self.assertIn("软件研究", reasons["Reason"].tolist())
        self.assertIn("样品间排单拥挤", reasons["Reason"].tolist())
        self.assertTrue(reasons["Target"].isna().all())

    def test_two_row_dashboard_database(self):
        workbook = BytesIO()
        dashboard_rows = pd.DataFrame(
            [
                ["JOB", "NAME", "KPI", 2026, None],
                [None, None, None, 1, 2],
                ["Designer", "Louis Diao", "3D RFT", 1.0, 0.98],
                ["ME", "Cancan Gong", "SOT ON TIME", None, None],
            ]
        )
        with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
            pd.DataFrame({"old": [1]}).to_excel(
                writer, sheet_name="KPI database", index=False
            )
            dashboard_rows.to_excel(
                writer,
                sheet_name="8.10 DATABASE for Dashboard",
                index=False,
                header=False,
            )
        workbook.seek(0)

        data, info = load_kpi_data(workbook)

        self.assertEqual(info["sheet_name"], "8.10 DATABASE for Dashboard")
        self.assertEqual(info["employee_count"], 2)
        self.assertEqual(info["job_count"], 2)
        self.assertEqual(info["data_points"], 2)
        self.assertEqual(
            sorted(data["Month"].dt.strftime("%Y/%m").unique().tolist()),
            ["2026/01", "2026/02"],
        )
        self.assertEqual(
            info["roster"],
            [
                {"Job": "Designer", "Name": "Louis Diao"},
                {"Job": "ME", "Name": "Cancan Gong"},
            ],
        )

    def test_single_row_dashboard_database_treats_na_as_not_applicable(self):
        workbook = BytesIO()
        dashboard = pd.DataFrame(
            {
                "JOB": ["Designer", "Modelist", "ME", "PIS"],
                "NAME": ["Louis Diao", "Jiao Chen", "Cancan Gong", "Bethy Tang"],
                "KPI": ["3D RFT", "TP BOM RFT", "SOT ON TIME", "SSS RFT"],
                pd.Timestamp("2026-01-01"): [1.0, "NA", "", ""],
                pd.Timestamp("2026-02-01"): [1.0, 0.5, "N/A", ""],
                pd.Timestamp("2026-03-01"): ["", "", "", ""],
            }
        )
        with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
            pd.DataFrame({"old": [1]}).to_excel(
                writer, sheet_name="KPI database", index=False
            )
            dashboard.to_excel(
                writer, sheet_name="8.14 DATABASE for Dashboard", index=False
            )
        workbook.seek(0)

        data, info = load_kpi_data(workbook)

        self.assertEqual(info["sheet_name"], "8.14 DATABASE for Dashboard")
        self.assertEqual(info["data_points"], 3)
        self.assertEqual(info["invalid_numeric"], 0)
        self.assertEqual(info["not_applicable_count"], 2)
        self.assertEqual(
            [month.strftime("%Y/%m") for month in info["reporting_months"]],
            ["2026/01", "2026/02"],
        )
        self.assertTrue(data["Value"].notna().all())


if __name__ == "__main__":
    unittest.main()
