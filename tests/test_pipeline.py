"""Tests for the extract -> validate -> transform -> load pipeline."""
import sqlite3

import pandas as pd
import pytest

from pipeline import report
from pipeline.config import SCHEMA_SQL, SOURCE_CSV
from pipeline.extract import extract
from pipeline.load import LOAD_ORDER, load
from pipeline.run import run
from pipeline.transform import transform
from pipeline.validate import completeness, has_errors, validate


@pytest.fixture(scope="module")
def src():
    return extract()


@pytest.fixture(scope="module")
def tables(src):
    return transform(src)


@pytest.fixture(scope="module")
def db(tables, tmp_path_factory):
    path = tmp_path_factory.mktemp("wh") / "warehouse.db"
    load(tables, path)
    return path


def failed(results, name):
    return next(r for r in results if r.name == name).failed


# --- extract ------------------------------------------------------------------------------------
def test_extract_reads_all_rows(src):
    assert len(src) == 117 and src["fighter"].is_unique


def test_extract_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract(tmp_path / "nope.csv")


# --- validate -----------------------------------------------------------------------------------
def test_real_data_has_no_blocking_errors(src):
    assert not has_errors(validate(src))


def test_validate_flags_duplicate_fighter(src):
    bad = pd.concat([src, src.iloc[[0]]], ignore_index=True)
    assert failed(validate(bad), "unique_fighter") == 2


def test_validate_flags_wrong_win_rate(src):
    bad = src.copy()
    bad.loc[0, "win_rate"] = bad.loc[0, "win_rate"] + 5
    res = validate(bad)
    assert failed(res, "win_rate_formula") == 1 and has_errors(res)


def test_validate_flags_bad_domain_and_range(src):
    bad = src.copy()
    bad.loc[1, "stance"] = "Sideways"
    bad.loc[2, "height_cm"] = 50
    bad.loc[3, "str_acc"] = 140
    res = validate(bad)
    assert failed(res, "domain_stance") == 1
    assert failed(res, "range_height_cm") == 1
    assert failed(res, "range_str_acc") == 1


def test_validate_flags_null_and_total_mismatch(src):
    bad = src.copy()
    bad.loc[4, "country"] = None
    bad.loc[5, "total_fights"] = bad.loc[5, "total_fights"] + 1
    res = validate(bad)
    assert failed(res, "not_null_core") == 1
    assert failed(res, "total_fights_sum") == 1


def test_validate_reports_missing_columns_without_crashing(src):
    res = validate(src.drop(columns=["win_rate"]))
    assert has_errors(res) and failed(res, "required_columns") == 1


def test_warnings_do_not_block(src):
    res = validate(src)
    assert any(r.severity == "warn" and not r.passed for r in res)
    assert not has_errors(res)


def test_completeness_lists_only_columns_with_nulls(src):
    comp = completeness(src)
    assert (comp["missing"] > 0).all() and "fighter" not in comp.index


def test_report_is_deterministic_and_mentions_checks(src):
    text = report.render(src, validate(src))
    assert text == report.render(src, validate(src))
    assert "win_rate_formula" in text and "load allowed" in text


def test_committed_quality_report_is_current(src):
    committed = (SOURCE_CSV.parents[1] / "docs" / "DATA_QUALITY.md").read_text(encoding="utf-8")
    assert committed == report.render(src, validate(src)), "re-run: python -m pipeline.run"


# --- transform ----------------------------------------------------------------------------------
def test_expected_tables_and_row_counts(tables, src):
    assert set(tables) == set(LOAD_ORDER)
    assert len(tables["dim_fighter"]) == len(tables["fact_fighter_record"]) == len(src)
    assert len(tables["fact_ufc_performance"]) == src["ufc_fights"].notna().sum()


def test_surrogate_keys_are_unique_and_dense(tables):
    for name, key in [("dim_fighter", "fighter_key"), ("dim_stance", "stance_key"),
                      ("dim_handedness", "hand_key"), ("dim_weight_class", "weight_class_key"),
                      ("dim_country", "country_key"), ("dim_fighting_style", "style_key")]:
        k = tables[name][key]
        assert k.is_unique and list(k) == list(range(1, len(k) + 1)), name


