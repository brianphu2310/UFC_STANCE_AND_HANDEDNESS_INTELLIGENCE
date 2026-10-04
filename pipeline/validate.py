"""Validate: data-quality checks that run on the extracted data before anything is loaded.

Each check returns a :class:`CheckResult`. Severity ``error`` blocks the load; ``warn`` is
reported but allowed (used for cross-source differences and expected missing values).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import VALID_GENDERS, VALID_HANDS, VALID_STANCES, VALID_STYLES

REQUIRED_COLUMNS = [
    "fighter", "country", "continent", "stance", "stance_project", "hand", "wins", "losses",
    "total_fights", "win_rate", "weight_class", "gender", "height_cm", "reach_cm", "dob",
    "ufcstats_url", "ufc_fights", "ufc_wins", "ufc_losses", "ufc_ko_wins", "ufc_sub_wins",
    "ufc_dec_wins", "first_ufc_fight", "last_ufc_fight", "fighting_style", "champion",
    "popularity_index", "weight_class_source", "learning_tip", "active",
]
PERCENT_COLUMNS = ["win_rate", "str_acc", "str_def", "td_acc", "td_def", "ctrl_pct",
                   "pct_distance", "pct_clinch", "pct_ground", "pct_head", "pct_body", "pct_leg"]
NOT_NULL = ["fighter", "country", "continent", "stance", "hand", "wins", "losses", "total_fights",
            "win_rate", "weight_class", "gender", "height_cm", "dob", "fighting_style"]


@dataclass
class CheckResult:
    name: str
    description: str
    severity: str            # "error" | "warn"
    failed: int              # number of offending rows (or 1 for a table-level failure)
    total: int               # rows examined
    examples: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.failed == 0


def _result(name, description, severity, bad: pd.Series, df, id_col="fighter") -> CheckResult:
    bad = pd.Series(bad, index=df.index).fillna(False).astype(bool)
    ex = df.loc[bad, id_col].astype(str).head(5).tolist() if id_col in df else []
    return CheckResult(name, description, severity, int(bad.sum()), len(df), ex)


def validate(df: pd.DataFrame) -> list[CheckResult]:
    results: list[CheckResult] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    results.append(CheckResult("required_columns", "All columns the pipeline needs are present",
                               "error", len(missing), len(REQUIRED_COLUMNS),
                               [f"missing: {c}" for c in missing[:5]]))
    if missing:                      # nothing else can be evaluated safely
        return results

    results.append(CheckResult("non_empty", "Source has at least one row", "error",
                               int(len(df) == 0), 1))
    results.append(_result("unique_fighter", "fighter is unique (natural key)", "error",
                           df["fighter"].duplicated(keep=False), df))
    results.append(_result("unique_url", "ufcstats_url is unique where present", "error",
                           df["ufcstats_url"].notna() & df["ufcstats_url"].duplicated(keep=False), df))
    nulls = df[NOT_NULL].isna().any(axis=1)
    results.append(_result("not_null_core", f"No nulls in {', '.join(NOT_NULL)}", "error", nulls, df))

    for col, valid in [("stance", VALID_STANCES), ("hand", VALID_HANDS), ("gender", VALID_GENDERS),
                       ("fighting_style", VALID_STYLES)]:
        results.append(_result(f"domain_{col}", f"{col} is one of {sorted(valid)}", "error",
                               ~df[col].isin(valid), df))

    w, l = df["wins"], df["losses"]
    results.append(_result("record_non_negative", "wins and losses are non-negative integers", "error",
                           (w < 0) | (l < 0) | (w % 1 != 0) | (l % 1 != 0), df))
    results.append(_result("total_fights_sum", "total_fights = wins + losses", "error",
                           df["total_fights"] != w + l, df))
    expected = np.where(w + l > 0, w / (w + l).replace(0, np.nan) * 100, np.nan)
    results.append(_result("win_rate_formula", "win_rate = wins / (wins + losses) x 100 (tolerance 0.01)",
                           "error", ~np.isclose(df["win_rate"], expected, atol=0.01), df))

    for col in [c for c in PERCENT_COLUMNS if c in df]:
        results.append(_result(f"range_{col}", f"{col} within 0-100", "error",
                               (df[col] < 0) | (df[col] > 100), df))
    results.append(_result("range_height_cm", "height_cm within 140-220", "error",
                           ~df["height_cm"].between(140, 220), df))
    results.append(_result("range_reach_cm", "reach_cm within 140-230 where present", "error",
                           df["reach_cm"].notna() & ~df["reach_cm"].between(140, 230), df))
    results.append(_result("range_popularity", "popularity_index within 0-100", "error",
                           ~df["popularity_index"].between(0, 100), df))

    for cols, label in [(["pct_distance", "pct_clinch", "pct_ground"], "range-of-fight shares"),
                        (["pct_head", "pct_body", "pct_leg"], "target shares")]:
        if all(c in df for c in cols):
            total = df[cols].sum(axis=1, min_count=3)
            results.append(_result(f"shares_sum_{cols[0]}", f"{label} sum to 100 (+/-0.5)", "error",
                                   total.notna() & ~np.isclose(total, 100, atol=0.5), df))

    dob = pd.to_datetime(df["dob"], errors="coerce")
    results.append(_result("dob_parses_and_past", "dob parses and is in the past", "error",
                           dob.isna() | (dob >= pd.Timestamp.today()), df))
    first = pd.to_datetime(df["first_ufc_fight"], errors="coerce")
    last = pd.to_datetime(df["last_ufc_fight"], errors="coerce")
    results.append(_result("ufc_dates_ordered", "first_ufc_fight <= last_ufc_fight and both after dob",
                           "error", (first > last) | (first < dob), df))

    finishes = df[["ufc_ko_wins", "ufc_sub_wins", "ufc_dec_wins"]].sum(axis=1)
    results.append(_result("ufc_wins_breakdown", "ko + sub + decision wins <= ufc_wins", "error",
                           finishes > df["ufc_wins"].fillna(0), df))
    results.append(_result("ufc_record_consistent", "ufc_wins + ufc_losses <= ufc_fights", "error",
                           (df["ufc_wins"] + df["ufc_losses"]) > df["ufc_fights"], df))

    # --- warnings: real-world differences between sources or expected gaps -------------------
    results.append(_result("warn_stance_sources_differ",
                           "stance (UFCSTATS) equals stance_project (project Excel); differences kept, "
                           "UFCSTATS stance is used", "warn", df["stance"] != df["stance_project"], df))
    results.append(_result("warn_ufc_fights_gt_record",
                           "ufc_fights <= total_fights (UFC bouts may include draws / no-contests that "
                           "the W+L record excludes)", "warn",
                           df["ufc_fights"].notna() & (df["ufc_fights"] > df["total_fights"]), df))
    results.append(_result("warn_missing_reach", "reach_cm present", "warn",
                           df["reach_cm"].isna(), df))
    results.append(_result("warn_missing_ufc_stats", "UFC career stats (ufc_fights) present", "warn",
                           df["ufc_fights"].isna(), df))
    results.append(_result("warn_small_sample", "total_fights >= 10 so win_rate is not noise", "warn",
                           df["total_fights"] < 10, df))
    return results


def has_errors(results: list[CheckResult]) -> bool:
    return any((not r.passed) and r.severity == "error" for r in results)


def completeness(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column non-null share, only columns with at least one null."""
    out = pd.DataFrame({"missing": df.isna().sum(), "rows": len(df)})
    out["completeness_pct"] = ((1 - out["missing"] / out["rows"]) * 100).round(1)
    return out[out["missing"] > 0].sort_values("missing", ascending=False)
