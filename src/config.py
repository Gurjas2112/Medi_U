"""Shared paths, schema mapping, and environment defaults."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
MODELS_DIR = ROOT_DIR / "models"
DASHBOARDS_DIR = ROOT_DIR / "dashboards"
EXCEL_DIR = DASHBOARDS_DIR / "excel"
POWERBI_DIR = DASHBOARDS_DIR / "powerbi"
ASSETS_DIR = ROOT_DIR / "assets"
SCREENSHOTS_DIR = ASSETS_DIR / "screenshots"

RAW_FILE = RAW_DATA_DIR / "hospital_raw.csv"
CLEANED_FILE = CLEANED_DATA_DIR / "hospital_cleaned.csv"
CLEANED_SQLITE = CLEANED_DATA_DIR / "hospital.db"
SAMPLE_CSV = SAMPLE_DATA_DIR / "hospital_cleaned_sample.csv"
ANALYTICS_DB = SAMPLE_DATA_DIR / "hospital_analytics.db"
EXCEL_REPORT = EXCEL_DIR / "Hospital_Operational_Report.xlsx"
POWERBI_FILE = POWERBI_DIR / "Hospital_Operational_Dashboard.pbix"
MODEL_PATH = MODELS_DIR / "stay_risk_model.pkl"

TABLE_NAME = "Patients"
SAMPLE_ROW_LIMIT = 1500
KAGGLE_DATASET = "prasad22/healthcare-dataset"

COLUMN_MAP = {
    "PatientID": "PatientID",
    "Name": "Name",
    "Age": "Age",
    "Gender": "Gender",
    "Blood Type": "BloodType",
    "Medical Condition": "MedicalCondition",
    "Date of Admission": "DateOfAdmission",
    "Doctor": "Doctor",
    "Hospital": "Hospital",
    "Department": "Department",
    "Insurance Provider": "InsuranceProvider",
    "Billing Amount": "BillingAmount",
    "Room Number": "RoomNumber",
    "Admission Type": "AdmissionType",
    "Discharge Date": "DischargeDate",
    "Medication": "Medication",
    "Test Results": "TestResults",
    "Age Group": "AgeGroup",
    "Length of Stay": "LengthOfStay",
    "Admission Year": "AdmissionYear",
    "Admission Month": "AdmissionMonth",
    "Admission Month Name": "AdmissionMonthName",
}

POWER_BI_EXE_CANDIDATES = [
    Path(r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"),
    Path(r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe"),
]
POWER_BI_START_MENU = Path(
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Power BI Desktop"
)


def ensure_directories() -> None:
    for path in (
        RAW_DATA_DIR,
        CLEANED_DATA_DIR,
        SAMPLE_DATA_DIR,
        MODELS_DIR,
        EXCEL_DIR,
        POWERBI_DIR,
        SCREENSHOTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def sqlite_uri(path: Path) -> str:
    return "sqlite:///" + path.resolve().as_posix()
