"""
UFC Stance & Handedness Intelligence — Streamlit app.

Run locally:  streamlit run ufc_intelligence_app.py
Data:         data/ufc_fighters_enriched.csv (scripts/build_clean_dataset.py → enrich_dataset.py)
"""
import pandas as pd
import streamlit as st

import ufc_core as core
import ui
from views import brian, build_fighter, dashboard, data_notes, overview, stance_lab

st.set_page_config(page_title="UFC Stance Intelligence", page_icon="🥊", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject_css()


@st.cache_data
def get_data() -> pd.DataFrame:
    return core.load_fighters()


try:
    df = get_data()
except Exception as exc:  # surfaced in the UI
    st.error(f"Could not load the dataset — {exc}")
    st.stop()


def _page(render, footer=True):
    def run():
        render(df)
        if footer:
            ui.footer(len(df))
    run.__name__ = render.__module__.split(".")[-1]
    return run


pages = [
    st.Page(_page(overview.render, footer=False), title="Global overview", icon="🌍",
            url_path="overview", default=True),
    st.Page(_page(dashboard.render), title="Deep-dive charts", icon="📈", url_path="deep-dive"),
    st.Page(_page(build_fighter.render), title="Build your fighter", icon="🥋",
            url_path="build-your-fighter"),
    st.Page(_page(stance_lab.render), title="Stance lab", icon="📊", url_path="stance-lab"),
    st.Page(_page(brian.render), title="Spar vs Brian", icon="⚔️", url_path="spar-vs-brian"),
    st.Page(_page(data_notes.render), title="Data & methods", icon="ℹ️", url_path="data-methods"),
]
st.navigation(pages, position="sidebar").run()
