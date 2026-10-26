"""
UFC Stance & Handedness Intelligence — Streamlit app.

Run locally:  streamlit run ufc_intelligence_app.py
Data:         data/ufc_fighters_enriched.csv (scripts/build_clean_dataset.py → enrich_dataset.py)
"""
from pathlib import Path

import pandas as pd
import streamlit as st

import ufc_core as core
import ui
from views import brian, build_fighter, data_notes, fighters, home, matchup, overview, stance_lab

st.set_page_config(page_title="UFC Stance Intelligence", layout="wide",
                   page_icon=str(Path(__file__).parent / "static" / "mark.png"),
                   initial_sidebar_state="collapsed")
ui.inject_css()


@st.cache_data
def get_data() -> pd.DataFrame:
    return core.load_fighters()


try:
    df = get_data()
except Exception as exc:  # surfaced in the UI
    st.error(f"Could not load the dataset — {exc}")
    st.stop()


def _page(render, title, footer=True):
    def run():
        render(df)
        if footer:
            ui.footer(len(df))
    run.__name__ = render.__module__.split(".")[-1]
    return run


pages = [
    st.Page(_page(home.render, "Home"), title="Home", url_path="home", default=True),
    st.Page(_page(overview.render, "Dashboard", footer=False), title="Dashboard", url_path="dashboard"),
    st.Page(_page(fighters.render, "Fighters"), title="Fighters", url_path="fighters"),
    st.Page(_page(matchup.render, "Matchup"), title="Matchup", url_path="matchup"),
    st.Page(_page(stance_lab.render, "Analysis"), title="Analysis", url_path="analysis"),
    st.Page(_page(build_fighter.render, "Build"), title="Build", url_path="build-your-fighter"),
    st.Page(_page(brian.render, "Spar"), title="Spar", url_path="spar-vs-brian"),
    st.Page(_page(data_notes.render, "Methodology"), title="Methodology", url_path="methodology"),
]
ui.PAGES.update(zip(["home", "dashboard", "fighters", "matchup", "analysis", "build", "spar", "methodology"], pages))
st.navigation(pages, position="top").run()
