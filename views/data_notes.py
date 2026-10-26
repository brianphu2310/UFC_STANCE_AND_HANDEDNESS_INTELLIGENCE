"""Methodology: sources, cleaning, feature definitions, methods, limitations and reproducibility."""
from html import escape

import pandas as pd
import streamlit as st

import ufc_core as core
import ui

REPO = "https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE"
LINKS = [
    ("Streamlit app", "https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app"),
    ("Tableau dashboard", "https://public.tableau.com/app/profile/brian.ma5935/viz/UFCRECOMENDATIONENGINE/Dashboard1"),
    ("Scraping notebook in Colab", f"https://colab.research.google.com/github/brianphu2310/"
                                   "UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/blob/main/notebooks/UFC_DATA_SCRAPING.ipynb"),
    ("Cleaning notebook in Colab", f"https://colab.research.google.com/github/brianphu2310/"
                                   "UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/blob/main/notebooks/UFC_DATA_CLEANING_PROCESSING.ipynb"),
    ("Source code on GitHub", REPO),
]

SOURCES = [
    ("Project spreadsheet", "UFC_FINAL_DATASET.xlsx", "Fighter list, full pro record, dominant hand, nationality"),
    ("UFCSTATS", "via the public Greco1899/scrape_ufc_stats dump",
     "Official stance, height, reach, date of birth, round-by-round UFC fight stats"),
    ("Derived", "scripts/build_clean_dataset.py", "Accuracy, defence, output, damage absorbed, takedowns, "
     "control time, fighting style, popularity"),
    ("Estimated", "scripts/enrich_dataset.py", "Dominant foot only: no public source records it"),
]

CLEANING = [
    "Load the 117 fighters from the project spreadsheet and match each one to UFCSTATS by normalised name; "
    "the build stops if any fighter has no match.",
    "Replace the spreadsheet's stance with the official UFCSTATS stance wherever they disagree "
    "(the corrections are listed below).",
    "Convert heights and reaches from inches to centimetres, parse \"13 of 27\" strike counts and mm:ss "
    "control times, and sum UFC fight logs into per-minute and per-15-minute rates.",
    "Derive age, ape index (reach minus height), win rate = wins / (wins + losses) and a fighting style "
    "(striker, grappler or all-rounder) from striking and grappling percentiles, for fighters with 3+ UFC fights.",
    "Validate 33 rules before loading the warehouse (unique fighter, domains, ranges, win-rate formula); "
    "the load is blocked if any fails. See docs/DATA_QUALITY.md.",
]

METHODS = [
    ("Group comparison", "Welch's t-test on the difference in means, which does not assume equal variances."),
    ("Rank check", "Mann-Whitney U, which does not assume normal data."),
    ("Uncertainty", "95% bootstrap interval for the difference in means (5,000 resamples, fixed seed)."),
    ("Effect size", "Cohen's d with the pooled standard deviation; |d| < 0.2 negligible, < 0.5 small, < 0.8 medium."),
    ("Multiple tests", "Holm step-down correction across the family of comparisons shown together."),
    ("Power", "Fighters per group needed to detect the observed d at 80% power and 5% significance."),
    ("All groups", "One-way ANOVA and Kruskal-Wallis across every level of a grouping."),
    ("Skill percentiles", "Each of nine UFC rates ranked against all 117 fighters; lower is better for "
     "strikes absorbed."),
]


