"""
UFC Stance & Handedness Intelligence — Streamlit app.

Run locally:  streamlit run ufc_intelligence_app.py
Pages:        Global dashboard · Build your fighter · Stance lab · Spar vs Brian · Data & methods
Data:         data/ufc_fighters_enriched.csv (scripts/build_clean_dataset.py → enrich_dataset.py)
"""
import pandas as pd
import streamlit as st

import ufc_core as core
import ui
from views import brian, build_fighter, dashboard, data_notes, stance_lab

st.set_page_config(page_title="UFC Stance Intelligence", page_icon="🥊", layout="wide")
ui.inject_css()

PAGES = {
    "🌍 Global dashboard": dashboard.render,
    "🥋 Build your fighter": build_fighter.render,
    "📊 Stance lab": stance_lab.render,
    "⚔️ Spar vs Brian": brian.render,
    "ℹ️ Data & methods": data_notes.render,
}
SLUGS = {name: name.split(" ", 1)[1].lower().replace(" & ", "-").replace(" ", "-")
         for name in PAGES}


@st.cache_data
def get_data() -> pd.DataFrame:
    return core.load_fighters()


try:
    df = get_data()
except Exception as exc:  # surfaced in the UI
    st.error(f"Could not load the dataset — {exc}")
    st.stop()

# Page picker: a dropdown in the header, remembered in the URL (?page=build-your-fighter)
by_slug = {v: k for k, v in SLUGS.items()}
current = by_slug.get(st.query_params.get("page", ""), next(iter(PAGES)))
bar = st.columns([3, 1.2])
with bar[0]:
    st.markdown('<div class="eyebrow" style="margin-top:8px">🥊 UFC Stance &amp; Handedness '
                'Intelligence</div>', unsafe_allow_html=True)
with bar[1]:
    page = st.selectbox("Page", list(PAGES), index=list(PAGES).index(current),
                        label_visibility="collapsed")
if SLUGS[page] != st.query_params.get("page"):
    st.query_params["page"] = SLUGS[page]

PAGES[page](df)
ui.footer(len(df))
