"""Tests for sql/analysis/*.sql and sql/run_queries.py."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from pipeline.config import SOURCE_CSV
from pipeline.extract import extract
from pipeline.load import load
from pipeline.transform import transform

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_queries", ROOT / "sql" / "run_queries.py")
rq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rq)


@pytest.fixture(scope="module")
def src():
    return extract()


@pytest.fixture(scope="module")
def results(src, tmp_path_factory):
    base = tmp_path_factory.mktemp("sql")
    db = base / "w.db"
    load(transform(src), db)
    return rq.run_all(db, base / "out")


def test_between_6_and_10_queries_all_return_rows(results):
    assert 6 <= len(results) <= 10
    assert all(len(df) > 0 for df in results.values())


def test_each_query_uses_cte_or_window_or_case():
    for f in (ROOT / "sql" / "analysis").glob("*.sql"):
        text = f.read_text().upper()
        assert any(k in text for k in ("WITH ", " OVER (", "CASE ")), f.name


def test_stance_counts_match_pandas(results, src):
    q = results["01_win_rate_by_stance"].set_index("stance")
    assert q["fighters"].to_dict() == src["stance"].value_counts().to_dict()
    for stance, mean in src.groupby("stance")["win_rate"].mean().items():
        assert q.loc[stance, "mean_win_rate"] == pytest.approx(mean, abs=0.006)


def test_matrix_counts_sum_to_total(results, src):
    m = results["02_stance_handedness_matrix"]
    assert m["fighters"].sum() == len(src)
    assert m["pct_of_fighters"].sum() == pytest.approx(100, abs=0.5)


def test_effect_size_matches_python(results, src):
    r = results["03_southpaw_right_vs_orthodox_right"].iloc[0]
    a = src[(src.stance == "Southpaw") & (src.hand == "Right")]["win_rate"]
    b = src[(src.stance == "Orthodox") & (src.hand == "Right")]["win_rate"]
    pooled = (((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2)) ** 0.5
    assert r["southpaw_right_n"] == len(a) and r["orthodox_right_n"] == len(b)
    assert r["cohens_d"] == pytest.approx((a.mean() - b.mean()) / pooled, abs=0.006)


def test_top_fighters_ranks_are_at_most_three_and_ordered(results):
    t = results["05_top_fighters_by_division"]
    assert t["division_rank"].between(1, 3).all()
    for _, g in t.groupby("weight_class"):
        assert g["win_rate"].is_monotonic_decreasing


def test_finish_shares_sum_to_100(results):
    f = results["07_finish_methods_by_style"]
    assert (f[["ko_pct", "sub_pct", "decision_pct", "other_pct"]].sum(axis=1) - 100).abs().max() < 0.3


def test_cumulative_window_ends_at_stance_total(results, src):
    e = results["08_experience_bands"]
    last = e.groupby("stance")["cumulative_fighters"].max()
    assert last.to_dict() == src["stance"].value_counts().to_dict()


def test_committed_outputs_match_regenerated(results):
    out_dir = ROOT / "docs" / "query_results"
    for name, df in results.items():
        committed = pd.read_csv(out_dir / f"{name}.csv")
        pd.testing.assert_frame_equal(committed, pd.read_csv(pd.io.common.StringIO(df.to_csv(index=False))),
                                      check_exact=False, atol=0.011)