def render(df: pd.DataFrame):
    mism = df[~df["stance_matches_project"]]
    ui.page_header("How the numbers are made",
                   f"<b>{len(df)}</b> fighters, <b>{df.shape[1]}</b> columns, <b>{len(mism)}</b> stances corrected "
                   "against UFCSTATS. Every figure in the app is computed from this one table, and every column "
                   "is labelled scraped, derived, curated or estimated.", kicker="Methodology")

    st.markdown(CSS, unsafe_allow_html=True)
    links = "".join(f'<a href="{u}" target="_blank" rel="noopener">{escape(t)}</a>' for t, u in LINKS)
    st.markdown(f'<div class="links">{links}</div>', unsafe_allow_html=True)

    ui.section("Data sources")
    rows = "".join(f'<div class="sr"><b>{escape(a)}</b><span>{escape(b)}</span><p>{escape(c)}</p></div>'
                   for a, b, c in SOURCES)
    st.markdown(f'<div class="srcs">{rows}</div>', unsafe_allow_html=True)

    ui.section("Data cleaning", "From the raw spreadsheet and scrape to the table the app reads.")
    steps = "".join(f"<li>{escape(x)}</li>" for x in CLEANING)
    st.markdown(f'<ol class="steps">{steps}</ol>', unsafe_allow_html=True)

    ui.section(f"Stance corrections ({len(mism)} fighters)",
               "Where the original spreadsheet disagreed with the official UFCSTATS stance. The app uses UFCSTATS.")
    st.dataframe(mism[["fighter", "stance_project", "stance", "hand"]]
                 .rename(columns={"stance_project": "Spreadsheet", "stance": "UFCSTATS",
                                  "fighter": "Fighter", "hand": "Hand"}),
                 hide_index=True, width="stretch", height=min(38 + 35 * len(mism), 360))

    ui.section("Feature definitions", "Every column, what it means and where it comes from "
               "(data/data_dictionary.csv).")
    dic = pd.read_csv(core.DATA_DIR / "data_dictionary.csv")
    st.dataframe(dic, hide_index=True, width="stretch", height=420,
                 column_config={"column": st.column_config.TextColumn("Column", width="medium"),
                                "meaning": st.column_config.TextColumn("Meaning", width="large"),
                                "source": st.column_config.TextColumn("Source", width="small")})

    ui.section("Analytical methods", "Implemented in ufc_core.py and unit-tested in tests/test_core.py.")
    rows = "".join(f'<div class="mr"><b>{escape(a)}</b><p>{escape(b)}</p></div>' for a, b in METHODS)
    st.markdown(f'<div class="meth">{rows}</div>', unsafe_allow_html=True)

    ui.section("Limitations")
    st.markdown(f"""<ul class="lim">
  <li><b>Selection.</b> {len(df)} well-known fighters, mostly winners, so win rates are compressed (median
    {df['win_rate'].median():.0f}%) and differences are harder to see.</li>
  <li><b>Small groups.</b> {int((df['stance'] == 'Switch').sum())} switch-stance and {int((df['hand'] == 'Left').sum())}
    left-handed fighters: intervals for those groups are wide.</li>
  <li><b>Dominant foot is estimated</b>, set to the hand's side for about 80% of fighters with a fixed seed.
    Comparisons that use it are marked ≈ and should not be read as findings.</li>
  <li><b>Dominant hand</b> comes from the project spreadsheet and is not independently verified.</li>
  <li><b>UFC-only rates.</b> Accuracy, output and takedowns cover UFC bouts only; fighters with little UFC time
    have missing or noisy values.</li>
  <li><b>Observational data.</b> Stance is chosen, not assigned, so no result here is causal.</li>
</ul>""", unsafe_allow_html=True)

    ui.section("Reproduce it")
    st.code("""pip install -r requirements.txt -r requirements-dev.txt
python scripts/build_clean_dataset.py   # scrape + merge (downloads the UFCSTATS dump once)
python scripts/enrich_dataset.py        # derived columns, estimated foot, data dictionary
python -m pipeline.run                  # validate and load the SQLite star schema
python sql/run_queries.py               # ten analysis queries -> docs/query_results/
pytest -q                               # data, statistics and every page
streamlit run ufc_intelligence_app.py""", language="bash")
    st.caption("Bootstrap intervals use a fixed seed (7), so the same data gives the same intervals. "
               "Continuous integration runs the test suite on every pull request.")


CSS = f"""<style>
  .links {{ display: flex; flex-wrap: wrap; gap: 8px; margin: -4px 0 8px; }}
  .links a {{ display: inline-flex; align-items: center; height: 34px; padding: 0 14px; border: 1px solid {ui.CONTROL};
              border-radius: 2px; font-size: 13px; font-weight: 500; color: {ui.INK} !important; text-decoration: none !important;
              transition: border-color .15s ease; }}
  .links a::after {{ content: "↗"; margin-left: 8px; color: {ui.ACCENT}; }}
  .links a:hover {{ border-color: {ui.INK_2}; }}
  .srcs, .meth {{ background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 4px; padding: 4px 20px; }}
  .sr {{ display: grid; grid-template-columns: 180px 280px 1fr; gap: 20px; padding: 12px 0; border-bottom: 1px solid {ui.BORDER}; }}
  .mr {{ display: grid; grid-template-columns: 180px 1fr; gap: 20px; padding: 12px 0; border-bottom: 1px solid {ui.BORDER}; }}
  .sr:last-child, .mr:last-child {{ border-bottom: none; }}
  .sr b, .mr b {{ font: 500 14px/1.5 {ui.FONT}; color: {ui.INK}; }}
  .sr span {{ font-size: 13px; color: {ui.INK_MUTED}; line-height: 1.5; }}
  .sr p, .mr p {{ margin: 0; }}
  .steps {{ counter-reset: s; list-style: none; padding: 0; margin: 0; border-top: 1px solid {ui.BORDER}; }}
  .steps li {{ counter-increment: s; display: grid; grid-template-columns: 40px 1fr; padding: 12px 0;
               border-bottom: 1px solid {ui.BORDER}; margin: 0; }}
  .steps li::before {{ content: counter(s); font: 800 22px/1 {ui.DISPLAY}; color: {ui.ACCENT}; }}
  .lim {{ padding-left: 18px; }} .lim li {{ margin: 6px 0; }}
  @media (max-width: 800px) {{ .sr, .mr {{ grid-template-columns: 1fr; gap: 4px; }} }}
</style>"""
