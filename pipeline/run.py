"""Run the full pipeline:  python -m pipeline.run [--source CSV] [--db warehouse.db] [--no-report]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import report
from .config import QUALITY_REPORT, SOURCE_CSV, WAREHOUSE_DB
from .extract import extract
from .load import load
from .transform import transform
from .validate import has_errors, validate


def run(source=SOURCE_CSV, db=WAREHOUSE_DB, report_path=QUALITY_REPORT, write_report=True) -> int:
    df = extract(source)
    print(f"[extract]   {len(df)} rows x {df.shape[1]} cols from {Path(source).name}")
    results = validate(df)
    failed_err = [r for r in results if r.severity == "error" and not r.passed]
    warns = [r for r in results if r.severity == "warn" and not r.passed]
    print(f"[validate]  {len(results)} checks, {len(failed_err)} errors, {len(warns)} warnings with findings")
    if write_report:
        print(f"[report]    {report.write(df, results, report_path, source)}")
    if has_errors(results):
        for r in failed_err:
            print(f"  ERROR {r.name}: {r.failed} rows {r.examples}", file=sys.stderr)
        print("[load]      skipped because of validation errors", file=sys.stderr)
        return 1
    tables = transform(df)
    print("[transform] " + ", ".join(f"{k}={len(v)}" for k, v in tables.items()))
    print(f"[load]      {load(tables, db, source)}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default=SOURCE_CSV)
    p.add_argument("--db", default=WAREHOUSE_DB)
    p.add_argument("--no-report", action="store_true", help="do not rewrite docs/DATA_QUALITY.md")
    a = p.parse_args(argv)
    return run(a.source, a.db, QUALITY_REPORT, not a.no_report)


if __name__ == "__main__":
    sys.exit(main())
