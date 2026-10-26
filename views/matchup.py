"""Matchup lab: two fighters side by side on the attributes the dataset holds. No predictions."""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui
from body3d import body3d

A_COLOR, B_COLOR = ui.ACCENT, ui.STEEL      # fighter A in red, fighter B in steel


@st.cache_data
def _similar(df, name):
    return core.similar_fighters(df, name, n=5)


@st.cache_data
def _h2h(df, a, b):
    return core.head_to_head(df, a, b)


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



ATTRS = [("Career win rate", "win_rate", "{:.0f}%"), ("Pro fights", "total_fights", "{:.0f}"),
         ("UFC fights", "ufc_fights", "{:.0f}"), ("Height", "height_cm", "{:.0f} cm"),
         ("Reach", "reach_cm", "{:.0f} cm"), ("Ape index", "ape_index_cm", "{:+.0f} cm"),
         ("Strikes landed / min", "slpm", "{:.2f}"), ("Strikes absorbed / min", "sapm", "{:.2f}"),
         ("Takedowns / 15 min", "td_avg", "{:.2f}")]


def _attrs(fa, fb, df):
    """Each attribute as two bars from a shared centre line, scaled to the dataset's range."""
    rows = ""
    for label, col, fmt in ATTRS:
        x, y = fa.get(col), fb.get(col)
        lo, hi = df[col].min(), df[col].max()
        def w(v):
            return 0 if pd.isna(v) or hi == lo else 8 + 92 * (v - lo) / (hi - lo)
        def t(v):
            return fmt.format(v) if pd.notna(v) else "—"
        rows += (f'<div class="ar"><b class="va">{t(x)}</b><i class="ba"><u style="width:{w(x):.0f}%"></u></i>'
                 f'<span>{escape(label)}</span><i class="bb"><u style="width:{w(y):.0f}%"></u></i>'
                 f'<b class="vb">{t(y)}</b></div>')
    return f'<div class="attrs">{rows}</div>'


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
  @media (max-width: 900px) {{ .card.tape {{ min-height: 0; }} }}
  .tape .t {{ font-size: 24px; }}
  .tape .kv b {{ font-size: 18px; }}
  .best {{ margin-top: 22px; }}
  .best .s {{ margin-bottom: 8px; }}
  .br {{ display: grid; grid-template-columns: 1fr 48px 26px; gap: 10px; align-items: center; padding: 5px 0; }}
  .br span {{ font-size: 13px; color: {ui.INK_2}; }}
  .br i {{ display: block; height: 3px; background: {ui.RAISED}; }}
  .br u {{ display: block; height: 3px; background: {ui.INK_2}; }}
  .br b {{ font-weight: 500; font-size: 13px; text-align: right; font-variant-numeric: tabular-nums; }}
  .simh {{ font: 700 19px/1.1 {ui.DISPLAY}; text-transform: uppercase; color: {ui.INK}; margin: 14px 0 4px; }}
  .sims {{ font-size: 12px; color: {ui.INK_MUTED}; margin-bottom: 6px; }}
  .st-key-ex_sim {{ background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 4px; padding: 2px 20px 10px; }}
  .attrs {{ background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 4px; padding: 8px 20px; }}
  .ar {{ display: grid; grid-template-columns: 90px 1fr 190px 1fr 90px; gap: 14px; align-items: center;
         padding: 9px 0; border-bottom: 1px solid {ui.BORDER}; }}
  .ar:last-child {{ border-bottom: none; }}
  .ar span {{ text-align: center; font-size: 13px; color: {ui.INK_2}; }}
  .ar b {{ font-weight: 500; font-size: 14px; font-variant-numeric: tabular-nums; }}
  .ar .va {{ text-align: right; }} .ar .vb {{ text-align: left; }}
  .ar i {{ display: flex; height: 6px; background: {ui.RAISED}; }}
  .ar .ba {{ justify-content: flex-end; }} .ar .ba u {{ background: {A_COLOR}; }} .ar .bb u {{ background: {B_COLOR}; }}
  .ar u {{ display: block; height: 6px; transition: width .4s cubic-bezier(.2,.7,.2,1); }}
  @media (max-width: 640px) {{ .ar {{ grid-template-columns: 56px 1fr 56px; gap: 8px; }} .ar i {{ display: none; }}
    .ar span {{ grid-column: 2; grid-row: 1; }} .ar .vb {{ text-align: right; }} }}
</style>"""


def render(df: pd.DataFrame):
    st.markdown(CSS, unsafe_allow_html=True)
    names = df.sort_values("popularity_index", ascending=False)["fighter"].tolist()
    if st.session_state.get("ex_a") not in names:
        st.session_state["ex_a"] = "Conor McGregor"
    a = st.session_state["ex_a"]
    b_opts = [n for n in names if n != a]
    if st.session_state.get("ex_b") not in b_opts:
        st.session_state["ex_b"] = "Khabib Nurmagomedov" if "Khabib Nurmagomedov" in b_opts else b_opts[0]
    b = st.session_state["ex_b"]
    fa = df[df["fighter"] == a].iloc[0]
    fb = df[df["fighter"] == b].iloc[0]
    h = _h2h(df, a, b)
    reach = (f"{escape(a)} has <b>{abs(h['reach_gap']):.0f} cm</b> {'more' if h['reach_gap'] > 0 else 'less'} reach"
             if h["reach_gap"] not in (None, 0) else "Reach is even")
    ui.page_header(f"{a} vs {b}",
                   f"{escape(h['geometry'])}. {escape(a)} is ahead on <b>{h['wins_a']}</b> of 9 skill percentiles "
                   f"and {escape(b)} on <b>{h['wins_b']}</b> (a lead is more than 5 points). {reach}. "
                   "This compares records and styles; it does not predict a result.", kicker="Matchup lab")

    c1, c2 = st.columns(2)
    c1.selectbox("Fighter A", names, key="ex_a")
    c2.selectbox("Fighter B", b_opts, key="ex_b")

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

    ui.section("Tale of the tape", "Bars run from the lowest to the highest value among the 117 fighters. "
               "UFC rates cover UFC bouts only.")
    st.markdown(_attrs(fa, fb, df), unsafe_allow_html=True)

    ui.section("Skills and style", "Percentile against all 117 fighters on the nine skills measured from fight logs.")
    g1, g2 = st.columns([7, 5], gap="small")
    with g1:
        ui.chart(_butterfly(h, a, b), key="ex_fly")
    with g2, st.container(key="ex_sim", height=436, border=False):
        st.markdown(f'<div class="simh">Fights most like {escape(a)}</div><div class="sims">Nearest on the nine '
                    'skill percentiles plus height and reach, scored out of 100.</div>', unsafe_allow_html=True)
        sim = _similar(df, a)
        rows = "".join(
            f'<div class="simrow"><div><b>{escape(r.fighter)}</b><span>{escape(r.weight_class)}, '
            f'{escape(r.stance.lower())}, {escape(r.fighting_style.lower())}</span></div>'
            f'<div class="simbar"><i style="width:{r.similarity:.0f}%"></i></div>'
            f'<em>{r.similarity:.0f}</em></div>' for r in sim.itertuples())
        st.markdown(f'<div class="simlist">{rows}</div>', unsafe_allow_html=True)
