"""Run the hospital analytics pipeline from the repository root."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.etl.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()
