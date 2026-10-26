"""Explorer: head-to-head comparison, look-alike fighters and a filterable fighter table."""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui
from body3d import body3d

A_COLOR, B_COLOR = ui.PALETTE[0], ui.PALETTE[1]      # red corner vs blue corner


@st.cache_data
def _similar(df, name):
    return core.similar_fighters(df, name, n=5)


@st.cache_data
def _h2h(df, a, b):
    return core.head_to_head(df, a, b)


def _filters(df):
    """Search beside a Filters button in the table's own header row."""
    keys = ("ex_g", "ex_div", "ex_st", "ex_hand", "ex_style", "ex_champ")
    on = sum(bool(st.session_state.get(k)) and st.session_state.get(k) != "All" for k in keys)
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    q = c1.text_input("Search by name", placeholder="Search fighters, e.g. Adesanya", label_visibility="collapsed",
                      key="ex_q")
    with c2, st.popover(f"Filters, {on} on" if on else "Filters", width="content"):
        gender = st.selectbox("Division", ["All", "Men", "Women"], key="ex_g")
        divs = st.multiselect("Weight class",
                              [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])],
                              placeholder="Any", key="ex_div")
        stances = st.multiselect("Stance", ["Orthodox", "Southpaw", "Switch"], placeholder="Any", key="ex_st")
        hands = st.multiselect("Dominant hand", ["Right", "Left"], placeholder="Any", key="ex_hand")
        styles = st.multiselect("Fighting style", core.STYLES, placeholder="Any", key="ex_style")
        champs = st.toggle("Champions only", False, key="ex_champ")
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


def _tape(f, color, skills=None):
    def val(x, fmt):
        return fmt.format(x) if pd.notna(x) else "—"
    return f"""
    <div class="card tape">
      <div class="t"><i class="dot" style="background:{color}"></i>{escape(f['fighter'])}</div>
      <div class="s">{escape(f['weight_class'])}, {escape(f['country'])}{', former champion' if f['champion'] else ''}</div>
      <div style="margin-top:8px"><span class="pill">{escape(f['stance'])}</span><span class="pill">{escape(f['hand'])}-handed</span><span class="pill">{escape(f['fighting_style'])}</span></div>
      <div class="kv">
        <div>Record<b>{f['wins']}–{f['losses']} <small>{f['win_rate']:.0f}%</small></b></div>
        <div>Age<b>{val(f['age'], '{:.0f}')}</b></div>
        <div>Height<b>{val(f['height_cm'], '{:.0f}')} <small>cm</small></b></div>
        <div>Reach<b>{val(f['reach_cm'], '{:.0f}')} <small>cm</small></b></div>
        <div>UFC fights<b>{val(f['ufc_fights'], '{:.0f}')}</b></div>
        <div>Dominant foot<b>{f['foot']}<span class="est">est.</span></b></div>
      </div>{_best(skills)}
    </div>"""


def _best(skills):
    """The fighter's three highest skill percentiles, as a short ranked list under the tape."""
    if skills is None or skills.empty:
        return ""
    rows = "".join(f'<div class="br"><span>{escape(k)}</span><i><u style="width:{v:.0f}%"></u></i><b>{v:.0f}</b></div>'
                   for k, v in skills.items())
    return f'<div class="best"><div class="s">Strongest skills, percentile</div>{rows}</div>'



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
    fig.add_vline(x=0, line=dict(color="#6A6A6A", width=1))
    fig.update_layout(showlegend=False)
    return ui.layout(fig, height=420, title="Skill percentiles, side by side",
                     margin=dict(l=12, r=18, t=48, b=10))


CSS = f"""<style>
  .card.tape {{ min-height: 480px; box-sizing: border-box; }}
  .best {{ margin-top: 22px; }}
  .best .s {{ margin-bottom: 8px; }}
  .br {{ display: grid; grid-template-columns: 1fr 48px 26px; gap: 10px; align-items: center; padding: 5px 0; }}
  .br span {{ font-size: 13px; color: {ui.INK_2}; }}
  .br i {{ display: block; height: 3px; background: {ui.RAISED}; border-radius: 2px; }}
  .br u {{ display: block; height: 3px; background: {ui.INK_2}; border-radius: 2px; }}
  .br b {{ font-weight: 400; font-size: 13px; text-align: right; font-variant-numeric: tabular-nums; }}
  .tape .t {{ font-size: 18px; }}
  .tape .kv b {{ font-size: 18px; }}
  .st-key-oct_tape [data-testid="stColumn"] > div {{ height: 100%; }}
  .simh {{ font: 500 16px/1.3 {ui.FONT}; color: {ui.INK}; margin: 16px 0 2px; }}
  .sims {{ font-size: 12px; color: {ui.INK_MUTED}; margin-bottom: 6px; }}
  .st-key-ex_sim {{ background: {ui.SURFACE}; border-radius: 10px; padding: 2px 20px 10px; }}
  .st-key-ex_sim .simlist {{ padding: 0; background: transparent; }}
</style>"""


