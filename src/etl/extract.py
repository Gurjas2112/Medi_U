"""Step 1: extract hospital encounters from Kaggle or a synthetic fallback."""

from __future__ import annotations

import random
import shutil
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import KAGGLE_DATASET, RAW_DATA_DIR, RAW_FILE, ensure_directories


def download_from_kaggle() -> Path | None:
    try:
        import kagglehub
    except ImportError:
        print("kagglehub is not installed; skipping live download.")
        return None

    try:
        print(f"Downloading dataset '{KAGGLE_DATASET}' from Kaggle...")
        dataset_path = kagglehub.dataset_download(KAGGLE_DATASET)
        csv_files = list(Path(dataset_path).glob("*.csv"))
        if not csv_files:
            print("No CSV file found in the downloaded dataset.")
            return None
        ensure_directories()
        shutil.copy(csv_files[0], RAW_FILE)
        print(f"Copied raw data to: {RAW_FILE}")
        return RAW_FILE
    except Exception as exc:
        print(f"Kaggle download failed or is not configured: {exc}")
        return None


def generate_synthetic_fallback(n_rows: int = 5000) -> Path:
    from faker import Faker

    print(f"Generating synthetic hospital encounters ({n_rows} rows)...")
    fake = Faker()
    Faker.seed(42)
    np.random.seed(42)
    random.seed(42)

    genders = ["Male", "Female"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    conditions = ["Diabetes", "Hypertension", "Asthma", "Cancer", "Obesity", "Arthritis"]
    doctors = [fake.name() for _ in range(40)]
    hospitals = [f"{fake.last_name()} Medical Center" for _ in range(15)]
    insurance_providers = ["Aetna", "Blue Cross", "Cigna", "Medicare", "UnitedHealthcare"]
    admission_types = ["Emergency", "Elective", "Urgent"]
    medications = ["Aspirin", "Ibuprofen", "Penicillin", "Paracetamol", "Lipitor"]
    test_results = ["Normal", "Abnormal", "Inconclusive"]
    departments = [
        "Cardiology",
        "Neurology",
        "Orthopedics",
        "Pediatrics",
        "Oncology",
        "General Medicine",
        "Emergency",
    ]

    start_date = pd.Timestamp("2022-01-01")
    date_range_days = (pd.Timestamp("2024-12-31") - start_date).days
    rows = []
    for _ in range(n_rows):
        admission_date = start_date + timedelta(days=random.randint(0, date_range_days))
        stay_length = random.randint(1, 20)
        rows.append(
            {
                "Name": fake.name(),
                "Age": random.randint(0, 95),
                "Gender": random.choice(genders),
                "Blood Type": random.choice(blood_types),
                "Medical Condition": random.choice(conditions),
                "Date of Admission": admission_date.strftime("%Y-%m-%d"),
                "Doctor": random.choice(doctors),
                "Hospital": random.choice(hospitals),
                "Department": random.choice(departments),
                "Insurance Provider": random.choice(insurance_providers),
                "Billing Amount": round(random.uniform(500, 55000), 2),
                "Room Number": random.randint(100, 999),
                "Admission Type": random.choice(admission_types),
                "Discharge Date": (admission_date + timedelta(days=stay_length)).strftime("%Y-%m-%d"),
                "Medication": random.choice(medications),
                "Test Results": random.choice(test_results),
            }
        )

    df = pd.DataFrame(rows)
    df = pd.concat([df, df.sample(frac=0.02, random_state=1)], ignore_index=True)
    for col in ["Billing Amount", "Insurance Provider", "Age"]:
        missing_idx = df.sample(frac=0.01, random_state=2).index
        df.loc[missing_idx, col] = None

    ensure_directories()
    df.to_csv(RAW_FILE, index=False)
    print(f"Synthetic raw dataset written to: {RAW_FILE}")
    return RAW_FILE


def main(n_rows: int = 5000) -> Path:
    ensure_directories()
    path = download_from_kaggle()
    if path is None:
        path = generate_synthetic_fallback(n_rows=n_rows)
    df = pd.read_csv(path)
    print(f"Raw dataset shape: {df.shape}")
    return path


if __name__ == "__main__":
    main()
