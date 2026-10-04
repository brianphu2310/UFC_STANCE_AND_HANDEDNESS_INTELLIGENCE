"""Transform: reshape the flat CSV into dimension and fact tables with surrogate keys.

Reuses ``scripts/build_clean_dataset.norm`` for name normalisation rather than re-implementing it.
"""
from __future__ import annotations

import pandas as pd

from scripts.build_clean_dataset import norm
from .config import EXCLUDED_ESTIMATED_COLUMNS

INT_COLS_PERF = ["ufc_fights", "ufc_wins", "ufc_losses", "ufc_ko_wins", "ufc_sub_wins",
                 "ufc_dec_wins", "title_fights", "main_events", "stats_fights"]


def _dim(df: pd.DataFrame, key: str, cols: list[str]) -> pd.DataFrame:
    """Distinct combinations of ``cols`` sorted for stable surrogate keys (1..n)."""
    d = df[cols].drop_duplicates().sort_values(cols).reset_index(drop=True)
    d.insert(0, key, range(1, len(d) + 1))
    return d


def transform(src: pd.DataFrame) -> dict[str, pd.DataFrame]:
    df = src.drop(columns=[c for c in EXCLUDED_ESTIMATED_COLUMNS if c in src.columns]).copy()
    for c in ("fighter", "country", "continent", "weight_class"):
        df[c] = df[c].astype(str).str.strip()
    # Order fighters by normalised name so fighter_key does not depend on accents/case.
    df["_norm"] = df["fighter"].map(norm)
    df = df.sort_values(["_norm", "fighter"]).reset_index(drop=True)

    dim_stance = _dim(df, "stance_key", ["stance"])
    dim_hand = _dim(df, "hand_key", ["hand"])
    dim_weight = _dim(df, "weight_class_key", ["weight_class", "gender"])
    dim_country = _dim(df, "country_key", ["country", "continent"])
    dim_style = _dim(df, "style_key", ["fighting_style"])

    dim_fighter = pd.DataFrame({
        "fighter_key": range(1, len(df) + 1),
        "fighter_name": df["fighter"],
        "gender": df["gender"],
        "dob": pd.to_datetime(df["dob"]).dt.strftime("%Y-%m-%d"),
        "ufcstats_url": df["ufcstats_url"],
        "is_champion": df["champion"].astype(int),
        "is_active": df["active"].map({True: 1, False: 0}).astype("Int64"),
        "stance_project": df["stance_project"],
        "weight_class_source": df["weight_class_source"],
        "learning_tip": df["learning_tip"],
    })
    keyed = df.assign(fighter_key=dim_fighter["fighter_key"])
    for dim, on in [(dim_stance, ["stance"]), (dim_hand, ["hand"]),
                    (dim_weight, ["weight_class", "gender"]), (dim_country, ["country", "continent"]),
                    (dim_style, ["fighting_style"])]:
        keyed = keyed.merge(dim, on=on, how="left", validate="m:1")
    keyed = keyed.sort_values("fighter_key").reset_index(drop=True)

    fact_record = keyed[["fighter_key", "stance_key", "hand_key", "weight_class_key", "country_key",
                         "style_key", "wins", "losses", "total_fights", "win_rate", "height_cm",
                         "reach_cm", "ape_index_cm", "age", "popularity_index"]].rename(
        columns={"age": "age_years"})

    perf_cols = ["fighter_key"] + INT_COLS_PERF + [
        "first_ufc_fight", "last_ufc_fight", "ufc_minutes", "slpm", "str_acc", "sapm", "str_def",
        "td_avg", "td_acc", "td_def", "sub_avg", "kd_avg", "ctrl_pct", "pct_distance", "pct_clinch",
        "pct_ground", "pct_head", "pct_body", "pct_leg", "striking_index", "grappling_index"]
    fact_perf = keyed.loc[keyed["ufc_fights"].notna(), perf_cols].copy()
    for c in INT_COLS_PERF:
        fact_perf[c] = fact_perf[c].astype("Int64")
    fact_perf = fact_perf.reset_index(drop=True)

    return {
        "dim_stance": dim_stance, "dim_handedness": dim_hand, "dim_weight_class": dim_weight,
        "dim_country": dim_country, "dim_fighting_style": dim_style, "dim_fighter": dim_fighter,
        "fact_fighter_record": fact_record, "fact_ufc_performance": fact_perf,
    }