def render(df: pd.DataFrame):
    st.markdown(CSS, unsafe_allow_html=True)
    names = df.sort_values("popularity_index", ascending=False)["fighter"].tolist()
    if "ex_a" not in st.session_state:
        st.session_state["ex_a"] = "Conor McGregor"
    # A row clicked in the table (previous run) becomes Fighter A, applied before the widget exists.
    tbl = st.session_state.get("ex_table_rows")
    sel = (st.session_state.get("ex_table") or {}).get("selection", {}).get("rows", [])
    if sel and tbl and sel[0] < len(tbl):
        picked = tbl[sel[0]]
        if picked != st.session_state.get("ex_last_pick"):
            st.session_state["ex_last_pick"] = picked
            st.session_state["ex_a"] = picked
    a = st.session_state["ex_a"]
    b_opts = [n for n in names if n != a]
    if st.session_state.get("ex_b") == a:
        del st.session_state["ex_b"]
    b = st.session_state.get("ex_b") or ("Khabib Nurmagomedov" if "Khabib Nurmagomedov" in b_opts else b_opts[0])
    fa = df[df["fighter"] == a].iloc[0]
    fb = df[df["fighter"] == b].iloc[0]
    h = _h2h(df, a, b)
    reach = (f"{escape(a)} has <b>{abs(h['reach_gap']):.0f} cm</b> {'more' if h['reach_gap'] > 0 else 'less'} reach"
             if h["reach_gap"] not in (None, 0) else "Reach is even")
    ui.page_header(f"{a} vs {b}",
                   f"{escape(h['geometry'])}. {escape(a)} leads on <b>{h['wins_a']}</b> of 9 skills and "
                   f"{escape(b)} on <b>{h['wins_b']}</b>. {reach}.")

    c1, c2 = st.columns(2)
    c1.selectbox("Red corner", names, key="ex_a")
    c2.selectbox("Blue corner", b_opts, index=b_opts.index(b), key="ex_b")

    # 12 columns: tape 3 | octagon 6 | tape 3
    with st.container(key="oct_tape"):
        left, mid, right = st.columns([3, 6, 3], gap="small")
    with left:
        st.markdown(_tape(fa, A_COLOR, h["table"].set_index("skill")["a"].nlargest(3)), unsafe_allow_html=True)
    with right:
        st.markdown(_tape(fb, B_COLOR, h["table"].set_index("skill")["b"].nlargest(3)), unsafe_allow_html=True)
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

    g1, g2 = st.columns([7, 5], gap="small")
    with g1:
        ui.chart(_butterfly(h, a, b), key="ex_fly")
    with g2, st.container(key="ex_sim", height=432, border=False):
        st.markdown(f'<div class="simh">Fights most like {escape(a)}</div><div class="sims">Nearest on all '
                    'nine UFC skill percentiles plus height and reach, out of 100.</div>', unsafe_allow_html=True)
        sim = _similar(df, a)
        rows = "".join(
            f'<div class="simrow"><div><b>{escape(r.fighter)}</b><span>{escape(r.weight_class)}, '
            f'{escape(r.stance.lower())}, {escape(r.fighting_style.lower())}</span></div>'
            f'<div class="simbar"><i style="width:{r.similarity:.0f}%"></i></div>'
            f'<em>{r.similarity:.0f}</em></div>' for r in sim.itertuples())
        st.markdown(f'<div class="simlist">{rows}</div>', unsafe_allow_html=True)
        st.caption("Percentiles compare each fighter with the 117 here: a style comparison, not a prediction.")

    ui.section("All fighters", "Click a row to put that fighter in the red corner.")
    v = _filters(df)
    table = v.sort_values("popularity_index", ascending=False)[
        ["fighter", "stance", "hand", "weight_class", "country", "wins", "losses", "win_rate",
         "height_cm", "reach_cm", "str_acc", "sapm", "td_avg", "popularity_index"]]
    st.session_state["ex_table_rows"] = table["fighter"].tolist()
    st.caption(f"{len(table)} of {len(df)} fighters")
    st.dataframe(
        table, hide_index=True, width="stretch", height=420, on_select="rerun",
        selection_mode="single-row", key="ex_table",
        column_config={
            "fighter": "Fighter", "stance": "Stance", "hand": "Hand", "weight_class": "Division",
            "country": "Country", "wins": "W", "losses": "L",
            "win_rate": st.column_config.NumberColumn("Win rate", format="%.0f%%"),
            "height_cm": st.column_config.NumberColumn("Height", format="%.0f cm"),
            "reach_cm": st.column_config.NumberColumn("Reach", format="%.0f cm"),
            "str_acc": st.column_config.NumberColumn("Str. acc", format="%.0f%%"),
            "sapm": st.column_config.NumberColumn("Absorbed/min", format="%.2f"),
            "td_avg": st.column_config.NumberColumn("TD/15", format="%.2f"),
            "popularity_index": st.column_config.NumberColumn("Popularity", format="%d"),
        })
    st.download_button("Download this view as CSV", table.to_csv(index=False).encode(),
                       "ufc_fighters.csv", "text/csv")
