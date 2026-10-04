"""Load: create ``warehouse.db`` from schema.sql and insert the transformed tables (full refresh)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from .config import SCHEMA_SQL, SOURCE_CSV, WAREHOUSE_DB

# Parents before children so foreign keys are satisfied while loading.
LOAD_ORDER = ["dim_stance", "dim_handedness", "dim_weight_class", "dim_country",
              "dim_fighting_style", "dim_fighter", "fact_fighter_record", "fact_ufc_performance"]


def load(tables: dict[str, pd.DataFrame], db_path: Path | str = WAREHOUSE_DB,
         source: Path | str = SOURCE_CSV) -> Path:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()             # full refresh keeps the load idempotent
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:                   # one transaction: all tables or none
            for name in LOAD_ORDER:
                tables[name].to_sql(name, conn, if_exists="append", index=False)
            conn.executemany(
                "INSERT INTO etl_load_audit(table_name, row_count, source_file) VALUES (?,?,?)",
                [(n, len(tables[n]), Path(source).name) for n in LOAD_ORDER])
        bad = conn.execute("PRAGMA foreign_key_check").fetchall()
        if bad:
            raise RuntimeError(f"foreign key violations after load: {bad[:5]}")
        conn.execute("ANALYZE")
    finally:
        conn.close()
    return db_path
