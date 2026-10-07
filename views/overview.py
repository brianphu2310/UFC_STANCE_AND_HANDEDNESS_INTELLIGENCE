"""Overview — one screen.

Left : the finding as a headline, then the globe (the page's one bold element) with continent
       chips and a debut-year strip inside the same octagon-cut panel.
Right: the scoreline (four numbers) and four charts that compare the stances, separated by
       hairlines rather than boxed.
"""
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import gaussian_kde

import ufc_core as core
import ui
from globe3d import ISO3, country_payload, globe3d

STANCES = ["Orthodox", "Southpaw", "Switch"]
SC = dict(zip(STANCES, ui.PALETTE))            # magenta, indigo, tan
CONTINENTS = ["Africa", "Asia", "Europe", "North America", "Oceania", "South America"]
ALL = "All"
H_GLOBE = 372
MINI_H = 196


# =============================================================== filters
def _sidebar(df):
    with st.sidebar:
        st.markdown('<div class="sbh">Filter fighters</div>', unsafe_allow_html=True)
        divs = [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])]
        f = dict(
            weight_class=st.selectbox("Weight class", [ALL] + divs, key="ov_wc"),
            stance=st.selectbox("Stance", [ALL] + STANCES, key="ov_st"),
            hand=st.selectbox("Dominant hand", [ALL, "Right", "Left"], key="ov_hand"),
            foot=st.selectbox("Dominant foot (estimated)", [ALL, "Right", "Left"], key="ov_foot"),
            fighting_style=st.selectbox("Fighting style", [ALL] + core.STYLES, key="ov_style"),
        )
        names = st.slider("Names per country on the globe", 1, 6, 3, key="ov_names")
        st.markdown('<div class="sb-note">Dominant foot is estimated. Everything else comes from '
                    'UFCSTATS, Tapology and Sherdog.</div>', unsafe_allow_html=True)
    return f, names


def _apply(df, f, continents, years):
    v = df
    for col, val in f.items():
        if val != ALL:
            v = v[v[col] == val]
    if continents:
        v = v[v["continent"].isin(continents)]
    if years:
        y = v["debut_year"]
        v = v[y.isna() | y.between(*years)]
    return v


def _rgba(hex_, a):
    h = hex_.lstrip("#")
    return f"rgba({int(h[:2], 16)},{int(h[2:4], 16)},{int(h[4:], 16)},{a})"


def _mini(fig, title, sub, height=MINI_H, **kw):
    ui.layout(fig, height=height, margin=kw.pop("margin", dict(l=4, r=8, t=6, b=4)), **kw)
    fig.update_layout(font=dict(size=10.5), showlegend=False)
    st.markdown(f'<div class="mt">{escape(title)}</div><div class="ms">{sub}</div>',
                unsafe_allow_html=True)
    return fig


def _stance_words():
    return ", ".join(f'<span style="color:{SC[s]};font-weight:600">{s.lower()}</span>'
                     for s in STANCES)


# =============================================================== the finding
def headline(v):
    n = len(v)
    other = v["stance"].isin(["Southpaw", "Switch"])
    share = other.mean() if n else 0
    if other.sum() >= 3 and (~other).sum() >= 3:
        gap = v.loc[other, "win_rate"].mean() - v.loc[~other, "win_rate"].mean()
        if abs(gap) < 3:
            verdict = "They win about as often as everyone else."
        else:
            verdict = f"They win {abs(gap):.0f} points {'more' if gap > 0 else 'less'} often here."
    else:
        verdict = "Too few of them in this view to compare."
    st.markdown(f"""
    <div class="ph" style="margin-bottom:10px">
      <h1>{share:.0%} of these fighters lead with the other side. {escape(verdict)}</h1>
    </div>""", unsafe_allow_html=True)


def scoreline(v):
    n = max(len(v), 1)
    items = [
        (f"{(v['stance'] == 'Southpaw').sum() / n:.0%}", "southpaw"),
        (f"{(v['stance'] == 'Switch').sum() / n:.0%}", "switch"),
        (f"{(v['hand'] == 'Left').sum() / n:.0%}", "left-handed"),
        (f"{v['win_rate'].median():.0f}%" if len(v) else "—", "median wins"),
    ]
    cells = "".join(f'<div><b>{a}</b><span>{escape(b)}</span></div>' for a, b in items)
    st.markdown(f'<div class="score4">{cells}</div>'
                f'<div class="scope">{len(v)} fighters from {v["country"].nunique()} countries '
                f'in this view</div>', unsafe_allow_html=True)


