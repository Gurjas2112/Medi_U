"""Canonical Patients schema helpers."""

from __future__ import annotations

import pandas as pd

from src.config import COLUMN_MAP


def to_pascal_case(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(columns={col: COLUMN_MAP.get(col, col) for col in df.columns})
    return renamed


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ("DateOfAdmission", "DischargeDate"):
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    return out
