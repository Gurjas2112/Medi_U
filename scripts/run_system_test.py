"""Backend system test covering ETL outputs, SQL, Excel, ML, and AI fallback."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics import answer_question, compute_kpis, load_patients
from src.config import ANALYTICS_DB, EXCEL_REPORT, MODEL_PATH, SAMPLE_CSV, TABLE_NAME
from src.excel.generate_report import generate_excel_report
from src.ml.predict import predict_stay_risk
from src.powerbi.launch_desktop import find_power_bi_desktop
from src.rag.chatbot import ask_hospital_ai

LOG = ROOT / "assets" / "system_test" / "logs" / "backend_system_test.log"
RESULTS: list[tuple[str, str, str]] = []


def record(name: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    RESULTS.append((status, name, detail))
    print(f"[{status}] {name}: {detail}")


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)

    df = load_patients()
    kpis = compute_kpis(df)
    record(
        "Load Patients sample",
        len(df) > 0 and "Department" in df.columns,
        f"{len(df)} rows, columns={len(df.columns)}",
    )
    record(
        "KPI computation",
        kpis["total_patients"] > 0 and kpis["total_revenue"] > 0,
        (
            f"patients={kpis['total_patients']:,} "
            f"revenue=${kpis['total_revenue']:,.2f} "
            f"avg_stay={kpis['avg_length_of_stay']:.1f}"
        ),
    )

    conn = sqlite3.connect(ANALYTICS_DB)
    count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    cols = [row[1] for row in conn.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]
    conn.close()
    record(
        "SQLite Patients table",
        count == len(df) and "BillingAmount" in cols and "LengthOfStay" in cols,
        f"{count} rows, PascalCase={('BillingAmount' in cols)}",
    )
    record("Hostable sample CSV", SAMPLE_CSV.exists(), str(SAMPLE_CSV))

    report = generate_excel_report()
    from openpyxl import load_workbook

    wb = load_workbook(report, read_only=True)
    expected_sheets = {"Executive", "Admissions", "Doctors", "Financial", "Patients"}
    record(
        "Excel operational report",
        expected_sheets.issubset(set(wb.sheetnames)),
        f"{report.name} sheets={wb.sheetnames}",
    )
    wb.close()

    scored = predict_stay_risk(
        pd.DataFrame(
            [
                {
                    "Age": 72,
                    "Gender": "Female",
                    "MedicalCondition": "Cancer",
                    "AdmissionType": "Emergency",
                }
            ]
        )
    )
    record(
        "Stay-risk model scoring",
        MODEL_PATH.exists() and "StayRiskLabel" in scored.columns,
        f"{scored.iloc[0]['StayRiskLabel']} p={scored.iloc[0]['RiskProbability']:.3f}",
    )

    answer = ask_hospital_ai("What is total revenue by department?")
    record(
        "AI / analytics Q&A fallback",
        "revenue" in answer.lower() or "department" in answer.lower(),
        answer.replace("\n", " | ")[:240],
    )
    summary = answer_question("executive summary", df)
    record("Executive summary Q&A", "Patients" in summary, summary.replace("\n", " | "))

    pbi = find_power_bi_desktop()
    record(
        "Power BI Desktop discovery",
        pbi is not None and pbi.exists(),
        str(pbi),
    )
    record("Power BI pbix present", EXCEL_REPORT.exists(), str(EXCEL_REPORT))

    failed = sum(1 for status, _, _ in RESULTS if status == "FAIL")
    LOG.write_text(
        "\n".join(f"{status}\t{name}\t{detail}" for status, name, detail in RESULTS),
        encoding="utf-8",
    )
    print(f"\nWrote {LOG}")
    print(f"Passed {len(RESULTS) - failed}/{len(RESULTS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
