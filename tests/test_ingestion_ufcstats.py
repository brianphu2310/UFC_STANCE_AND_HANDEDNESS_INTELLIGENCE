"""UFCStats ingestion: parsers on hand-written fixtures (tests/fixtures/README.md) + mocked scrape."""
import csv
from pathlib import Path

from ingestion import ufcstats
from ingestion.fetch import FetchError, RobotsDisallowed

FX = Path(__file__).parent / "fixtures"


def fx(name):
    return (FX / name).read_text(encoding="utf-8")


def test_parse_fighter_list_columns_and_dash_handling():
    rows = ufcstats.parse_fighter_list(fx("ufcstats_list_page.html"))
    assert [r["fighter_name"] for r in rows] == ["Test Alpha", "Test Bravo", "No Link Charlie"]  # short row skipped
    a, b, c = rows
    assert a["detail_url"] == "http://ufcstats.com/fighter-details/aaa111"
    assert (a["height_raw"], a["weight_raw"], a["reach_raw"], a["stance_raw"]) == ("5' 11\"", "170 lbs.", '72"', "Orthodox")
    assert (a["wins"], a["losses"], a["draws"]) == ("10", "2", "0")
    assert (b["height_raw"], b["reach_raw"], b["stance_raw"]) == (None, None, None)  # '--' -> None
    assert c["detail_url"] is None


def test_parse_fighter_list_without_table_is_empty():
    assert ufcstats.parse_fighter_list(fx("ufcstats_list_page_no_table.html")) == []


def test_parse_fighter_detail_primary_selectors():
    assert ufcstats.parse_fighter_detail(fx("ufcstats_fighter_detail.html")) == {
        "height": "5' 11\"", "reach": '72"', "stance": "southpaw"}


def test_parse_fighter_detail_table_fallback():
    assert ufcstats.parse_fighter_detail(fx("ufcstats_fighter_detail_table_fallback.html")) == {
        "height": "6' 2\"", "reach": '77"', "stance": "switch"}


def test_parse_fighter_detail_empty_page():
    assert ufcstats.parse_fighter_detail("<html></html>") == {"height": None, "reach": None, "stance": None}


class StubFetcher:
    def __init__(self, pages, errors=None):
        self.pages, self.errors, self.requested = pages, errors or {}, []

    def get_html(self, url):
        self.requested.append(url)
        if url in self.errors:
            raise self.errors[url]
        return self.pages[url]


def _pages():
    return {
        ufcstats.BASE_URL: fx("ufcstats_list_page.html"),
        ufcstats.BASE_URL + "?page=2": fx("ufcstats_list_page_no_table.html"),
        "http://ufcstats.com/fighter-details/aaa111": fx("ufcstats_fighter_detail.html"),
        "http://ufcstats.com/fighter-details/bbb222": fx("ufcstats_fighter_detail_table_fallback.html"),
    }


def test_scrape_assembles_rows_stops_on_missing_table_and_adds_provenance():
    f = StubFetcher(_pages())
    rows = ufcstats.scrape(f, max_pages=5, max_details=50)
    assert f.requested[:2] == [ufcstats.BASE_URL, ufcstats.BASE_URL + "?page=2"]  # stopped after page 2
    assert len(rows) == 3
    a, b, c = rows
    assert a["stance_tott"] == "southpaw" and a["source_url"] == a["detail_url"]
    assert b["height_tott"] == "6' 2\""
    assert c["source_url"] == ufcstats.BASE_URL and c.get("stance_tott") is None
    assert all(r["scraped_at"].endswith("+00:00") for r in rows)


def test_scrape_detail_failure_is_tolerated_but_robots_aborts():
    pages = _pages()
    f = StubFetcher(pages, {"http://ufcstats.com/fighter-details/aaa111": FetchError("boom")})
    rows = ufcstats.scrape(f)
    assert rows[0].get("height_tott") is None and rows[1]["stance_tott"] == "switch"

    f = StubFetcher(pages, {"http://ufcstats.com/fighter-details/aaa111": RobotsDisallowed("no")})
    try:
        ufcstats.scrape(f)
        raise AssertionError("expected RobotsDisallowed")
    except RobotsDisallowed:
        pass


def test_write_csv_has_timestamp_and_source_url(tmp_path):
    rows = ufcstats.scrape(StubFetcher(_pages()))
    out = tmp_path / "raw" / "f.csv"
    ufcstats.write_csv(rows, out)
    got = list(csv.DictReader(out.open(encoding="utf-8")))
    assert list(got[0].keys()) == ufcstats.FIELDS
    assert "source_url" in got[0] and got[0]["scraped_at"]


def test_cli_exits_3_and_writes_nothing_when_robots_disallows(tmp_path, monkeypatch):
    def deny(self, url):
        raise RobotsDisallowed("robots.txt disallows")

    monkeypatch.setattr("ingestion.fetch.PoliteFetcher.get_html", deny)
    out = tmp_path / "o.csv"
    assert ufcstats.main(["--out", str(out), "--cache-dir", str(tmp_path / "c")]) == 3
    assert not out.exists()
