"""Main dashboard — one screen, modelled on a 'story + globe + side panel' layout.

Left : headline · continent picker · big KPI · 3D globe · debut-year timeline with slider
Right: scrollable panel of small, *different* charts that all revolve around stance / hand / foot
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
H_GLOBE = 432
MINI_H = 150


# =============================================================== filters
def _sidebar(df):
    with st.sidebar:
        st.markdown('<div class="sb-brand">Stance<span>Intel</span></div>'
                    '<div class="eyebrow" style="margin-top:14px">Filters</div>',
                    unsafe_allow_html=True)
        divs = [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])]
        f = dict(
            weight_class=st.selectbox("Weight class", [ALL] + divs, key="ov_wc"),
            stance=st.selectbox("Stance", [ALL] + STANCES, key="ov_st"),
            hand=st.selectbox("Dominant hand", [ALL, "Right", "Left"], key="ov_hand"),
            foot=st.selectbox("Dominant foot ≈", [ALL, "Right", "Left"], key="ov_foot"),
            fighting_style=st.selectbox("Fighting style", [ALL] + core.STYLES, key="ov_style"),
        )
        names = st.slider("Names per country on the globe", 1, 6, 3, key="ov_names")
        st.markdown('<div class="sb-note">≈ estimated field · all other data from UFCSTATS, '
                    'Tapology & Sherdog</div>', unsafe_allow_html=True)
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


# =============================================================== small helpers
def _mini(fig, title, sub=None, height=MINI_H, **kw):
    ui.layout(fig, height=height, margin=kw.pop("margin", dict(l=6, r=10, t=8, b=6)), **kw)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(size=10.5), showlegend=kw.get("showlegend", False))
    st.markdown(f'<div class="mt">{escape(title)}</div>'
                + (f'<div class="ms">{escape(sub)}</div>' if sub else ""), unsafe_allow_html=True)
    return fig


def _legend_html(items):
    return " ".join(f'<span class="lg"><i style="background:{c}"></i>{escape(n)}</span>'
                    for n, c in items)


# =============================================================== right panel charts
def share_bar(v, selected=None):
    n = max(len(v), 1)
    parts = [(s, (v["stance"] == s).sum()) for s in STANCES]
    segs = "".join(f'<div style="flex:{c};background:{SC[s]}">{c / n:.0%}</div>'
                   for s, c in parts if c)
    sel = ""
    if selected:
        name = next((c for c, iso in ISO3.items() if iso == selected), None)
        pool = v[v["country"] == name].sort_values("popularity_index", ascending=False)
        if len(pool):
            sel = (f'<div class="ms" style="margin-top:2px"><b style="color:{ui.INK}">{escape(name)}</b>'
                   f' · {escape(", ".join(pool["fighter"].head(6)))}'
                   f'{" …" if len(pool) > 6 else ""}</div>')
    st.markdown(f"""
    <div class="mt" style="margin-top:0">Orthodox vs southpaw vs switch</div>
    <div class="ms">{_legend_html([(s, SC[s]) for s in STANCES])}</div>
    <div class="sharebar">{segs}</div>{sel}""", unsafe_allow_html=True)


def winrate_curves(v):
    fig = go.Figure()
    xs = np.linspace(45, 100, 160)
    for s in STANCES:
        w = v.loc[v["stance"] == s, "win_rate"].dropna()
        if len(w) < 3:
            continue
        y = gaussian_kde(w)(xs)
        fill = SC[s].replace("#", "")
        rgba = f"rgba({int(fill[:2], 16)},{int(fill[2:4], 16)},{int(fill[4:], 16)},0.22)"
        fig.add_scatter(x=xs, y=y, mode="lines", line=dict(color=SC[s], width=2), fill="tozeroy",
                        fillcolor=rgba, name=s,
                        hovertemplate=f"{s}<br>win rate %{{x:.0f}}%<extra></extra>")
        fig.add_vline(x=w.median(), line=dict(color=SC[s], width=1, dash="dot"))
    fig.update_layout(xaxis=dict(ticksuffix="%", range=[45, 100]), yaxis=dict(visible=False))
    ui.chart(_mini(fig, "Win-rate curves", "Density · dotted = median"), key="p_kde")


def striking_dumbbell(v, full):
    metrics = [("slpm", "Output"), ("str_acc", "Accuracy"), ("str_def", "Defence"),
               ("td_avg", "Takedowns"), ("td_def", "TD defence"), ("ctrl_pct", "Control")]
    pct = {m: full[m].rank(pct=True) * 100 for m, _ in metrics}
    fig = go.Figure()
    for m, label in metrics:
        means = {s: pct[m][v.index[v["stance"] == s]].mean() for s in STANCES}
        means = {s: x for s, x in means.items() if pd.notna(x)}
        if not means:
            continue
        fig.add_scatter(x=[min(means.values()), max(means.values())], y=[label, label],
                        mode="lines", line=dict(color="#3B2C5E", width=6), hoverinfo="skip",
                        showlegend=False)
        for s, x in means.items():
            fig.add_scatter(x=[x], y=[label], mode="markers", name=s, showlegend=False,
                            marker=dict(color=SC[s], size=11, line=dict(color=ui.SURFACE, width=2)),
                            hovertemplate=f"{s} · {label}: %{{x:.0f}}th pct<extra></extra>")
    fig.update_layout(xaxis=dict(range=[20, 80], ticksuffix="th", dtick=20),
                      yaxis=dict(autorange="reversed"))
    ui.chart(_mini(fig, "Fight profile", "Mean skill percentile"), key="p_dumb")


def hand_foot_bubbles(v):
    g = v.groupby(["foot", "hand"])["win_rate"].agg(["size", "mean"]).reset_index()
    x = g["hand"].map({"Right": 0, "Left": 1})
    y = g["foot"].map({"Right": 1, "Left": 0})
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="markers+text", text=g["size"].astype(str),
        textfont=dict(color="#fff", size=11),
        marker=dict(size=np.sqrt(g["size"]) * 5 + 16, color=g["mean"], colorscale=ui.SEQ_BLUE,
                    cmin=70, cmax=85, line=dict(color=ui.RULE, width=1), showscale=False,
                    opacity=0.95),
        customdata=np.stack([g["foot"], g["hand"], g["mean"]], axis=1),
        hovertemplate="%{customdata[0]} foot · %{customdata[1]} hand<br>%{text} fighters · "
                      "%{customdata[2]:.0f}% wins<extra></extra>"))
    fig.update_layout(xaxis=dict(range=[-0.6, 1.6], tickvals=[0, 1], ticktext=["R hand", "L hand"],
                                 showgrid=False, zeroline=False, tickangle=0),
                      yaxis=dict(range=[-0.6, 1.6], tickvals=[0, 1], ticktext=["L foot", "R foot"],
                                 showgrid=False, zeroline=False))
    ui.chart(_mini(fig, "Hand × foot ≈", "Size = fighters · colour = win rate"), key="p_bub")


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
                    hovertemplate=f"{s}<br>reach − height %{{y:+.0f}} cm: %{{customdata:.0f}}%"
                                  "<extra></extra>")
    fig.update_layout(barmode="overlay", bargap=0.12,
                      xaxis=dict(tickvals=[-30, -15, 0, 15, 30],
                                 ticktext=["30%", "15%", "0", "15%", "30%"]),
                      yaxis=dict(title=None, ticksuffix=" cm"))
    fig.add_vline(x=0, line=dict(color=ui.RULE, width=1))
    ui.chart(_mini(fig, "Reach advantage", "Reach − height · orthodox | southpaw"), key="p_fly")


def age_vs_fights(v):
    fig = go.Figure()
    for s in STANCES:
        d = v[v["stance"] == s]
        fig.add_scatter(x=d["age"], y=d["total_fights"], mode="markers", name=s, text=d["fighter"],
                        marker=dict(color=SC[s], size=7, opacity=.9, line=dict(color=ui.SURFACE, width=1)),
                        hovertemplate="<b>%{text}</b><br>age %{x:.0f} · %{y} pro fights<extra></extra>")
    fig.update_layout(xaxis=dict(title=dict(text="age", font=dict(size=10))),
                      yaxis=dict(title=dict(text="pro fights", font=dict(size=10))))
    ui.chart(_mini(fig, "Age vs experience", "Each dot is a fighter"), key="p_age")


def top_bars(v):
    top = v.sort_values("popularity_index", ascending=False).head(5).iloc[::-1]
    k = np.linspace(0, 1, len(top)) if len(top) > 1 else np.array([1.0])
    a, b = np.array([0x5A, 0x54, 0xD8]), np.array([0xC8, 0x62, 0xCE])
    cols = ["#%02X%02X%02X" % tuple((a + (b - a) * t).astype(int)) for t in k]
    fig = go.Figure(go.Bar(
        y=top["fighter"], x=top["popularity_index"], orientation="h",
        marker=dict(color=cols, line=dict(width=0)), text=top["stance"].str[0] + top["hand"].str[0],
        textposition="inside", insidetextanchor="start", textfont=dict(color="#fff", size=10),
        customdata=top[["stance", "hand"]],
        hovertemplate="<b>%{y}</b><br>%{customdata[0]} · %{customdata[1]}-handed<br>"
                      "popularity %{x}<extra></extra>"))
    fig.add_vline(x=top["popularity_index"].mean() if len(top) else 0,
                  line=dict(color=ui.RULE, width=1.5))
    fig.update_layout(xaxis=dict(range=[0, 100]), bargap=0.3)
    ui.chart(_mini(fig, "Most popular", "Popularity index · line = average"), key="p_top")


# =============================================================== left side pieces
def headline(v, df, f, continents):
    sp = v["stance"].isin(["Southpaw", "Switch"]).mean() if len(v) else 0
    scope = []
    if f["weight_class"] != ALL:
        scope.append(f["weight_class"].lower())
    if continents:
        scope.append(" & ".join(continents))
    where = " in " + ", ".join(scope) if scope else " at the top of MMA"
    st.markdown(f"""
    <div class="hl"><span>Southpaws &amp; switch-hitters</span> are rare{escape(where)}</div>
    <div class="hl2">{sp:.0%} of {len(v)} fighters · {v['country'].nunique()} countries</div>""",
                unsafe_allow_html=True)


def kpi_block(v):
    n = max(len(v), 1)
    sp = v["stance"].isin(["Southpaw", "Switch"]).sum()
    lh = (v["hand"] == "Left").sum()
    wr = v["win_rate"].median() if len(v) else float("nan")
    st.markdown(f"""
    <div class="bigkpi">{sp / n * 100:.0f}<small>%</small></div>
    <div class="bigsub">fight southpaw or switch<br>in the current view</div>
    <div class="kmini"><div><b>{lh / n:.0%}</b>left-handed</div><div><b>{wr:.0f}%</b>median win</div></div>
    <div class="glegend">Fighters per country
      <div class="gbar"></div><div class="gends"><span>1</span><span>most</span></div></div>
    """, unsafe_allow_html=True)


def timeline(v_no_year, years):
    y = v_no_year["debut_year"].dropna().astype(int)
    lo, hi = years
    counts = y.value_counts().reindex(range(1993, 2025), fill_value=0)
    inside = (counts.index >= lo) & (counts.index <= hi)
    fig = go.Figure()
    for yr, c, ins in zip(counts.index, counts.values, inside):
        if c:
            fig.add_scatter(x=[yr, yr], y=[0, c], mode="lines", hoverinfo="skip", showlegend=False,
                            line=dict(color=ui.ACCENT if ins else "#3B2C5E", width=3))
    fig.add_scatter(x=counts.index[counts.values > 0], y=counts.values[counts.values > 0],
                    mode="markers", showlegend=False,
                    marker=dict(size=10, color=[ui.ACCENT if i else "#4A3A70" for i in
                                                inside[counts.values > 0]],
                                line=dict(color=ui.SURFACE, width=2)),
                    hovertemplate="%{x}: %{y} UFC debuts<extra></extra>")
    fig.add_hline(y=counts[counts > 0].mean() if (counts > 0).any() else 0,
                  line=dict(color=ui.RULE, width=1.2))
    fig.update_layout(xaxis=dict(dtick=4, range=[1992.4, 2024.6], tickfont=dict(size=10),
                                 showgrid=False),
                      yaxis=dict(visible=False))
    ui.layout(fig, height=112, margin=dict(l=4, r=4, t=4, b=4))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    ui.chart(fig, key="p_time")


CSS = f"""
<style>
  .block-container {{ padding-top: 4.4rem !important; padding-bottom: .4rem !important; }}
  div[data-testid="stVerticalBlock"] {{ gap: .55rem; }}
  [data-testid="stSidebarHeader"] {{ height: 1.2rem; padding: 0; }}
  .block-container {{ max-width: none !important; padding-left: 1.4rem !important;
                      padding-right: 1.4rem !important; }}
  .st-key-sidepanel {{ padding: 14px 14px 6px !important; }}
  .st-key-sidepanel div[data-testid="stVerticalBlock"] {{ gap: .2rem; }}
  .sb-brand {{ font-size: 1.15rem; font-weight: 800; color: {ui.INK}; letter-spacing: -.01em; }}
  .sb-brand span {{ color: {ui.ACCENT}; }}
  .sb-note {{ color: {ui.INK_MUTED}; font-size: .72rem; margin-top: 10px; line-height: 1.4; }}
  .hl {{ font-size: 1.62rem; line-height: 1.18; font-weight: 300; color: {ui.INK}; margin: 0 0 4px; }}
  .hl span {{ color: {ui.ACCENT}; font-weight: 500; }}
  .hl2 {{ font-size: 1.05rem; color: {ui.INK_2}; font-weight: 300; margin-bottom: 6px; }}
  .bigkpi {{ font-size: 4.3rem; font-weight: 300; color: {ui.INK}; line-height: 1; margin-top: 16px; }}
  .bigkpi small {{ font-size: 1.3rem; color: {ui.INK_2}; margin-left: 4px; }}
  .bigsub {{ color: {ui.INK_2}; font-size: .86rem; margin-top: 4px; line-height: 1.35; }}
  .kmini {{ display: flex; gap: 16px; margin-top: 12px; }}
  .kmini div {{ color: {ui.INK_MUTED}; font-size: .74rem; }}
  .kmini b {{ display: block; color: {ui.INK}; font-size: 1.05rem; font-weight: 600; }}
  .glegend {{ color: {ui.INK_MUTED}; font-size: .72rem; margin-top: 16px; }}
  .gbar {{ height: 8px; border-radius: 4px; margin: 4px 0 2px; max-width: 170px;
           background: linear-gradient(90deg, #3A2C62, #5A54D8, #C862CE, #F2A6F0); }}
  .gends {{ display: flex; justify-content: space-between; max-width: 170px; }}
  /* card containers (keyed st.container → .st-key-*) */
  .st-key-contcard, .st-key-timecard, .st-key-sidepanel {{
    background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 16px;
    box-shadow: {ui.SHADOW}; }}
  .st-key-contcard {{ padding: 12px 14px 6px; }}
  .st-key-contcard [data-testid="stCheckbox"] {{ margin-bottom: -10px; }}
  .st-key-contcard label p {{ font-size: .84rem; color: {ui.INK_2}; }}
  .st-key-timecard {{ padding: 12px 18px 2px; }}
  .st-key-sidepanel {{ padding: 14px 16px; }}
  .st-key-timecard [data-testid="stPlotlyChart"], .st-key-sidepanel [data-testid="stPlotlyChart"] {{
    box-shadow: none; background: transparent; border-radius: 0; }}
  .tl-title {{ display: flex; gap: 12px; align-items: flex-start; }}
  .tl-icon-unused {{ width: 30px; height: 30px; border-radius: 8px; flex: none; display: grid;
              place-items: center; background: linear-gradient(135deg, {ui.ACCENT_2}, {ui.ACCENT});
              color: #fff; font-size: 15px; }}
  .tl-k {{ color: {ui.INK_MUTED}; font-size: .74rem; }}
  .tl-t {{ color: {ui.INK}; font-weight: 700; font-size: .98rem; line-height: 1.2; }}
  .mt {{ color: {ui.INK}; font-weight: 700; font-size: .92rem; margin-top: 6px; }}
  .ms {{ color: {ui.INK_MUTED}; font-size: .74rem; margin-bottom: 2px; }}
  .lg {{ margin-right: 10px; white-space: nowrap; }}
  .lg i {{ display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; }}
  .sharebar {{ display: flex; height: 26px; border-radius: 6px; overflow: hidden; margin: 8px 0 6px;
               gap: 2px; }}
  .sharebar div {{ display: grid; place-items: center; color: #fff; font-size: .74rem;
                   font-weight: 700; min-width: 34px; }}
  .selcard {{ margin-top: 8px; }}
</style>"""


def render(df: pd.DataFrame):
    df = df.assign(debut_year=pd.to_datetime(df["first_ufc_fight"], errors="coerce").dt.year)
    st.markdown(CSS, unsafe_allow_html=True)
    f, names = _sidebar(df)
    y_min, y_max = 1993, 2024
    years = st.session_state.get("ov_years", (y_min, y_max))
    continents = [c for c in CONTINENTS if st.session_state.get(f"ov_c_{c}")]

    v = _apply(df, f, continents, years)
    v_no_year = _apply(df, f, continents, None)

    left, right = st.columns([1.42, 1], gap="medium")
    with left:
        headline(v, df, f, continents)
        a, b = st.columns([0.9, 2.2], gap="small")
        with a:
            with st.container(key="contcard"):
                for c in CONTINENTS:
                    st.checkbox(c, key=f"ov_c_{c}")
            kpi_block(v)
        with b:
            selected = globe3d(country_payload(v), height=H_GLOBE, max_names=names, key="globe")
        with st.container(key="timecard"):
            t1, t2 = st.columns([1.25, 4.2], gap="small")
            with t1:
                in_range = v["debut_year"].notna().sum()
                st.markdown(f"""<div class="tl-title"><div>
                  <div class="tl-k">UFC debuts per year</div><div class="tl-t">{in_range} fighters
                  </div><div class="tl-k">{years[0]}–{years[1]} · drag the slider</div></div></div>""",
                            unsafe_allow_html=True)
            with t2:
                timeline(v_no_year, years)
            st.slider("Debut years", y_min, y_max, (y_min, y_max), key="ov_years",
                      label_visibility="collapsed")

    with right:
        with st.container(key="sidepanel"):
            if v.empty:
                st.info("No fighters match these filters.")
                return
            share_bar(v, selected)
            r1a, r1b = st.columns(2, gap="small")
            with r1a:
                winrate_curves(v)
            with r1b:
                striking_dumbbell(v, df)
            r2a, r2b = st.columns(2, gap="small")
            with r2a:
                reach_butterfly(v)
            with r2b:
                hand_foot_bubbles(v)
            r3a, r3b = st.columns(2, gap="small")
            with r3a:
                age_vs_fights(v)
            with r3b:
                top_bars(v)
