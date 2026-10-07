"""Step 2: clean, validate, and enrich hospital encounters."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import CLEANED_FILE, RAW_FILE, ensure_directories


def load_raw(path: Path = RAW_FILE) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded raw data: {df.shape}")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed {before - len(df)} duplicate rows")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Billing Amount"] = df["Billing Amount"].fillna(df["Billing Amount"].median())
    df["Insurance Provider"] = df["Insurance Provider"].fillna("Unknown")
    critical_cols = ["Name", "Date of Admission", "Doctor", "Hospital"]
    before = len(df)
    df = df.dropna(subset=critical_cols)
    print(f"Dropped {before - len(df)} rows missing critical fields")
    return df


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], errors="coerce")
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], errors="coerce")
    df["Age"] = df["Age"].astype(int)
    df["Billing Amount"] = df["Billing Amount"].astype(float).round(2)
    df["Room Number"] = df["Room Number"].astype(int)
    return df


def validate_billing(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df[df["Billing Amount"] > 0]
    print(f"Removed {before - len(df)} rows with invalid (non-positive) billing")
    return df


def add_age_groups(df: pd.DataFrame) -> pd.DataFrame:
    bins = [0, 12, 19, 35, 50, 65, 120]
    labels = [
        "Child (0-12)",
        "Teen (13-19)",
        "Young Adult (20-35)",
        "Adult (36-50)",
        "Middle Age (51-65)",
        "Senior (65+)",
    ]
    df["Age Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)
    return df


def add_length_of_stay(df: pd.DataFrame) -> pd.DataFrame:
    df["Length of Stay"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days
    df["Length of Stay"] = df["Length of Stay"].clip(lower=0)
    return df


def add_calendar_fields(df: pd.DataFrame) -> pd.DataFrame:
    df["Admission Year"] = df["Date of Admission"].dt.year
    df["Admission Month"] = df["Date of Admission"].dt.month
    df["Admission Month Name"] = df["Date of Admission"].dt.strftime("%B")
    return df


def add_patient_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index(drop=True)
    if "PatientID" not in df.columns:
        df.insert(0, "PatientID", range(1, len(df) + 1))
    return df


def add_department_if_missing(df: pd.DataFrame) -> pd.DataFrame:
    if "Department" in df.columns and df["Department"].notna().any():
        df["Department"] = df["Department"].fillna("General Medicine")
        return df

    condition_to_dept = {
        "Cancer": "Oncology",
        "Obesity": "Endocrinology",
        "Diabetes": "Endocrinology",
        "Asthma": "Pulmonology",
        "Hypertension": "Cardiology",
        "Arthritis": "Orthopedics",
    }
    source = df["Medical Condition"] if "Medical Condition" in df.columns else df.get("MedicalCondition")
    df["Department"] = source.map(condition_to_dept).fillna("General Medicine")
    print("Added Department from medical condition (source extract had no department column).")
    return df


def run_transform(raw_path: Path = RAW_FILE) -> pd.DataFrame:
    ensure_directories()
    df = load_raw(raw_path)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = convert_data_types(df)
    df = validate_billing(df)
    df = add_age_groups(df)
    df = add_length_of_stay(df)
    df = add_calendar_fields(df)
    df = add_department_if_missing(df)
    df = add_patient_id(df)
    df.to_csv(CLEANED_FILE, index=False)
    print(f"Cleaned dataset shape: {df.shape}")
    print(f"Cleaned dataset written to: {CLEANED_FILE}")
    return df


if __name__ == "__main__":
    run_transform()
