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
from views import brian, build_fighter, data_notes, explorer, overview, stance_lab

st.set_page_config(page_title="UFC Stance Intelligence", layout="wide",
                   page_icon=str(Path(__file__).parent / "static" / "mark.png"),
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


def _page(render, title, footer=True):
    def run():
        i = [p.title for p in pages].index(title) + 1
        ui.KICKER["value"] = f'<i>{i:02d}</i> {title}'
        render(df)
        if footer:
            ui.footer(len(df))
    run.__name__ = render.__module__.split(".")[-1]
    return run


pages = [
    st.Page(_page(overview.render, "Overview", footer=False), title="Overview",
            url_path="overview", default=True),
    st.Page(_page(explorer.render, "Explorer"), title="Explorer", url_path="explorer"),
    st.Page(_page(build_fighter.render, "Build a fighter"), title="Build a fighter",
            url_path="build-your-fighter"),
    st.Page(_page(stance_lab.render, "Stance lab"), title="Stance lab", url_path="stance-lab"),
    st.Page(_page(brian.render, "Spar vs Brian"), title="Spar vs Brian", url_path="spar-vs-brian"),
    st.Page(_page(data_notes.render, "Data"), title="Data", url_path="data-methods"),
]
st.navigation(pages, position="top").run()
