# Ingestion

Reusable ingestion modules ported from `notebooks/UFC_DATA_SCRAPING.ipynb`. They sit upstream of the existing pipeline: they write raw CSVs under `data/raw/`; the committed files that `pipeline/` reads are unchanged and the pipeline still makes no network calls.

## Status (read first)

- **Parser verified on fixtures only.** The parser unit tests use small hand-written HTML fixtures (`tests/fixtures/`, labelled as not captured pages) that mimic the selectors the notebook uses.
- **Live run attempted on a GitHub runner (4 Oct 2026): blocked by the site.** The manual workflow [`live-ingestion.yml`](../.github/workflows/live-ingestion.yml) fetched `ufcstats.com/statistics/fighters`; `robots.txt` returned 404 (allowed) and the page returned HTTP 200, but the body was a 2,994-character JavaScript "Checking your browser" challenge, not the fighter table, so 0 rows were written. The probe output is in [`LIVE_RUN.md`](LIVE_RUN.md). The module does not try to get around browser checks, so it cannot currently refresh data from this site. The committed dataset was collected earlier by the notebook (see `docs/DATA_DICTIONARY.md` for provenance).
- **Not wired into the normal CI** (it would make CI depend on a third-party site); run it from the Actions tab.
- **Check the site's terms of use before running.** The fetcher reads `robots.txt` and stops if the URL is disallowed, but that is not a substitute for reading the terms.
- **For personal / portfolio use only.** Do not redistribute scraped content.
- Not wired into CI as a live job, and not part of `python -m pipeline`.

## Sources and selectors ported

- Index pages `http://ufcstats.com/statistics/fighters` and `?page=N` for N = 1..5 (the notebook's loop; `--max-pages`). Selector: `table.b-statistics__table`, rows after the header; columns by position: 0 name + link, 3 height, 4 weight, 5 reach, 6 stance, 7 wins, 8 losses, 9 draws; `--` becomes empty.
- Fighter pages for the first 50 rows (`--max-details`): `.b-list__box-list-item` with `.b-list__box-item-title` / `.b-list__box-item-value`; fallback `table.b-list__table` `th`/`td` rows when neither height nor reach was found. Stance is lower-cased.
- Not ported because the notebook does not contain it: Tapology, Sherdog, any `?char=` / `page=all` index (an example in the README shows one, but the notebook code does not use it). The notebook treats column 0 as the full name; that is kept as-is and not checked against the live page.
- Not ingestion, so not ported: unit conversion, stance/handedness mapping, win rate. Those remain in the cleaning code downstream.

## Design

| Concern | Where | How |
|---|---|---|
| Fetching | `ingestion/fetch.py` | `PoliteFetcher.get_html(url)` |
| Parsing (pure) | `ingestion/ufcstats.py` | `parse_fighter_list(html)`, `parse_fighter_detail(html)` |
| Orchestration + CLI | `ingestion/ufcstats.py` | `scrape(...)`, `python -m ingestion.ufcstats` |
| robots.txt | `ingestion/fetch.py` | `urllib.robotparser`; 404 = allowed, 401/403 or unreachable/5xx = treated as disallowed; `RobotsDisallowed` aborts the run (CLI exit code 3, nothing written) |
| Identifying User-Agent | `ingestion/fetch.py`, module constant | Names the project and repo; override with `--user-agent` |
| Rate limit | `PoliteFetcher` | `min_interval` must be >= 1 s (enforced); also applies to robots.txt requests |
| Retries | `PoliteFetcher` | Network errors and HTTP 429/500/502/503/504; exponential backoff (2 s, 4 s, ...), honours numeric `Retry-After` |
| Raw HTML cache | `data/raw_html/` (git-ignored) | One file per URL (SHA-256 of the URL); a cache hit makes no request |
| Output | `data/raw/ufcstats_fighters.csv` (`--out`) | CSV with `scraped_at` (UTC ISO) and `source_url` |
| Logging | `logging` | INFO by default, `-v` for debug |

## Tests (offline)

- `tests/test_ingestion_fetch.py`: robots allow/disallow/404/403/unreachable, one robots fetch per host, User-Agent header, rate-limit spacing, retry/backoff/give-up, `Retry-After`, cache. HTTP is mocked with a fake session and a fake clock, so the tests neither sleep nor use the network.
- `tests/test_ingestion_*.py` (module tests): parsers on hand-written fixtures in `tests/fixtures/` (see its README: minimal, written to match the notebook's selectors, **not captured pages**), plus the assembly step with a stub fetcher and the CLI's robots abort.

These tests show the code does what it says on markup written to match the notebook. They say nothing about whether the live sites still serve that markup.