# =============================================================== right column charts
def split_bar(v, selected):
    n = max(len(v), 1)
    segs = "".join(
        f'<div style="flex:{c};background:{SC[s]}" title="{s}">'
        f'{"<span>" + s + "</span>" if c / n > .2 else ""}<b>{c / n:.0%}</b></div>'
        for s in STANCES if (c := (v["stance"] == s).sum()))
    sel = ""
    if selected:
        name = next((c for c, iso in ISO3.items() if iso == selected), None)
        pool = v[v["country"] == name].sort_values("popularity_index", ascending=False)
        if len(pool):
            names = ", ".join(pool["fighter"].head(8)) + (f" and {len(pool) - 8} more"
                                                          if len(pool) > 8 else "")
            sel = (f'<div class="selc"><b>{escape(name)}</b>, {len(pool)} fighters: '
                   f'{escape(names)}</div>')
    st.markdown(f'<div class="split">{segs}</div>{sel}', unsafe_allow_html=True)


def winrate_curves(v):
    fig = go.Figure()
    xs = np.linspace(45, 102, 160)
    for s in STANCES:
        w = v.loc[v["stance"] == s, "win_rate"].dropna()
        if len(w) < 3:
            continue
        y = gaussian_kde(w)(xs)
        fig.add_scatter(x=xs, y=y, mode="lines", line=dict(color=SC[s], width=2), fill="tozeroy",
                        fillcolor=_rgba(SC[s], .16), name=s,
                        hovertemplate=f"{s}: median {w.median():.0f}%<extra></extra>")
    fig.update_layout(xaxis=dict(ticksuffix="%", range=[45, 102], dtick=10, showgrid=False),
                      yaxis=dict(visible=False))
    ui.chart(_mini(fig, "Win rates overlap almost completely",
                   f"Spread of career win rate for {_stance_words()}"), key="p_kde")


def fight_profile(v, full):
    metrics = [("slpm", "Output"), ("str_acc", "Accuracy"), ("str_def", "Defence"),
               ("td_avg", "Takedowns"), ("ctrl_pct", "Control")]
    pct = {m: full[m].rank(pct=True) * 100 for m, _ in metrics}
    fig = go.Figure()
    for m, label in metrics:
        means = {s: pct[m][v.index[v["stance"] == s]].mean() for s in STANCES}
        means = {s: x for s, x in means.items() if pd.notna(x)}
        if not means:
            continue
        fig.add_scatter(x=[min(means.values()), max(means.values())], y=[label, label],
                        mode="lines", line=dict(color=ui.BORDER, width=5), hoverinfo="skip")
        for s, x in means.items():
            fig.add_scatter(x=[x], y=[label], mode="markers", name=s,
                            marker=dict(color=SC[s], size=10, line=dict(color=ui.SURFACE, width=2)),
                            hovertemplate=f"{s}, {label.lower()}: %{{x:.0f}}th percentile<extra></extra>")
    fig.add_vline(x=50, line=dict(color=ui.RULE, width=1, dash="dot"))
    fig.update_layout(xaxis=dict(range=[25, 75], ticksuffix="th", dtick=25, showgrid=False),
                      yaxis=dict(autorange="reversed", showgrid=False))
    ui.chart(_mini(fig, "Where the styles differ", f"Average skill percentile for {_stance_words()}"),
             key="p_dumb")


