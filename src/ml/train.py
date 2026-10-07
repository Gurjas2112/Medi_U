"""Train a Random Forest classifier for above-median length of stay."""

from __future__ import annotations

import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from src.analytics import load_patients
from src.config import MODEL_PATH, ensure_directories

FEATURE_COLUMNS = ["Age", "Gender", "MedicalCondition", "AdmissionType"]


def train_stay_risk_model() -> dict:
    df = load_patients()
    df = df.dropna(subset=FEATURE_COLUMNS + ["LengthOfStay"])
    df["IsLongStay"] = (df["LengthOfStay"] > df["LengthOfStay"].median()).astype(int)

    X = pd.get_dummies(df[FEATURE_COLUMNS])
    y = df["IsLongStay"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    accuracy = accuracy_score(y_test, predictions)
    auc = roc_auc_score(y_test, probabilities)
    print(f"Stay-risk model accuracy={accuracy:.3f} roc_auc={auc:.3f}")

    ensure_directories()
    artifact = {
        "model": model,
        "feature_columns": list(X.columns),
        "metrics": {"accuracy": accuracy, "roc_auc": auc},
        "categories": {
            "Gender": sorted(df["Gender"].dropna().astype(str).unique().tolist()),
            "MedicalCondition": sorted(df["MedicalCondition"].dropna().astype(str).unique().tolist()),
            "AdmissionType": sorted(df["AdmissionType"].dropna().astype(str).unique().tolist()),
        },
    }
    with MODEL_PATH.open("wb") as handle:
        pickle.dump(artifact, handle)
    print(f"Stay-risk model saved to {MODEL_PATH}")
    return artifact


if __name__ == "__main__":
    train_stay_risk_model()
