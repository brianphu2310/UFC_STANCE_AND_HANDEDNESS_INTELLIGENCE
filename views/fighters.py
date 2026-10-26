"""Fighters: the searchable directory of all 117 fighters, filtered in one row of controls."""
import pandas as pd
import streamlit as st

import ufc_core as core
import ui

COLS = ["fighter", "stance", "hand", "foot", "weight_class", "country", "wins", "losses", "win_rate",
        "height_cm", "reach_cm", "ape_index_cm", "ufc_fights", "slpm", "str_acc", "str_def", "sapm",
        "td_avg", "fighting_style"]


def _filters(df):
    c = st.columns([2.2, 1.3, 1.1, 1, 1.1, 1], vertical_alignment="bottom")
    q = c[0].text_input("Search", placeholder="Fighter name", key="fd_q")
    div = c[1].selectbox("Division", ["All"] + [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])],
                         key="fd_div")
    stance = c[2].selectbox("Stance", ["All", "Orthodox", "Southpaw", "Switch"], key="fd_st")
    hand = c[3].selectbox("Hand", ["All", "Right", "Left"], key="fd_hand")
    style = c[4].selectbox("Style", ["All"] + core.STYLES, key="fd_style")
    champs = c[5].toggle("Champions", False, key="fd_champ")
    v = df
    if q:
        v = v[v["fighter"].str.contains(q, case=False, regex=False)]
    for col, val in [("weight_class", div), ("stance", stance), ("hand", hand), ("fighting_style", style)]:
        if val != "All":
            v = v[v[col] == val]
    if champs:
        v = v[v["champion"]]
    return v


def render(df: pd.DataFrame):
    sp, sw, lh = (df["stance"] == "Southpaw").sum(), (df["stance"] == "Switch").sum(), (df["hand"] == "Left").sum()
    ui.page_header("Fighter directory",
                   f"<b>{len(df)}</b> fighters from <b>{df['country'].nunique()}</b> countries: "
                   f"{sp} southpaws, {sw} switch-hitters and {lh} left-handers. Stance is the official "
                   "UFCSTATS listing; skill columns come from UFC fight logs only.", kicker="Fighters")
    v = _filters(df)
    table = v.sort_values("popularity_index", ascending=False)[COLS].reset_index(drop=True)
    if table.empty:
        st.markdown('<div class="empty">No fighter matches these filters. Clear the search or set a '
                    'filter back to All.</div>', unsafe_allow_html=True)
        return
    st.caption(f"Showing {len(table)} of {len(df)} fighters, most popular first. Select a row to open "
               "that fighter in the Matchup lab.")
    ev = st.dataframe(
        table, hide_index=True, width="stretch", height=min(38 + 35 * len(table), 640),
        on_select="rerun", selection_mode="single-row", key="fd_table",
        column_config={
            "fighter": st.column_config.TextColumn("Fighter", width="medium", pinned=True),
            "stance": "Stance", "hand": "Hand", "foot": "Foot (est.)", "weight_class": "Division",
            "country": "Country", "wins": "W", "losses": "L",
            "win_rate": st.column_config.NumberColumn("Win %", format="%.0f%%"),
            "height_cm": st.column_config.NumberColumn("Height", format="%.0f cm"),
            "reach_cm": st.column_config.NumberColumn("Reach", format="%.0f cm"),
            "ape_index_cm": st.column_config.NumberColumn("Ape index", format="%+.0f cm",
                                                          help="Reach minus height"),
            "ufc_fights": st.column_config.NumberColumn("UFC fights", format="%d"),
            "slpm": st.column_config.NumberColumn("Landed/min", format="%.2f"),
            "str_acc": st.column_config.NumberColumn("Str. acc", format="%.0f%%"),
            "str_def": st.column_config.NumberColumn("Str. def", format="%.0f%%"),
            "sapm": st.column_config.NumberColumn("Absorbed/min", format="%.2f"),
            "td_avg": st.column_config.NumberColumn("TD/15 min", format="%.2f"),
            "fighting_style": "Style",
        })
    rows = ev.selection.rows if ev and ev.selection else []
    b, a = st.columns([1, 3], vertical_alignment="center")
    with a:
        if rows:
            name = table.iloc[rows[0]]["fighter"]
            if st.button(f"Open {name} in Matchup", type="primary", key="fd_open"):
                st.session_state["ex_a"] = name
                if "matchup" in ui.PAGES:
                    st.switch_page(ui.PAGES["matchup"])
    with b:
        st.download_button("Download this view as CSV", table.to_csv(index=False).encode(), "ufc_fighters.csv",
                           "text/csv")