def reach_butterfly(v):
    bins = np.arange(-10, 22.5, 2.5)
    fig = go.Figure()
    for s, sign in [("Orthodox", -1), ("Southpaw", 1)]:
        a = v.loc[v["stance"] == s, "ape_index_cm"].dropna()
        if a.empty:
            continue
        h, _ = np.histogram(a, bins=bins)
        share = h / max(len(a), 1) * 100
        fig.add_bar(y=bins[:-1] + 1.25, x=sign * share, orientation="h", name=s,
                    marker=dict(color=SC[s], line=dict(width=0)), customdata=share,
                    hovertemplate=f"{s}: %{{customdata:.0f}}% have reach %{{y:+.0f}} cm vs height"
                                  "<extra></extra>")
    fig.update_layout(barmode="overlay", bargap=0.15,
                      xaxis=dict(tickvals=[-25, 0, 25], showgrid=False, tickangle=0,
                                 ticktext=["25%", "0", "25%"]),
                      yaxis=dict(ticksuffix=" cm", dtick=10))
    fig.add_vline(x=0, line=dict(color=ui.RULE, width=1))
    ui.chart(_mini(fig, "Reach beyond height",
                   f'Reach minus height: <span style="color:{SC["Orthodox"]};font-weight:600">'
                   f'orthodox</span> left, <span style="color:{SC["Southpaw"]};font-weight:600">'
                   'southpaw</span> right'), key="p_fly")


def hand_foot(v):
    g = v.groupby(["foot", "hand"])["win_rate"].agg(["size", "mean"]).reset_index()
    x = g["hand"].map({"Right": 0, "Left": 1})
    y = g["foot"].map({"Right": 1, "Left": 0})
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="markers+text", text=g["size"].astype(str),
        textfont=dict(color=ui.INK, size=12, family=ui.DISPLAY),
        marker=dict(size=np.sqrt(g["size"]) * 3.6 + 16, color=g["mean"], colorscale=ui.SEQ_BLUE,
                    cmin=70, cmax=85, line=dict(width=0), showscale=False),
        customdata=np.stack([g["foot"], g["hand"], g["mean"]], axis=1),
        hovertemplate="%{customdata[0]} foot, %{customdata[1]} hand: %{text} fighters, "
                      "%{customdata[2]:.0f}% wins<extra></extra>"))
    fig.update_layout(xaxis=dict(range=[-0.9, 1.9], tickvals=[0, 1], showgrid=False, tickangle=0,
                                 ticktext=["Right<br>hand", "Left<br>hand"]),
                      yaxis=dict(range=[-0.6, 1.6], tickvals=[0, 1], showgrid=False,
                                 ticktext=["Left foot", "Right foot"]))
    ui.chart(_mini(fig, "Hand and foot", "Fighters per pairing, brighter means a higher win rate. "
                   "Foot is estimated."), key="p_bub")


def timeline(v_no_year, years):
    y = v_no_year["debut_year"].dropna().astype(int)
    lo, hi = years
    counts = y.value_counts().reindex(range(1993, 2025), fill_value=0)
    inside = (counts.index >= lo) & (counts.index <= hi)
    fig = go.Figure()
    fig.add_bar(x=counts.index, y=counts.values, marker=dict(
        color=[ui.ACCENT if i else "#3A2D57" for i in inside], line=dict(width=0)),
        hovertemplate="%{x}: %{y} UFC debuts<extra></extra>")
    fig.update_layout(bargap=0.35, xaxis=dict(dtick=4, range=[1992.4, 2024.6], showgrid=False,
                                              tickfont=dict(size=10)),
                      yaxis=dict(visible=False))
    ui.layout(fig, height=100, margin=dict(l=2, r=2, t=2, b=20))
    ui.chart(fig, key="p_time")


