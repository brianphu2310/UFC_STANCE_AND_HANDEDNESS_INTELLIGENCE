"""Run with:  pytest -q"""
import numpy as np
import pandas as pd
import pytest

import ufc_core as core


@pytest.fixture(scope="module")
def df():
    return core.load_fighters()


# --- data quality -----------------------------------------------------------
def test_row_count_and_unique_names(df):
    assert len(df) == 117
    assert df["fighter"].is_unique


def test_no_nulls_in_critical_columns(df):
    cols = ["fighter", "stance", "hand", "foot", "wins", "losses", "win_rate", "weight_class",
            "height_cm", "fighting_style", "popularity_index"]
    assert df[cols].notna().all().all()


def test_categorical_values(df):
    assert set(df["stance"]) <= {"Orthodox", "Southpaw", "Switch"}
    assert set(df["hand"]) <= {"Right", "Left"}
    assert set(df["foot"]) <= {"Right", "Left"}
    assert set(df["weight_class"]) <= set(core.DIVISION_LIMIT_KG)
    for label, (col, order) in core.GROUP_DIMS.items():
        assert set(df[col]) <= set(order), label


def test_win_rate_matches_record(df):
    expected = (df["wins"] / (df["wins"] + df["losses"]) * 100).round(2)
    assert np.allclose(df["win_rate"], expected)


def test_physical_ranges(df):
    assert df["height_cm"].between(150, 215).all()
    assert df["reach_cm"].dropna().between(150, 225).all()
    assert df["popularity_index"].between(0, 100).all()
    assert df["str_acc"].dropna().between(0, 100).all()


def test_every_column_is_documented():
    dic = pd.read_csv(core.DATA_DIR / "data_dictionary.csv")
    assert set(dic["source"]) <= {"scraped", "derived", "curated", "estimated"}
    assert (dic["source"] == "estimated").sum() == 1  # only dominant foot is generated


# --- statistics -------------------------------------------------------------
def test_cohens_d_known_value():
    a = np.array([1, 2, 3, 4, 5], float)
    assert core.cohens_d(a + 1, a) == pytest.approx(1 / np.std(a, ddof=1))


def test_compare_groups(df):
    sp = df["stance"] == "Southpaw"
    c = core.compare_groups(df, sp, ~sp, "Southpaw", "Other")
    assert c.ci_low <= c.diff <= c.ci_high
    assert 0 <= c.welch_p <= 1 and 0 <= c.mwu_p <= 1
    assert c.n_a + c.n_b == len(df)


def test_required_n():
    assert core.required_n_per_group(0.8) < core.required_n_per_group(0.2)
    assert 60 <= core.required_n_per_group(0.5) <= 66


def test_strengths_are_real_numbers(df):
    lines = core.strengths(df, "Khabib Nurmagomedov", top=3)
    assert len(lines) == 3 and all("top" in x for x in lines)


# --- build your fighter -----------------------------------------------------
def test_division_for_weight():
    assert core.division_for_weight(69) == "Lightweight"
    assert core.division_for_weight(200) == "Heavyweight"
    assert core.division_for_weight(52, "Women") == "Women's Strawweight"


@pytest.mark.parametrize("hand,foot,style,expected", [
    ("Right", "Right", "Striker", "Orthodox"),
    ("Left", "Left", "Striker", "Southpaw"),
    ("Right", "Left", "Grappler", "Orthodox"),   # dominant left leg leads the shot
    ("Right", "Left", "All-rounder", "Southpaw"),  # dominant left leg at the back to kick
])
def test_recommend_stance(hand, foot, style, expected):
    assert core.recommend_stance(hand, foot, style)["recommended"] == expected


def test_model_fighters(df):
    top = core.model_fighters(df, height_cm=179, reach_cm=181, weight_kg=69, stance="Southpaw",
                              hand="Right", foot="Right", style="Striker", gender="Men",
                              goal="Amateur competition", n=5)
    assert len(top) == 5 and (top["gender"] == "Men").all()
    parts = top[["s_body", "s_stance", "s_hand", "s_foot", "s_style", "s_quality"]].sum(axis=1)
    assert np.allclose(parts, top["match_score"])
    assert top["match_score"].is_monotonic_decreasing
    assert top["match_score"].between(0, 100).all()


def test_roadmap_scales_with_frequency_and_goal():
    kw = dict(style="Striker", stance="Orthodox", hand="Right", foot="Right", level="Beginner")
    slow = core.roadmap(sessions=2, goal="Pro debut", **kw)["end_month"].max()
    fast = core.roadmap(sessions=6, goal="Pro debut", **kw)["end_month"].max()
    short = core.roadmap(sessions=4, goal="Fitness & self-defence", **kw)["end_month"].max()
    assert slow > fast > short


@pytest.mark.parametrize("sessions", range(1, 8))
def test_weekly_mix_has_one_class_per_session(sessions):
    for phase in range(4):
        week = core.weekly_mix("All-rounder", sessions, phase, "Pro debut", "Southpaw")
        assert len(week) == sessions


def test_catalogues_and_coaches():
    coaches = core.pick_coaches(core.load_catalogue("coaches"), style="Grappler",
                                stance="Southpaw", hand="Right", goal="Amateur competition")
    assert coaches.iloc[0]["discipline"] in {"BJJ", "Wrestling", "No-Gi / Sambo"}
    sched = core.schedule(["A", "B", "C"])
    assert (sched["Session"] != "Rest").sum() == 3


def test_matchup_notes_geometry():
    assert core.matchup_notes("Orthodox", "Right")["geometry"].startswith("Open")
    assert core.matchup_notes("Southpaw", "Left")["geometry"].startswith("Closed")


def test_globe_payload(df):
    import globe3d
    rows = globe3d.country_payload(df)
    assert sum(r["count"] for r in rows) == len(df)          # every fighter lands on the globe
    assert all(-90 <= r["lat"] <= 90 and -180 <= r["lon"] <= 180 for r in rows)
    usa = next(r for r in rows if r["iso3"] == "USA")
    assert usa["fighters"][0] == df[df["country"] == "USA"].sort_values(
        "popularity_index", ascending=False)["fighter"].iloc[0]
