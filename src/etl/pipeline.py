"""Orchestrate extract → transform → load → Excel → stay-risk model."""

from __future__ import annotations

import time

from src.etl.extract import main as extract_main
from src.etl.load_sql import main as load_main
from src.etl.transform import run_transform
from src.excel.generate_report import generate_excel_report
from src.ml.train import train_stay_risk_model


def run_pipeline(n_rows: int = 5000, train_model: bool = True) -> None:
    print("=" * 60)
    print("HOSPITAL ANALYTICS ETL PIPELINE")
    print("=" * 60)
    start = time.time()

    print("\n[1/5] EXTRACT")
    print("-" * 60)
    extract_main(n_rows=n_rows)

    print("\n[2/5] TRANSFORM")
    print("-" * 60)
    run_transform()

    print("\n[3/5] LOAD")
    print("-" * 60)
    load_main()

    print("\n[4/5] EXCEL REPORT")
    print("-" * 60)
    report_path = generate_excel_report()
    print(f"Excel workbook written to: {report_path}")

    if train_model:
        print("\n[5/5] STAY-RISK MODEL")
        print("-" * 60)
        train_stay_risk_model()
    else:
        print("\n[5/5] STAY-RISK MODEL skipped")

    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"PIPELINE COMPLETE in {elapsed:.2f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