CSS = f"""
<style>
  .block-container {{ padding-top: 4.6rem !important; padding-bottom: .4rem !important;
                      max-width: none !important; padding-left: 2rem !important; padding-right: 2rem !important; }}
  div[data-testid="stVerticalBlock"] {{ gap: .5rem; }}
  .ph h1 {{ font-size: 2.15rem !important; max-width: 30ch; line-height: 1.02 !important; }}
  .sb-note {{ color: {ui.INK_MUTED}; font-size: .74rem; margin-top: 12px; line-height: 1.45; }}

  .score4 {{ display: grid; grid-template-columns: repeat(4, 1fr); margin-top: 4px; }}
  .score4 div {{ padding: 2px 10px 0; border-left: 1px solid {ui.BORDER}; }}
  .score4 div:first-child {{ padding-left: 0; border-left: none; }}
  .score4 b {{ display: block; font-family: {ui.DISPLAY}; font-weight: 800; font-size: 2.3rem;
               line-height: .95; color: {ui.INK}; }}
  .score4 span {{ font-size: .76rem; color: {ui.INK_MUTED}; white-space: nowrap; }}
  .scope {{ font-size: .78rem; color: {ui.INK_MUTED}; margin: 8px 0 4px; }}

  /* the one bold element: globe in an octagon-cut panel */
  .st-key-globepanel {{ position: relative; padding: 10px 18px 4px;
      background: radial-gradient(600px 380px at 50% 42%, rgba(90,84,216,.18), transparent 70%), {ui.SURFACE};
      clip-path: polygon(0 0, calc(100% - 34px) 0, 100% 34px, 100% 100%, 34px 100%, 0 calc(100% - 34px)); }}
  .st-key-globepanel [data-testid="stPlotlyChart"] {{ border: none; background: transparent; }}
  .st-key-globepanel [data-testid="stPills"] label {{ display: none; }}
  .tlh {{ display: flex; justify-content: space-between; align-items: baseline;
          border-top: 1px solid {ui.BORDER}; padding-top: 8px; margin-top: 2px; }}
  .tlh b {{ font-family: {ui.DISPLAY}; font-size: 1.15rem; font-weight: 700; color: {ui.INK}; }}
  .tlh span {{ font-size: .76rem; color: {ui.INK_MUTED}; }}

  /* right column: hairline sections, no boxes */
  .st-key-rightcol [data-testid="stPlotlyChart"] {{ border: none; background: transparent; }}
  .mt {{ font-family: {ui.DISPLAY}; font-weight: 700; font-size: 1.18rem; color: {ui.INK};
         line-height: 1.1; border-top: 1px solid {ui.BORDER}; padding-top: 10px; margin-top: 6px; }}
  .ms {{ color: {ui.INK_MUTED}; font-size: .76rem; margin: 2px 0 2px; line-height: 1.35; }}
  .split {{ display: flex; height: 34px; gap: 2px; margin: 12px 0 4px; }}
  .split div {{ display: flex; justify-content: space-between; align-items: center; padding: 0 9px;
                color: #fff; min-width: 44px; overflow: hidden; white-space: nowrap; }}
  .split span {{ font-size: .74rem; opacity: .9; }}
  .split b {{ font-family: {ui.DISPLAY}; font-size: 1.15rem; font-weight: 800; margin-left: 6px; }}
  .selc {{ font-size: .8rem; color: {ui.INK_2}; margin: 6px 0 2px; line-height: 1.4; }}
  .selc b {{ color: {ui.INK}; }}
</style>"""


def render(df: pd.DataFrame):
    df = df.assign(debut_year=pd.to_datetime(df["first_ufc_fight"], errors="coerce").dt.year)
    st.markdown(CSS, unsafe_allow_html=True)
    f, names = _sidebar(df)
    y_min, y_max = 1993, 2024
    years = st.session_state.get("ov_years", (y_min, y_max))
    continents = st.session_state.get("ov_cont") or []

    v = _apply(df, f, continents, years)
    v_no_year = _apply(df, f, continents, None)

    left, right = st.columns([1.42, 1], gap="large")
    with left:
        headline(v)
        with st.container(key="globepanel"):
            st.pills("Continents", CONTINENTS, selection_mode="multi", key="ov_cont",
                     label_visibility="collapsed")
            selected = globe3d(country_payload(v), height=H_GLOBE, max_names=names, key="globe")
            in_range = v["debut_year"].notna().sum()
            st.markdown(f'<div class="tlh"><b>UFC debuts by year</b><span>{in_range} fighters '
                        f'debuted {years[0]}–{years[1]}. Drag the slider to narrow it.</span></div>',
                        unsafe_allow_html=True)
            timeline(v_no_year, years)
            st.slider("Debut years", y_min, y_max, (y_min, y_max), key="ov_years",
                      label_visibility="collapsed")

    with right:
        with st.container(key="rightcol"):
            scoreline(v)
            if v.empty:
                st.info("No fighters match these filters. Clear a filter in the sidebar to see more.")
                return
            split_bar(v, selected if selected in {r["iso3"] for r in country_payload(v)} else None)
            a, b = st.columns(2, gap="medium")
            with a:
                winrate_curves(v)
            with b:
                fight_profile(v, df)
            c, d = st.columns(2, gap="medium")
            with c:
                reach_butterfly(v)
            with d:
                hand_foot(v)