def test_fact_keys_resolve_to_dimensions(tables):
    f = tables["fact_fighter_record"]
    for key, dim in [("stance_key", "dim_stance"), ("hand_key", "dim_handedness"),
                     ("weight_class_key", "dim_weight_class"), ("country_key", "dim_country"),
                     ("style_key", "dim_fighting_style"), ("fighter_key", "dim_fighter")]:
        assert f[key].notna().all() and f[key].isin(tables[dim][key]).all(), key
    assert tables["fact_ufc_performance"]["fighter_key"].isin(tables["dim_fighter"]["fighter_key"]).all()


def test_estimated_foot_is_not_loaded(tables):
    for df in tables.values():
        assert not any("foot" in c for c in df.columns)


def test_transform_is_deterministic(src, tables):
    again = transform(src)
    for name in tables:
        pd.testing.assert_frame_equal(tables[name], again[name])


def test_transform_preserves_values(src, tables):
    prof = tables["fact_fighter_record"].merge(tables["dim_fighter"], on="fighter_key")
    merged = prof.merge(src, left_on="fighter_name", right_on="fighter")
    assert (merged["win_rate_x"] == merged["win_rate_y"]).all()
    assert (merged["wins_x"] == merged["wins_y"]).all()


# --- load ---------------------------------------------------------------------------------------
def test_load_creates_tables_indexes_and_view(db):
    conn = sqlite3.connect(db)
    objs = dict(conn.execute("SELECT name, type FROM sqlite_master").fetchall())
    assert all(objs.get(t) == "table" for t in LOAD_ORDER + ["etl_load_audit"])
    assert objs["vw_fighter_profile"] == "view"
    assert sum(1 for t in objs.values() if t == "index") >= 8  # explicit ix_* indexes
    conn.close()


def test_load_row_counts_match_audit(db, tables):
    conn = sqlite3.connect(db)
    for name in LOAD_ORDER:
        n = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        audited = conn.execute("SELECT row_count FROM etl_load_audit WHERE table_name=?", (name,)).fetchone()[0]
        assert n == audited == len(tables[name]), name
    conn.close()


def test_foreign_keys_hold_and_are_enforced(db):
    conn = sqlite3.connect(db)
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.execute("PRAGMA foreign_keys = ON")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO fact_ufc_performance(fighter_key, ufc_fights, ufc_wins, ufc_losses,"
                     " ufc_ko_wins, ufc_sub_wins, ufc_dec_wins) VALUES (9999,1,1,0,0,0,1)")
    conn.close()


def test_check_constraints_reject_bad_rows(db):
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE fact_fighter_record SET win_rate = 150 WHERE fighter_key = 1")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO dim_stance(stance_key, stance) VALUES (99, 'Sideways')")
    conn.close()


def test_reload_is_idempotent(tables, tmp_path):
    path = tmp_path / "w.db"
    load(tables, path)
    load(tables, path)
    conn = sqlite3.connect(path)
    assert conn.execute("SELECT COUNT(*) FROM dim_fighter").fetchone()[0] == 117
    conn.close()


def test_run_blocks_load_on_validation_error(src, tmp_path):
    bad = src.copy()
    bad.loc[0, "win_rate"] = 1.0
    bad_csv = tmp_path / "bad.csv"
    bad.to_csv(bad_csv, index=False)
    db_path = tmp_path / "w.db"
    assert run(bad_csv, db_path, write_report=False) == 1
    assert not db_path.exists()


def test_run_end_to_end(tmp_path):
    db_path = tmp_path / "w.db"
    assert run(SOURCE_CSV, db_path, write_report=False) == 0 and db_path.exists()


def test_schema_file_lists_every_table_documented():
    ddl = SCHEMA_SQL.read_text()
    doc = (SOURCE_CSV.parents[1] / "docs" / "DATA_MODEL.md").read_text()
    for t in LOAD_ORDER + ["etl_load_audit", "vw_fighter_profile"]:
        assert t in ddl and t in doc, t
