# Imports 
from __future__ import annotations
from pathlib import Path
from typing import Optional
import pandas as pd

EXAMPLES_PATH  = Path("data/examples/trends.csv")
EXPECTED_COLUMNS = [ "topic", "score", "source", "discovered_at", "region", "niche"]   


def load_examples(csv_path: Optional[Path] = None) -> pd.DataFrame:
    # Load trends from CSV into clean pandas DataFrame.
    path = csv_path or EXAMPLES_PATH
    if not path.exists():
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    df = pd.read_csv(path)
   
   # Normalize column names and ensure all expected columns are present
    df.columns = [col.strip().lower() for col in df.columns]
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    
    # Parse types 
    df["discovered_at"] = pd.to_datetime(df["discovered_at"], errors="coerce", utc=True)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    # Trim overly long topics 
    df["topic"] = df["topic"].astype(str).str.slice(0, 180)

    # Reorder to expected columns then anything extra 
    extras = [c for c in df.columns if c not in EXPECTED_COLUMNS]  # type: ignore
    df = df[EXPECTED_COLUMNS + extras]

    return df
