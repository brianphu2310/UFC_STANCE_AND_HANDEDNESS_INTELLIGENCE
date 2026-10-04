"""UFCStats fighter ingestion, ported from notebooks/UFC_DATA_SCRAPING.ipynb.

Only what the notebook uses is ported:
  * index pages  http://ufcstats.com/statistics/fighters[?page=N]  (N = 1..5), the
    ``table.b-statistics__table`` rows, columns 0 (name + link), 3 height, 4 weight, 5 reach,
    6 stance, 7 wins, 8 losses, 9 draws;
  * the first 50 fighter pages: ``.b-list__box-list-item`` with ``.b-list__box-item-title`` /
    ``.b-list__box-item-value``, falling back to ``table.b-list__table`` th/td rows.
The notebook's cleaning (unit conversion, stance/handedness, win rate) is NOT part of ingestion;
this module writes the raw strings, and the existing cleaning/pipeline code stays downstream.

Usage:  python -m ingestion.ufcstats --out data/raw/ufcstats_fighters.csv

Personal / portfolio use only. Check UFCStats' terms of use before running a live fetch.
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from .fetch import FetchError, PoliteFetcher, RobotsDisallowed

log = logging.getLogger("ingestion.ufcstats")

BASE_URL = "http://ufcstats.com/statistics/fighters"  # as in the notebook
USER_AGENT = (
    "ufc-stance-portfolio-ingest/0.1 (personal portfolio project; "
    "https://github.com/brianphu2310/ufc_stance_and_handedness_intelligence)"
)
FIELDS = [
    "fighter_name", "detail_url", "height_raw", "weight_raw", "reach_raw", "stance_raw",
    "wins", "losses", "draws", "height_tott", "reach_tott", "stance_tott",
    "source_url", "scraped_at",
]


# ---- pure parsers --------------------------------------------------------------------------
def _none_if_dash(value: str | None) -> str | None:
    return None if value == "--" else value


def parse_fighter_list(html: str) -> list[dict]:
    """Rows of ``table.b-statistics__table``; [] if the table is missing. Pure function."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="b-statistics__table")
    if not table:
        return []
    out = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        link = cols[0].find("a")

        def cell(i, default=None):
            return cols[i].get_text(strip=True) if len(cols) > i else default

        out.append({
            "fighter_name": cols[0].get_text(strip=True),
            "detail_url": link["href"] if link and link.has_attr("href") else None,
            "height_raw": _none_if_dash(cell(3)),
            "weight_raw": _none_if_dash(cell(4)),
            "reach_raw": _none_if_dash(cell(5)),
            "stance_raw": _none_if_dash(cell(6)),
            "wins": cell(7, "0"),
            "losses": cell(8, "0"),
            "draws": cell(9, "0"),
        })
    return out


def _assign(details: dict, label: str, value: str) -> None:
    label = label.lower()
    if "height" in label:
        details["height"] = value
    elif "reach" in label:
        details["reach"] = value
    elif "stance" in label:
        details["stance"] = value.lower()


def parse_fighter_detail(html: str) -> dict:
    """Height / reach / stance from a fighter page (tale of the tape). Pure function."""
    soup = BeautifulSoup(html, "html.parser")
    details = {"height": None, "reach": None, "stance": None}
    for item in soup.select(".b-list__box-list-item"):
        label = item.select_one(".b-list__box-item-title")
        value = item.select_one(".b-list__box-item-value")
        if label and value:
            _assign(details, label.get_text(strip=True), value.get_text(strip=True))
    if not details["height"] and not details["reach"]:  # notebook's fallback
        for table in soup.find_all("table", class_="b-list__table"):
            for row in table.find_all("tr"):
                th, td = row.find("th"), row.find("td")
                if th and td:
                    _assign(details, th.get_text(strip=True), td.get_text(strip=True))
    return details


# ---- fetch + assemble ----------------------------------------------------------------------
def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def scrape(fetcher: PoliteFetcher, max_pages: int = 5, max_details: int = 50) -> list[dict]:
    """Index pages 1..max_pages, then detail pages for the first max_details fighters.

    RobotsDisallowed propagates (the caller aborts). Other fetch errors end paging (index) or
    leave the detail fields empty (detail), like the notebook's try/except.
    """
    rows: list[dict] = []
    for page in range(1, max_pages + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
        try:
            parsed = parse_fighter_list(fetcher.get_html(url))
        except RobotsDisallowed:
            raise
        except FetchError as exc:
            log.error("index page %d failed: %s", page, exc)
            break
        if not parsed:
            log.warning("no fighter table on page %d; stopping", page)
            break
        stamp = _now()
        for r in parsed:
            r.update(source_url=url, scraped_at=stamp)
        rows.extend(parsed)
        log.info("page %d: %d fighters", page, len(parsed))

    for i, r in enumerate(rows[:max_details]):
        if not r["detail_url"]:
            continue
        try:
            d = parse_fighter_detail(fetcher.get_html(r["detail_url"]))
        except RobotsDisallowed:
            raise
        except FetchError as exc:
            log.warning("detail page failed for %s: %s", r["detail_url"], exc)
            continue
        r.update(height_tott=d["height"], reach_tott=d["reach"], stance_tott=d["stance"],
                 source_url=r["detail_url"], scraped_at=_now())
    return rows


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="data/raw/ufcstats_fighters.csv", type=Path)
    ap.add_argument("--cache-dir", default="data/raw_html", type=Path)
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--max-details", type=int, default=50)
    ap.add_argument("--min-interval", type=float, default=1.5, help="seconds between requests (>= 1)")
    ap.add_argument("--user-agent", default=USER_AGENT)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    fetcher = PoliteFetcher(args.user_agent, args.cache_dir, args.min_interval)
    try:
        rows = scrape(fetcher, args.max_pages, args.max_details)
    except RobotsDisallowed as exc:
        log.error("%s. Not fetching; nothing written.", exc)
        return 3
    if not rows:
        log.error("no rows scraped; nothing written")
        return 1
    write_csv(rows, args.out)
    log.info("wrote %d rows to %s", len(rows), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
