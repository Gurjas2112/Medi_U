"""Score encounters for above-median length-of-stay risk."""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd

from src.config import MODEL_PATH
from src.schema import to_pascal_case

REQUIRED_COLUMNS = ["Age", "Gender", "MedicalCondition", "AdmissionType"]


def load_model(model_path: Path | None = None):
    path = model_path or MODEL_PATH
    with path.open("rb") as handle:
        artifact = pickle.load(handle)
    if isinstance(artifact, dict) and "model" in artifact:
        return artifact
    return {"model": artifact, "feature_columns": None}


def prepare_features(df: pd.DataFrame, feature_columns: list[str] | None = None) -> pd.DataFrame:
    frame = to_pascal_case(df)
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns for prediction: {missing}")
    features = pd.get_dummies(frame[REQUIRED_COLUMNS])
    if feature_columns is not None:
        features = features.reindex(columns=feature_columns, fill_value=0)
    return features


def predict_stay_risk(input_df: pd.DataFrame, model_path: Path | None = None) -> pd.DataFrame:
    artifact = load_model(model_path)
    model = artifact["model"]
    X = prepare_features(input_df, artifact.get("feature_columns"))
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    result = to_pascal_case(input_df).copy()
    result["PredictedLongStay"] = predictions
    result["RiskProbability"] = probabilities
    result["StayRiskLabel"] = result["PredictedLongStay"].map({0: "Expected stay", 1: "High stay risk"})
    return result


def predict_from_csv(csv_path: str | Path, model_path: Path | None = None) -> pd.DataFrame:
    return predict_stay_risk(pd.read_csv(csv_path), model_path=model_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict long-stay risk from hospital data")
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default=str(MODEL_PATH))
    args = parser.parse_args()
    scored = predict_from_csv(args.input, model_path=Path(args.model))
    print(
        scored[
            ["Age", "Gender", "MedicalCondition", "AdmissionType", "RiskProbability", "StayRiskLabel"]
        ].head()
    )
