# SQL analysis

Ten analytical queries over `warehouse.db` (SQLite). Build the warehouse with
`python -m pipeline.run`, then run `python sql/run_queries.py`; each query's result is written to
`docs/query_results/<query>.csv` and committed so results can be read without running anything.

| Query | Question | Techniques |
|---|---|---|
| `01_win_rate_by_stance.sql` | Does stance alone separate win rates? | CTE, `SUM() OVER ()`, CASE |
| `02_stance_handedness_matrix.sql` | Stance x handedness cells | window over aggregates, joins |
| `03_southpaw_right_vs_orthodox_right.sql` | The project hypothesis: Welch t and Cohen's d in SQL | CTEs, self-join, CASE |
| `04_weight_class_stance_mix.sql` | Stance mix per division | conditional aggregation, `RANK()`, HAVING |
| `05_top_fighters_by_division.sql` | Top 3 per division (15+ fights) | `ROW_NUMBER()`, partitioned `AVG()`, view |
| `06_ufc_striking_by_stance.sql` | UFC striking / grappling rates by stance and hand | fact-to-fact join |
| `07_finish_methods_by_style.sql` | KO / submission / decision share by style | CTE, CASE |
| `08_experience_bands.sql` | Win rate by experience band and stance | CASE banding, cumulative window |
| `09_country_continent_rollup.sql` | Fighters by country within continent | `RANK()` partitioned, share-of-partition |
| `10_southpaw_share_by_debut_decade.sql` | Southpaw share by UFC debut cohort | `LAG()`, date parsing |

The fighters are a curated set of 117, not a random sample of all UFC fighters, so these results
are descriptive. Small cells (for example 5 left-handed Southpaws) are shown with their counts.
