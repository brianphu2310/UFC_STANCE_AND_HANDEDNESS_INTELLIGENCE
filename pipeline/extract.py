"""Extract: read the project's enriched fighter CSV into a DataFrame, unchanged."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import SOURCE_CSV


def extract(path: Path | str = SOURCE_CSV) -> pd.DataFrame:
    """Read the source CSV. No cleaning happens here; that is validate/transform's job."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"source file not found: {path}")
    return pd.read_csv(path)
