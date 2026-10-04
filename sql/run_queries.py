"""Run every sql/analysis/*.sql against warehouse.db and write docs/query_results/<name>.csv.

    python sql/run_queries.py            # builds warehouse.db first if it does not exist
    python sql/run_queries.py --db path/to/warehouse.db --out some/dir
"""
from __future__ import annotations

import argparse
import math
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.config import WAREHOUSE_DB  # noqa: E402

QUERY_DIR = ROOT / "sql" / "analysis"
OUT_DIR = ROOT / "docs" / "query_results"


def connect(db: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    # Some SQLite builds ship without math functions; make sqrt available either way.
    conn.create_function("sqrt", 1, lambda x: None if x is None or x < 0 else math.sqrt(x),
                         deterministic=True)
    return conn


def run_all(db: Path | str = WAREHOUSE_DB, out_dir: Path | str = OUT_DIR) -> dict[str, pd.DataFrame]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    conn = connect(db)
    try:
        for sql_file in sorted(QUERY_DIR.glob("*.sql")):
            df = pd.read_sql_query(sql_file.read_text(encoding="utf-8"), conn)
            df.to_csv(out_dir / f"{sql_file.stem}.csv", index=False)
            results[sql_file.stem] = df
            print(f"{sql_file.name}: {len(df)} rows -> {out_dir / (sql_file.stem + '.csv')}")
    finally:
        conn.close()
    return results


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default=WAREHOUSE_DB)
    p.add_argument("--out", default=OUT_DIR)
    a = p.parse_args(argv)
    if not Path(a.db).exists():
        from pipeline.run import run
        if run(db=a.db, write_report=False):
            return 1
    run_all(a.db, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
