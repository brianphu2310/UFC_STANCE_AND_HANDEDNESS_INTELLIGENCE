"""Explorer: head-to-head comparison, look-alike fighters and a filterable fighter table."""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui
from body3d import body3d

A_COLOR, B_COLOR = ui.PALETTE[0], ui.PALETTE[1]      # magenta vs indigo


@st.cache_data
def _similar(df, name):
    return core.similar_fighters(df, name, n=5)


@st.cache_data
def _h2h(df, a, b):
    return core.head_to_head(df, a, b)


def _filters(df):
    with st.sidebar:
        st.markdown('<div class="eyebrow" style="margin-top:6px">Table filters</div>',
                    unsafe_allow_html=True)
        q = st.text_input("Search name", placeholder="e.g. Adesanya")
        gender = st.segmented_control("Divisions", ["All", "Men", "Women"], default="All",
                                      key="ex_g") or "All"
        divs = st.multiselect("Weight class",
                              [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])])
        stances = st.multiselect("Stance", ["Orthodox", "Southpaw", "Switch"])
        hands = st.multiselect("Dominant hand", ["Right", "Left"])
        styles = st.multiselect("Fighting style", core.STYLES)
        champs = st.toggle("Champions only", False)
    v = df
    if q:
        v = v[v["fighter"].str.contains(q, case=False, regex=False)]
    if gender != "All":
        v = v[v["gender"] == gender]
    for col, sel in [("weight_class", divs), ("stance", stances), ("hand", hands),
                     ("fighting_style", styles)]:
        if sel:
            v = v[v[col].isin(sel)]
    if champs:
        v = v[v["champion"]]
    return v


def _tape(f, color):
    def val(x, fmt):
        return fmt.format(x) if pd.notna(x) else "—"
    return f"""
    <div class="card" style="border-top:3px solid {color}">
      <div class="t" style="font-size:1.15rem">{escape(f['fighter'])}</div>
      <div class="s">{escape(f['weight_class'])} · {escape(f['country'])}{' · champion' if f['champion'] else ''}</div>
      <div style="margin-top:8px"><span class="pill">{escape(f['stance'])}</span><span class="pill">{escape(f['hand'])}-handed</span><span class="pill">{escape(f['fighting_style'])}</span></div>
      <div class="kv">
        <div>Record<b>{f['wins']}–{f['losses']} ({f['win_rate']:.0f}%)</b></div>
        <div>Age<b>{val(f['age'], '{:.0f}')}</b></div>
        <div>Height<b>{val(f['height_cm'], '{:.0f} cm')}</b></div>
        <div>Reach<b>{val(f['reach_cm'], '{:.0f} cm')}</b></div>
        <div>UFC fights<b>{val(f['ufc_fights'], '{:.0f}')}</b></div>
        <div>Dominant foot<b>{f['foot']} <span class="est">EST</span></b></div>
      </div>
    </div>"""


def _butterfly(h, a, b):
    t = h["table"].iloc[::-1]
    fig = go.Figure()
    fig.add_bar(y=t["skill"], x=-t["a"], orientation="h", name=a,
                marker=dict(color=A_COLOR, line=dict(width=0)), customdata=t["a"],
                hovertemplate=f"{escape(a)} · %{{y}}: %{{customdata:.0f}}th pct<extra></extra>")
    fig.add_bar(y=t["skill"], x=t["b"], orientation="h", name=b,
                marker=dict(color=B_COLOR, line=dict(width=0)),
                hovertemplate=f"{escape(b)} · %{{y}}: %{{x:.0f}}th pct<extra></extra>")
    fig.update_layout(barmode="overlay", bargap=0.35,
                      xaxis=dict(range=[-105, 105], tickvals=[-100, -50, 0, 50, 100],
                                 ticktext=["100", "50", "0", "50", "100"],
                                 title="percentile vs all 117 fighters"))
    fig.add_vline(x=0, line=dict(color=ui.RULE, width=1))
    return ui.layout(fig, height=400, title="Skill percentiles, side by side",
                     margin=dict(l=12, r=14, t=74, b=10))


