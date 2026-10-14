import json
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def test_role_filter_opens_employee_trend(self):
        workbook = BytesIO()
        rows = [
            ["Modelist", "Jiao Chen", "TP BOM RFT", 0.96, 0],
            ["Modelist", "Mengli Jiang", "TP PAP RFT", 1, 0.94],
            ["ME", "Cancan Gong", "SOT RFT", 1, 0.95],
            ["Designer", "Louis Diao", "3D RFT", 1, 0.9],
            ["PIS", "Bethy Tang", "SSS RFT", 0, "NA"],
        ]
        with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
            pd.DataFrame(rows, columns=["JOB", "NAME", "KPI", "2026/8", "2026/9"]).to_excel(
                writer, sheet_name="DATABASE for Dashboard", index=False
            )

        for role, name, module in (
            ("ME", "Cancan Gong", "SOT RFT"),
            ("Designer", "Louis Diao", "3D RFT"),
            ("PIS", "Bethy Tang", "SSS RFT"),
        ):
            with self.subTest(role=role):
                def role_filter(label, options, **kwargs):
                    return [role] if label == "职位" else [name]

                with patch("google_source.download_google_sheet", return_value=workbook.getvalue()), patch(
                    "streamlit.multiselect", side_effect=role_filter
                ):
                    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
                    app.session_state["selected_kpi_module"] = "TP RFT"
                    app.run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(app.session_state["selected_kpi_module"], module)
                self.assertIn(f"#### {name}", [item.value for item in app.markdown])
                charts = app.get("plotly_chart")
                self.assertEqual(len(charts), 1)
                spec = json.loads(charts[0].proto.spec)
                self.assertTrue(any(name in trace.get("name", "") for trace in spec["data"]))
                self.assertTrue(all("lines" in trace["mode"] for trace in spec["data"]))


if __name__ == "__main__":
    unittest.main()
