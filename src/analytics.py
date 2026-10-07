"""Shared KPI queries and deterministic question answering."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src.config import ANALYTICS_DB, CLEANED_FILE, SAMPLE_CSV, TABLE_NAME, sqlite_uri
from src.schema import normalize_dates, to_pascal_case


def load_patients(path: Path | None = None) -> pd.DataFrame:
    if path is not None:
        return _read_source(path)

    for candidate in (ANALYTICS_DB, SAMPLE_CSV, CLEANED_FILE):
        if candidate.exists() and candidate.stat().st_size > 0:
            return _read_source(candidate)

    raise FileNotFoundError(
        "No hospital dataset found. Run `python -m src.etl.pipeline` or ensure "
        f"{SAMPLE_CSV} / {ANALYTICS_DB} exists."
    )


def _read_source(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".db", ".sqlite"}:
        engine = create_engine(sqlite_uri(path))
        df = pd.read_sql_table(TABLE_NAME, engine)
    else:
        df = pd.read_csv(path)
    return normalize_dates(to_pascal_case(df))


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    return {
        "total_patients": int(len(df)),
        "total_revenue": float(df["BillingAmount"].sum()),
        "avg_billing": float(df["BillingAmount"].mean()),
        "avg_length_of_stay": float(df["LengthOfStay"].mean()),
    }


def department_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Department", as_index=False)
        .agg(
            PatientCount=("PatientID", "count"),
            TotalRevenue=("BillingAmount", "sum"),
            AvgBilling=("BillingAmount", "mean"),
            AvgLengthOfStay=("LengthOfStay", "mean"),
        )
        .sort_values("TotalRevenue", ascending=False)
    )


def monthly_admissions(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["AdmissionYear", "AdmissionMonth", "AdmissionMonthName"], as_index=False)
        .agg(Admissions=("PatientID", "count"), Revenue=("BillingAmount", "sum"))
        .sort_values(["AdmissionYear", "AdmissionMonth"])
    )
    monthly["Period"] = (
        monthly["AdmissionYear"].astype(int).astype(str)
        + "-"
        + monthly["AdmissionMonth"].astype(int).astype(str).str.zfill(2)
    )
    return monthly


def top_doctors(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Doctor", as_index=False)
        .agg(
            PatientsHandled=("PatientID", "count"),
            RevenueGenerated=("BillingAmount", "sum"),
        )
        .sort_values("PatientsHandled", ascending=False)
        .head(n)
    )


def insurance_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("InsuranceProvider", as_index=False)
        .agg(PatientCount=("PatientID", "count"), TotalBilled=("BillingAmount", "sum"))
        .sort_values("TotalBilled", ascending=False)
    )


def condition_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("MedicalCondition", as_index=False)
        .agg(Cases=("PatientID", "count"), AvgStay=("LengthOfStay", "mean"))
        .sort_values("Cases", ascending=False)
    )


def gender_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["Gender"].value_counts().rename_axis("Gender").reset_index(name="PatientCount")
    counts["Percentage"] = (counts["PatientCount"] / counts["PatientCount"].sum() * 100).round(2)
    return counts


def answer_question(question: str, df: pd.DataFrame | None = None) -> str:
    """Deterministic analytics answers used when no LLM is configured."""
    data = df if df is not None else load_patients()
    q = question.lower()
    kpis = compute_kpis(data)

    if any(term in q for term in ("total patient", "how many patient", "patient count")):
        return f"There are {kpis['total_patients']:,} patients in the current dataset."

    if "length of stay" in q or "avg stay" in q or "average stay" in q:
        if "department" in q:
            table = department_performance(data)[["Department", "AvgLengthOfStay"]]
            lines = [f"{row.Department}: {row.AvgLengthOfStay:.1f} days" for row in table.itertuples()]
            return "Average length of stay by department:\n" + "\n".join(lines)
        return f"Average length of stay is {kpis['avg_length_of_stay']:.1f} days."

    if "revenue" in q or "total billed" in q or "total billing" in q:
        if "department" in q:
            table = department_performance(data)[["Department", "TotalRevenue"]]
            lines = [f"{row.Department}: ${row.TotalRevenue:,.2f}" for row in table.itertuples()]
            return "Revenue by department:\n" + "\n".join(lines)
        if "insurance" in q:
            table = insurance_breakdown(data)
            lines = [f"{row.InsuranceProvider}: ${row.TotalBilled:,.2f}" for row in table.itertuples()]
            return "Billed amount by insurance provider:\n" + "\n".join(lines)
        return f"Total revenue is ${kpis['total_revenue']:,.2f}."

    if "average billing" in q or "avg billing" in q or "average bill" in q:
        if "department" in q:
            table = department_performance(data)[["Department", "AvgBilling"]]
            lines = [f"{row.Department}: ${row.AvgBilling:,.2f}" for row in table.itertuples()]
            return "Average billing by department:\n" + "\n".join(lines)
        return f"Average billing amount is ${kpis['avg_billing']:,.2f}."

    if "top doctor" in q or "busiest doctor" in q or "doctors by" in q:
        table = top_doctors(data)
        lines = [
            f"{row.Doctor}: {int(row.PatientsHandled)} patients, ${row.RevenueGenerated:,.2f}"
            for row in table.itertuples()
        ]
        return "Top doctors by patient volume:\n" + "\n".join(lines)

    if "insurance" in q:
        table = insurance_breakdown(data)
        lines = [
            f"{row.InsuranceProvider}: {int(row.PatientCount)} patients, ${row.TotalBilled:,.2f}"
            for row in table.itertuples()
        ]
        return "Insurance coverage breakdown:\n" + "\n".join(lines)

    if "condition" in q or "diagnosis" in q:
        table = condition_breakdown(data)
        lines = [f"{row.MedicalCondition}: {int(row.Cases)} cases" for row in table.itertuples()]
        return "Most frequent medical conditions:\n" + "\n".join(lines)

    if "gender" in q:
        table = gender_breakdown(data)
        lines = [f"{row.Gender}: {int(row.PatientCount)} ({row.Percentage}%)" for row in table.itertuples()]
        return "Gender distribution:\n" + "\n".join(lines)

    if "monthly" in q or "trend" in q or "admission" in q:
        table = monthly_admissions(data).tail(12)
        lines = [f"{row.Period}: {int(row.Admissions)} admissions" for row in table.itertuples()]
        return "Recent monthly admissions:\n" + "\n".join(lines)

    if "executive" in q or "kpi" in q or "summary" in q:
        return (
            "Executive summary:\n"
            f"- Patients: {kpis['total_patients']:,}\n"
            f"- Total revenue: ${kpis['total_revenue']:,.2f}\n"
            f"- Average billing: ${kpis['avg_billing']:,.2f}\n"
            f"- Average length of stay: {kpis['avg_length_of_stay']:.1f} days"
        )

    return (
        "I can answer operational questions about patient volume, revenue, average billing, "
        "length of stay, departments, doctors, insurance, conditions, gender mix, and monthly trends. "
        "Try: 'What is total revenue by department?'"
    )