def render(df: pd.DataFrame):
    v = _filters(df)
    st.markdown('<div class="eyebrow">Explorer</div>'
                '<div class="title">Put any two fighters side by side</div>'
                '<div class="sub">Tale of the tape, skill percentiles from UFC fight logs, '
                'stance geometry, and who fights most like them.</div>', unsafe_allow_html=True)
    st.write("")

    table = v.sort_values("popularity_index", ascending=False)[
        ["fighter", "stance", "hand", "weight_class", "country", "wins", "losses", "win_rate",
         "height_cm", "reach_cm", "str_acc", "sapm", "td_avg", "popularity_index"]]
    # A row clicked in the table (previous run) becomes Fighter A — applied before the widget exists.
    sel = (st.session_state.get("ex_table") or {}).get("selection", {}).get("rows", [])
    if sel and sel[0] < len(table):
        picked = table.iloc[sel[0]]["fighter"]
        if picked != st.session_state.get("ex_last_pick"):
            st.session_state["ex_last_pick"] = picked
            st.session_state["ex_a"] = picked

    names = df.sort_values("popularity_index", ascending=False)["fighter"].tolist()
    c1, c2 = st.columns(2)
    if "ex_a" not in st.session_state:
        st.session_state["ex_a"] = "Conor McGregor"
    a = c1.selectbox("Fighter A", names, key="ex_a")
    b_opts = [n for n in names if n != a]
    if st.session_state.get("ex_b") == a:
        del st.session_state["ex_b"]
    b = c2.selectbox("Fighter B", b_opts,
                     index=b_opts.index("Khabib Nurmagomedov") if "Khabib Nurmagomedov" in b_opts else 0,
                     key="ex_b")
    fa = df[df["fighter"] == a].iloc[0]
    fb = df[df["fighter"] == b].iloc[0]
    h = _h2h(df, a, b)

    left, mid, right = st.columns([1, 1.5, 1], gap="medium")
    with left:
        st.markdown(_tape(fa, A_COLOR), unsafe_allow_html=True)
    with right:
        st.markdown(_tape(fb, B_COLOR), unsafe_allow_html=True)
    with mid:
        body3d([dict(label=a, height_cm=float(fa["height_cm"]), weight_kg=float(fa["weight_kg"]),
                     reach_cm=float(fa["reach_cm"] if pd.notna(fa["reach_cm"]) else fa["height_cm"]),
                     stance="Orthodox" if fa["stance"] == "Switch" else fa["stance"],
                     hand=fa["hand"], foot=fa["foot"]),
                dict(label=b, height_cm=float(fb["height_cm"]), weight_kg=float(fb["weight_kg"]),
                     reach_cm=float(fb["reach_cm"] if pd.notna(fb["reach_cm"]) else fb["height_cm"]),
                     stance="Orthodox" if fb["stance"] == "Switch" else fb["stance"],
                     hand=fb["hand"], foot=fb["foot"], ghost=True)],
               height=330, autorotate=False, key="ex_body")

    reach = (f"{a} has {abs(h['reach_gap']):.0f} cm {'more' if h['reach_gap'] > 0 else 'less'} reach"
             if h["reach_gap"] not in (None, 0) else "Reach is even")
    ui.callout(f"<b>{escape(h['geometry'])}.</b> {escape(a)} leads on <b>{h['wins_a']}</b> of 9 skills, "
               f"{escape(b)} on <b>{h['wins_b']}</b> (a lead = more than 5 percentile points). "
               f"{escape(reach)}. Percentiles compare each fighter with this dataset of elite "
               "fighters, not the whole UFC roster — a style snapshot, not a fight prediction.")
    st.write("")
    g1, g2 = st.columns([1.5, 1], gap="medium")
    with g1:
        ui.chart(_butterfly(h, a, b), key="ex_fly")
    with g2:
        ui.section(f"Fights most like {a}",
                   "Nearest on all nine UFC skill percentiles plus height and reach.")
        sim = _similar(df, a)
        for r in sim.itertuples():
            st.markdown(f'<div class="card" style="padding:9px 14px;margin-bottom:8px">'
                        f'<div style="display:flex;justify-content:space-between">'
                        f'<span class="t" style="font-size:.95rem">{escape(r.fighter)}</span>'
                        f'<span class="score" style="font-size:1.05rem">{r.similarity:.0f}'
                        f'<small> / 100</small></span></div>'
                        f'<div class="s">{escape(r.weight_class)} · {escape(r.stance)} · '
                        f'{escape(r.hand)}-handed · {escape(r.fighting_style)}</div></div>',
                        unsafe_allow_html=True)

    ui.section(f"All fighters ({len(v)} in view)",
               "Filter in the sidebar. Click a row to load that fighter as Fighter A.")
    st.dataframe(
        table, hide_index=True, width="stretch", height=420, on_select="rerun",
        selection_mode="single-row", key="ex_table",
        column_config={
            "fighter": "Fighter", "stance": "Stance", "hand": "Hand", "weight_class": "Division",
            "country": "Country", "wins": "W", "losses": "L",
            "win_rate": st.column_config.ProgressColumn("Win rate", min_value=0, max_value=100,
                                                        format="%.0f%%"),
            "height_cm": st.column_config.NumberColumn("Height", format="%.0f cm"),
            "reach_cm": st.column_config.NumberColumn("Reach", format="%.0f cm"),
            "str_acc": st.column_config.NumberColumn("Str. acc", format="%.0f%%"),
            "sapm": st.column_config.NumberColumn("Absorbed/min", format="%.2f"),
            "td_avg": st.column_config.NumberColumn("TD/15", format="%.2f"),
            "popularity_index": st.column_config.ProgressColumn("Popularity", min_value=0,
                                                                max_value=100, format="%d"),
        })
    st.download_button("Download this view as CSV", table.to_csv(index=False).encode(),
                       "ufc_fighters.csv", "text/csv")
