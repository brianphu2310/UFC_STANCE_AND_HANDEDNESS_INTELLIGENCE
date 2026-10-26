# UFC Stance & Handedness Intelligence
*An end-to-end data project that started on the sparring mats at UFC Gym Townhall, Sydney.*

[![Streamlit App](https://img.shields.io/badge/Streamlit_App-Live-C862CE?style=for-the-badge&logo=streamlit&logoColor=white)](https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app)
[![Tableau](https://img.shields.io/badge/Tableau_Dashboard-Live-5A54D8?style=for-the-badge&logo=tableau&logoColor=white)](https://public.tableau.com/app/profile/brian.ma5935/viz/UFCRECOMENDATIONENGINE/Dashboard1)
[![Kaggle Dataset](https://img.shields.io/badge/Dataset-Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/brianphu)
[![Tests](https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/actions/workflows/ci.yml/badge.svg)](https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/actions/workflows/ci.yml)

![App tour: every page of the app](docs/gif/app_tour.gif)

## The question

I train kickboxing and Muay Thai. One session I stepped on my partner's foot mid-combination —
we were in mirror-image stances and our footwork collided. I'm a **right-handed southpaw**: my
dominant hand is my *lead* hand, so my jab is my best weapon, not the rear straight most
southpaws are known for.

That raised a testable question: **does stance — or the hand behind it — change who wins at the
top level?**

## What the data says

117 elite fighters from 28 countries, official UFCSTATS stance, pro record and UFC fight-log stats.

| Comparison | n | Mean win rate | Gap (95% CI) | Welch p | Holm p | Cohen's d |
|---|---|---|---|---|---|---|
| Southpaw vs orthodox | 26 vs 83 | 77.9% vs 77.7% | +0.2 (−3.9 to +4.5) | 0.93 | 1.00 | 0.02 |
| Right-handed southpaw vs orthodox right-hander | 21 vs 73 | 79.2% vs 77.4% | +1.8 (−2.7 to +6.7) | 0.45 | 1.00 | 0.19 |
| Switch-stance vs single-stance | 8 vs 109 | 82.5% vs 77.7% | +4.8 (−1.2 to +10.6) | 0.18 | 0.71 | 0.50 |
| Left-handed vs right-handed | 15 vs 102 | 77.1% vs 78.2% | −1.0 (−6.9 to +4.2) | 0.73 | 1.00 | −0.11 |

**No stance or handedness group wins reliably more often.** Every interval crosses zero, and none
survives a Holm correction for running several tests at once. Switch-hitters show the largest
gap, but with 8 fighters a 5-point edge can't be told apart from chance — a real test would need
about 60 fighters per group.

Where stance *does* show up is in **how** people fight (Analysis and Matchup pages): the skill
profiles, reach distributions and striking-vs-grappling mix differ by stance, even though the
win rates don't.

> Earlier versions of this README reported a 74.3% vs 70.2% "right-handed southpaw advantage"
> (d = 0.43). Re-checking against the official UFCSTATS stance showed that **43 of 117 fighters had
> the wrong stance** in the original spreadsheet, and the corrected data shows no such advantage.
> The app lists every correction on its Methodology page.

## See it move

The fighters are a real human body model (the MakeHuman CC0 base mesh, shaped into an athletic
male and rigged by `scripts/build_body_model.py`), posed every frame by the app's own joint solver,
inside a full-size Octagon (30 ft across, canvas mat, red and blue corner posts, chain-link fence that
cuts away on the camera's side). Both wear MMA kit: 4 oz gloves and fight shorts in their corner colour.

In **Spar** mode the two fighters bounce in stance, feint, circle and step in with real footwork, throw
ten combos (1-2, 1-2-3, jab and double-leg, 1-2 and body kick and more) and step back out, while the
other fighter slips, covers, rolls, checks kicks and sprawls. Every strike is judged as it arrives:
short, defended or landed, from the live distance between the two bodies. A body kick that lands drops
the opponent to one knee. The **Jab / Cross / Kick** buttons throw one strike from the measured
distance in the range table; **Height** and **Reach** line the two fighters up against a ruler.

| Spar: footwork, combos and defence | Jab, kick, then Height and Reach |
|---|---|
| ![Spar mode, McGregor vs Khabib](docs/gif/faceoff_combo.gif) | ![Single strikes and the height and reach views](docs/gif/modes.gif) |

**Build a fighter:** the body model grows and fills out as the height, weight and reach sliders move.

![Body model morphing with height and weight](docs/gif/morph.gif)

## The app

A fight-intelligence product in a charcoal-and-fight-red identity: condensed editorial headlines,
thin borders, square corners, and red kept for one job at a time (the active page, the primary
action, and the southpaw in every chart, against orthodox in steel and switch in brass). It opens on
a 7-second intro drawn in HTML and CSS (skippable, off under reduced motion), then the landing page.

| Page | What it does |
|---|---|
| **Home** | "Read the fight beyond the octagon": the research question, three findings with their numbers, an orthodox vs southpaw tale of the tape, and a way into every page |
| **Dashboard** | Sample counts, win rate by stance, Welch tests with bootstrap intervals and effect sizes for the three headline gaps, stance × hand and hand × foot distributions, a 3D globe with debut timeline, and how the styles differ. One Filters button drives every block |
| **Fighters** | Searchable, filterable directory of all 117 fighters: stance, hand, division, record, frame and UFC fight-log rates. Select a row to open the fighter in the Matchup lab; export the view as CSV |
| **Matchup** | Two fighters side by side: tale of the tape on nine attributes, a 3D face-off in the Octagon, skill-percentile butterfly chart and look-alike fighters. No predictions |
| **Analysis** | Any outcome by stance, hand or foot: Welch t-test, Mann-Whitney, bootstrap intervals, Cohen's d, Holm correction, ANOVA, power, and what the results do and do not support |
| **Build** | Your height, weight, reach, dominant hand and foot, style and goal → 3D body model, stance advice, fighters to study, a phased roadmap, gear to buy and classes. Downloadable plan |
| **Spar** | The case study that started the project: a game plan against a right-handed southpaw |
| **Methodology** | Sources, cleaning steps, the 43 stance corrections, feature definitions, methods, limitations and how to reproduce every number |

<table><tr><td colspan="2"><img src="docs/img/home.png" alt="Home: landing page"></td></tr><tr>
<td><img src="docs/img/overview.png" alt="Intelligence dashboard"></td>
<td><img src="docs/img/fighters.png" alt="Fighter directory"></td>
</tr><tr>
<td><img src="docs/img/explorer.png" alt="Matchup lab"></td>
<td><img src="docs/img/stance_lab.png" alt="Statistical analysis"></td>
</tr><tr>
<td><img src="docs/img/build_fighter.png" alt="Build a fighter"></td>
<td><img src="docs/img/data.png" alt="Methodology"></td>
</tr></table>

Colours, type, components and accessibility notes are in [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md).

## Power BI dashboard

The same dataset as a four-page Power BI report, `powerbi/ufc_dashboard.pbix`. **Dashboard** ranks the
top fighters to study and maps where they come from; **Fighters world** compares height against reach
and win rate by stance and hand; **Skills lab** breaks wins down by method and weight class; **About**
explains every measure. Stance, hand and weight-class filters apply on every page.

| | |
|---|---|
| ![Power BI dashboard](docs/powerbi/ufc-1.png) | ![Power BI fighters world](docs/powerbi/ufc-2.png) |
| ![Power BI skills lab](docs/powerbi/ufc-3.png) | ![Power BI about](docs/powerbi/ufc-4.png) |

## Data

| Source | Used for |
|---|---|
| Project spreadsheet (`UFC_FINAL_DATASET.xlsx`) | Fighter list, full pro record, dominant hand, nationality |
| [UFCSTATS](http://ufcstats.com) via the public [Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats) dump | Official stance, height, reach, date of birth, round-by-round fight stats |
| Derived | Strike accuracy/defence, output, damage absorbed, takedowns, control time, fighting style, popularity index |
| Estimated | **Dominant foot only** — no public source records it; clearly marked "≈" / "EST" everywhere |
| [MakeHuman](https://github.com/makehumancommunity/makehuman) (CC0) | 3D body mesh, skeleton, skin weights and body-shape targets for the fighter model |
| Press photos | The landing page; each one is credited on screen and listed in `static/hero/credits.csv` (gear photos in `static/gear/credits.csv`) |

Every column's source is listed in `data/data_dictionary.csv`. Coaches and classes on the
Build-a-fighter page are a fictional sample catalogue you can replace with a real gym's roster.

## Run it

```bash
pip install -r requirements.txt
streamlit run ufc_intelligence_app.py
```

Rebuild the data (downloads the UFCSTATS dump on first run):

```bash
pip install -r requirements-dev.txt
python scripts/build_clean_dataset.py
python scripts/enrich_dataset.py
```

Data pipeline and SQL (builds a SQLite star schema, then runs ten analysis queries):

```bash
python -m pipeline.run
python sql/run_queries.py
```

Tests (data quality, pipeline, SQL, statistics, recommender, and a smoke test of every page; 105 tests):

```bash
pytest -q
```

## Project structure

```
ufc_intelligence_app.py     entry point, top-bar navigation (Home is the default page)
ufc_core.py                 statistics, recommender, roadmap (no Streamlit — unit-tested)
ui.py                       design tokens, fonts, navigation, panels, chart defaults, motion, shared HTML pieces
views/                      one module per page (home.py holds the landing page and intro)
components/globe3d/         three.js globe (bundled locally, no CDN)
components/body3d/          three.js face-off: skinned MakeHuman body (fighter.glb) driven by a joint solver
static/hero/                fight photos for the landing page, credits.csv
static/gear/                gear photos for Build a fighter, credits.csv
static/fonts/               self-hosted Big Shoulders Display and Inter (OFL)
pipeline/                   ETL into a SQLite star schema with data-quality checks (schema.sql)
sql/                        ten analysis queries, results in docs/query_results/
ingestion/                  live UFCSTATS scraper (run by .github/workflows/live-ingestion.yml)
scripts/                    build_clean_dataset.py → enrich_dataset.py, build_body_model.py
data/                       cleaned + enriched dataset, data dictionary, sample catalogues
powerbi/                    Power BI report (screenshots in docs/powerbi/)
docs/                       data model, dictionary, quality report, design system, skills map
tests/                      pytest suite incl. Streamlit AppTest page smoke tests
notebooks/                  original scraping, cleaning and visualisation work
legacy/                     first-version scripts kept for reference
```

## Limitations

- **Sample:** 117 well-known fighters, mostly winners — win rates are compressed and small
  groups (5–21 fighters) give wide intervals.
- **Dominant hand** comes from the project spreadsheet and is not independently verified.
- **UFC-only stats** — fighters with little UFC time (e.g. Fedor) have no fight-log stats.
- The Tableau dashboard and Colab notebook predate the stance corrections.
- Fight photos belong to their owners and are used with credit for a class project;
  the app is not affiliated with the UFC.

## About

**Brian Phu** — data analyst and southpaw kickboxer, Sydney.
[LinkedIn](https://www.linkedin.com/in/brian-phu-data-analysta55353390/) ·
[GitHub](https://github.com/brianphu2310) ·
[Kaggle](https://www.kaggle.com/brianphu) ·
[Tableau](https://public.tableau.com/app/profile/brian.ma5935/vizzes)

MIT License.
