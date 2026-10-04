"""Documentation stays in sync with the data."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_every_column_in_dictionary_md():
    cols = pd.read_csv(ROOT / "data" / "ufc_fighters_enriched.csv", nrows=1).columns
    text = (ROOT / "docs" / "DATA_DICTIONARY.md").read_text(encoding="utf-8")
    assert [c for c in cols if c not in text] == []


def test_skills_doc_paths_exist():
    import re
    text = (ROOT / "docs" / "SKILLS_DEMONSTRATED.md").read_text(encoding="utf-8")
    paths = set(re.findall(r"`((?:pipeline|sql|tests|docs|scripts|data|notebooks|\.github)/[\w./\-]*[\w])`", text))
    assert paths, "no paths found"
    missing = [p for p in paths if not (ROOT / p).exists()]
    assert missing == []
