# Skills demonstrated

Each skill below points to files in this repository that you can open and run.

## Data engineering

| Skill | Where to see it |
|---|---|
| ETL pipeline with separated stages (extract, validate, transform, load) | `pipeline/extract.py`, `pipeline/validate.py`, `pipeline/transform.py`, `pipeline/load.py`, `pipeline/run.py` |
| Data-quality checks with a generated report | `pipeline/validate.py` (38 checks, errors vs warnings), `pipeline/report.py`, `docs/DATA_QUALITY.md` |
| Dimensional modelling (star schema, grain, surrogate and business keys) | `pipeline/schema.sql`, `pipeline/transform.py`, `docs/DATA_MODEL.md` |
| SQL DDL: constraints, foreign keys, indexes, views | `pipeline/schema.sql` |
| Idempotent, transactional load with audit table and FK check | `pipeline/load.py` |
| Reuse over duplication (shared name normalisation) | `pipeline/transform.py` imports `norm()` from `scripts/build_clean_dataset.py` |
| Reproducible dataset build from source files | `scripts/build_clean_dataset.py`, `scripts/enrich_dataset.py` |
| Excluding synthetic columns from the analytical store | `pipeline/config.py` (`EXCLUDED_ESTIMATED_COLUMNS`), `docs/DATA_MODEL.md` |
| Data documentation and provenance | `docs/DATA_DICTIONARY.md`, `data/data_dictionary.csv` |
| Web scraping with `requests` and BeautifulSoup | `notebooks/UFC_DATA_SCRAPING.ipynb` (documented, not re-run here; see provenance notes in `docs/DATA_DICTIONARY.md`) |

## Data analysis

| Skill | Where to see it |
|---|---|
| Analytical SQL: CTEs, window functions (`RANK`, `ROW_NUMBER`, `LAG`, running totals), joins, `CASE`, `HAVING` | `sql/analysis/` (10 queries), `sql/README.md` |
| Reproducible query runner writing versioned outputs | `sql/run_queries.py`, `docs/query_results/` |
| Statistics: t-tests, Cohen's d, bootstrap intervals, power / required sample size | `ufc_core.py` (`cohens_d`, `bootstrap_diff_ci`, `required_n_per_group`, `compare_groups`), `sql/analysis/03_southpaw_right_vs_orthodox_right.sql` |
| Exploratory analysis and visualisation notebooks | `notebooks/UFC_Visualization.ipynb`, `notebooks/UFC_DATA_CLEANING_PROCESSING.ipynb` |
| Feature engineering (style indices, ape index, popularity index) | `scripts/build_clean_dataset.py`, `scripts/enrich_dataset.py` |
| Interactive app: nearest-neighbour fighter matching, Streamlit pages | `ufc_intelligence_app.py`, `ufc_core.py`, `views/` |
| Honest reporting of limits (small n, curated sample, source disagreements) | `docs/DATA_QUALITY.md`, `docs/DATA_DICTIONARY.md` (Known data caveats), README "Limitations" |

## Engineering practice

| Skill | Where to see it |
|---|---|
| Automated tests (pytest): pipeline, SQL results cross-checked against pandas, docs in sync | `tests/test_pipeline.py`, `tests/test_sql_analysis.py`, `tests/test_docs.py`, `tests/test_core.py`, `tests/test_pages.py` |
| Reusable, polite web ingestion: `robots.txt` check, identifying User-Agent, rate limiting, retries with backoff, on-disk HTML cache, pure parsers separated from fetching, CSV with timestamp and source URL. Parsers verified on hand-written fixtures; live run not verified in CI | `ingestion/fetch.py`, `ingestion/ufcstats.py`, `docs/INGESTION.md` |
| Offline tests for network code (mocked HTTP, fake clock, fixtures) | `tests/test_ingestion_fetch.py`, `tests/test_ingestion_ufcstats.py`, `tests/fixtures/` |
| Continuous integration | `.github/workflows/ci.yml` |
| Dependency management | `requirements.txt`, `requirements-dev.txt` |
| Version control hygiene (build artefacts git-ignored) | `.gitignore` (`warehouse.db`) |
