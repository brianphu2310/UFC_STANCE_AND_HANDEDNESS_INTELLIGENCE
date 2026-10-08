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
        st.markdown('<div class="sbh">Filter the table</div>', unsafe_allow_html=True)
        q = st.text_input("Search name", placeholder="e.g. Adesanya")
        gender = st.selectbox("Divisions", ["All", "Men", "Women"], key="ex_g")
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
      <div class="s">{escape(f['weight_class'])}, {escape(f['country'])}{', former champion' if f['champion'] else ''}</div>
      <div style="margin-top:8px"><span class="pill">{escape(f['stance'])}</span><span class="pill">{escape(f['hand'])}-handed</span><span class="pill">{escape(f['fighting_style'])}</span></div>
      <div class="kv">
        <div>Record<b>{f['wins']}–{f['losses']} ({f['win_rate']:.0f}%)</b></div>
        <div>Age<b>{val(f['age'], '{:.0f}')}</b></div>
        <div>Height<b>{val(f['height_cm'], '{:.0f} cm')}</b></div>
        <div>Reach<b>{val(f['reach_cm'], '{:.0f} cm')}</b></div>
        <div>UFC fights<b>{val(f['ufc_fights'], '{:.0f}')}</b></div>
        <div>Dominant foot<b>{f['foot']} <span class="est">est.</span></b></div>
      </div>
    </div>"""


def _butterfly(h, a, b):
    t = h["table"].iloc[::-1]
    fig = go.Figure()
    fig.add_bar(y=t["skill"], x=-t["a"], orientation="h", name=a,
                marker=dict(color=A_COLOR, line=dict(width=0)), customdata=t["a"],
                hovertemplate=f"{escape(a)}, %{{y}}: %{{customdata:.0f}}th percentile<extra></extra>")
    fig.add_bar(y=t["skill"], x=t["b"], orientation="h", name=b,
                marker=dict(color=B_COLOR, line=dict(width=0)),
                hovertemplate=f"{escape(b)}, %{{y}}: %{{x:.0f}}th percentile<extra></extra>")
    fig.update_layout(barmode="overlay", bargap=0.35,
                      xaxis=dict(range=[-105, 105], tickvals=[-100, -50, 0, 50, 100],
                                 ticktext=["100", "50", "0", "50", "100"],
                                 title="percentile vs all 117 fighters"))
    fig.add_vline(x=0, line=dict(color=ui.RULE, width=1))
    return ui.layout(fig, height=400, title="Skill percentiles, side by side",
                     margin=dict(l=12, r=14, t=74, b=10))


def render(df: pd.DataFrame):
    v = _filters(df)
    ui.page_header("Two fighters, side by side",
                   "Compare frame, stance and nine skills measured from UFC fight logs, then see "
                   "who fights most like each of them.")

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

    with st.container(key="oct_tape"):
        left, mid, right = st.columns([1, 2.3, 1], gap="small")
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
               height=480, autorotate=False, key="ex_body")

    reach = (f"{a} has {abs(h['reach_gap']):.0f} cm {'more' if h['reach_gap'] > 0 else 'less'} reach"
             if h["reach_gap"] not in (None, 0) else "Reach is even")
    ui.callout(f"<b>{escape(h['geometry'])}.</b> {escape(a)} leads on <b>{h['wins_a']}</b> of 9 skills "
               f"and {escape(b)} on <b>{h['wins_b']}</b>, counting a lead as more than 5 percentile "
               f"points. {escape(reach)}. Percentiles compare each fighter with the 117 elite fighters "
               "here, so read this as a style comparison, not a prediction.")
    g1, g2 = st.columns([1.5, 1], gap="medium")
    with g1:
        ui.chart(_butterfly(h, a, b), key="ex_fly")
    with g2:
        ui.section(f"Fights most like {a}",
                   "Nearest on all nine UFC skill percentiles plus height and reach.")
        sim = _similar(df, a)
        rows = "".join(
            f'<div class="simrow"><div><b>{escape(r.fighter)}</b><span>{escape(r.weight_class)}, '
            f'{escape(r.stance.lower())}, {escape(r.fighting_style.lower())}</span></div>'
            f'<div class="simbar"><i style="width:{r.similarity:.0f}%"></i></div>'
            f'<em>{r.similarity:.0f}</em></div>' for r in sim.itertuples())
        st.markdown(f'<div class="simlist">{rows}</div>', unsafe_allow_html=True)

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
