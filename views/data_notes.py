"""Data & methods: provenance of every column, stance corrections, limitations."""
import pandas as pd
import streamlit as st

import ufc_core as core
import ui


def render(df: pd.DataFrame):
    st.markdown('<div class="eyebrow">Data &amp; methods</div>'
                '<div class="title">Where every number comes from</div>', unsafe_allow_html=True)
    st.write("")
    dic = pd.read_csv(core.DATA_DIR / "data_dictionary.csv")
    st.dataframe(dic, hide_index=True, width="stretch",
                 column_config={"source": st.column_config.TextColumn("Source")})
    ui.callout(
        "<b>scraped</b> = UFCSTATS / Tapology / Sherdog · <b>derived</b> = computed from scraped "
        "fight logs · <b>curated</b> = assigned from public knowledge · "
        "<b>estimated</b> = generated, not real (dominant foot only). Coaches and classes on the "
        "Build-your-fighter page are a fictional sample catalogue.")

    mism = df[~df["stance_matches_project"]]
    ui.section(f"Stance corrections ({len(mism)} fighters)",
               "The original Excel file's stance disagreed with the official UFCSTATS stance. "
               "The app uses UFCSTATS.")
    st.dataframe(mism[["fighter", "stance_project", "stance", "hand"]]
                 .rename(columns={"stance_project": "Project file", "stance": "UFCSTATS",
                                  "fighter": "Fighter", "hand": "Hand"}),
                 hide_index=True, width="stretch", height=300)

    st.markdown("""
**Limitations**
- *Dominant foot is estimated.* No public source records it; it's set to the same side as the
  dominant hand for ~80% of fighters. Add real values in `data/fighter_overrides.csv`.
- *Dominant hand* comes from the project dataset and is not independently verified.
- *Small groups.* Left-handed and switch-stance groups have 5–15 fighters, so intervals are wide.
- *Selection bias.* These are well-known fighters — mostly winners — which compresses win rates.
- *UFC-only stats.* Accuracy, output and damage cover UFC bouts only (from UFCSTATS fight logs);
  fighters with little UFC time have no or noisy values.

**Rebuild the data**
```bash
python scripts/build_clean_dataset.py   # scrape + merge (downloads the UFCSTATS dump once)
python scripts/enrich_dataset.py        # foot, popularity, dictionary, sample catalogues
```
""")
