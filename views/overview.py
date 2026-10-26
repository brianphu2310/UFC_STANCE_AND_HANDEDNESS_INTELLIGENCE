"""Dashboard: does the side a fighter leads with change how often they win?

The title row states the finding. A strip of sample counts, then the answer (median win rate by
stance over the spread) beside the tests that say whether the gap is real, then how stance and
hand are distributed, then where the fighters come from and how their styles differ.
Filters live behind one button in the title row; every block and every test follows them.
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
SC = dict(zip(STANCES, ui.PALETTE))            # red, blue, gold
CONTINENTS = ["Africa", "Asia", "Europe", "North America", "Oceania", "South America"]
ALL = "All"
H_GLOBE = 372
MINI_H = 196


# =============================================================== filters
def _filters(df):
    """The filter set behind one button in the title row; the button counts the filters that are on."""
    on = sum(st.session_state.get(k, ALL) != ALL for k in ("ov_wc", "ov_st", "ov_hand", "ov_foot", "ov_style"))
    with st.popover(f"Filters, {on} on" if on else "Filters", width="content"):
        divs = [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])]
        f = dict(
            weight_class=st.selectbox("Weight class", [ALL] + divs, key="ov_wc"),
            stance=st.selectbox("Stance", [ALL] + STANCES, key="ov_st"),
            hand=st.selectbox("Dominant hand", [ALL, "Right", "Left"], key="ov_hand"),
            foot=st.selectbox("Dominant foot (estimated)", [ALL, "Right", "Left"], key="ov_foot"),
            fighting_style=st.selectbox("Fighting style", [ALL] + core.STYLES, key="ov_style"),
        )
        names = st.slider("Names per country on the globe", 1, 6, 3, key="ov_names")
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
    fig.update_layout(showlegend=False)
    st.markdown(f'<div class="mt">{escape(title)}</div><div class="ms">{sub}</div>',
                unsafe_allow_html=True)
    return fig


def _stance_words():
    return ", ".join(f'<span style="color:{ui.text_color(SC[s])};font-weight:600">{s.lower()}</span>'
                     for s in STANCES)


# =============================================================== the finding
def finding(v) -> str:
    n = len(v)
    other = v["stance"].isin(["Southpaw", "Switch"])
    share = other.mean() if n else 0
    if other.sum() >= 3 and (~other).sum() >= 3:
        a, b = v.loc[other, "win_rate"].median(), v.loc[~other, "win_rate"].median()
        how = ("about as often as orthodox fighters" if abs(a - b) < 3 else
               f"{abs(a - b):.0f} points {'more' if a > b else 'less'} often than orthodox fighters")
        return (f"<b>{share:.0%}</b> of these {n} fighters lead with the other side, and they win {how}: "
                f"a median of <b>{a:.0f}%</b> against <b>{b:.0f}%</b>.")
    return f"{n} fighters in this view, too few southpaws or orthodox fighters to compare."


def answer(v):
    """The screen's answer: the median win rate of each stance, in its corner colour."""
    cells = "".join(
        f'<div><span><i class="dot" style="background:{SC[s]}"></i>{s}</span>'
        f'<b>{v.loc[v["stance"] == s, "win_rate"].median():.0f}%</b>'
        f'<small>{(v["stance"] == s).sum()} fighters</small></div>'
        if (v["stance"] == s).sum() else
        f'<div><span><i class="dot" style="background:{SC[s]}"></i>{s}</span><b class="na">—</b>'
        f'<small>0 fighters</small></div>' for s in STANCES)
    st.markdown(f'<div class="cardh">Median career win rate by stance</div><div class="ans">{cells}</div>',
                unsafe_allow_html=True)


def counts(v):
    items = [("Fighters", len(v)), ("Countries", v["country"].nunique()),
             ("Orthodox", int((v["stance"] == "Orthodox").sum())), ("Southpaw", int((v["stance"] == "Southpaw").sum())),
             ("Switch", int((v["stance"] == "Switch").sum())), ("Left-handed", int((v["hand"] == "Left").sum())),
             ("Pro fights", int(v["total_fights"].sum()))]
    cells = "".join(f'<div><span>{escape(a)}</span><b>{b:,}</b></div>' for a, b in items)
    st.markdown(f'<div class="strip">{cells}</div>', unsafe_allow_html=True)


TESTS = [("Southpaw vs orthodox", lambda v: v["stance"] == "Southpaw", lambda v: v["stance"] == "Orthodox"),
         ("Switch vs single stance", lambda v: v["stance"] == "Switch", lambda v: v["stance"] != "Switch"),
         ("Left- vs right-handed", lambda v: v["hand"] == "Left", lambda v: v["hand"] == "Right")]


def tests(v):
    """Welch tests on career win rate for the three headline comparisons, Holm-adjusted together."""
    res = []
    for label, ma, mb in TESTS:
        try:
            res.append((label, core.compare_groups(v, ma(v), mb(v), "a", "b")))
        except ValueError:
            res.append((label, None))
    ok = [r for _, r in res if r]
    holm = iter(core.holm_adjust([r.welch_p for r in ok])) if ok else iter([])
    span = 15.0
    rows = ""
    for label, r in res:
        if r is None:
            rows += (f'<div class="tr"><div><b>{escape(label)}</b><span>Too few fighters in this view</span></div>'
                     '<div class="ci"></div><div class="tv">—</div></div>')
            continue
        hp = next(holm)
        x = lambda d: 50 + 50 * max(-span, min(span, d)) / span
        lo, hi, mid = x(r.ci_low), x(r.ci_high), x(r.diff)
        rows += (f'<div class="tr"><div><b>{escape(label)}</b><span>n = {r.n_a} vs {r.n_b} · '
                 f'd = {r.d:+.2f}, {core.effect_label(r.d)}</span></div>'
                 f'<div class="ci" title="95% bootstrap interval {r.ci_low:+.1f} to {r.ci_high:+.1f} points">'
                 f'<i style="left:{lo:.1f}%;width:{max(hi - lo, .8):.1f}%"></i><u style="left:{mid:.1f}%"></u></div>'
                 f'<div class="tv"><b>{r.diff:+.1f}</b><span>p = {ui.fmt_p(r.welch_p)}<br>Holm {ui.fmt_p(hp)}</span></div></div>')
    sig = [label for (label, r) in res if r and r.welch_p < .05]
    verdict = ("None of the three gaps is distinguishable from chance: every interval crosses zero."
               if not sig else f"{', '.join(sig)} clears p < 0.05 before correction; check the Holm value.")
    st.markdown(f'<div class="cardh">Is the gap real?</div><div class="tsub">Difference in mean career win rate, '
                f'percentage points, with its 95% bootstrap interval on a ±{span:.0f}-point axis.</div>'
                f'<div class="tests">{rows}</div><div class="verdict">{escape(verdict)} Small groups make the intervals '
                'wide; see Analysis for power and every grouping.</div>', unsafe_allow_html=True)


def stance_hand(v):
    order = [s for s in STANCES if (v["stance"] == s).any()]
    fig = go.Figure()
    for hand, col in [("Right", "#5A5A63"), ("Left", ui.ACCENT)]:
        n = [int(((v["stance"] == s) & (v["hand"] == hand)).sum()) for s in order]
        fig.add_bar(y=order, x=n, orientation="h", name=f"{hand}-handed", marker=dict(color=col, line=dict(width=0)),
                    text=[str(k) if k else "" for k in n], textposition="inside", insidetextanchor="middle",
                    textfont=dict(color="#fff", size=12),
                    hovertemplate=f"%{{y}}, {hand.lower()}-handed: %{{x}} fighters<extra></extra>")
    fig.update_layout(barmode="stack", bargap=.35, yaxis=dict(autorange="reversed", showgrid=False),
                      xaxis=dict(title="fighters", showgrid=True), showlegend=True,
                      legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom"))
    ui.layout(fig, height=236, margin=dict(l=4, r=10, t=30, b=6))
    st.markdown(f'<div class="mt">Stance and dominant hand</div><div class="ms">Fighters per stance, split by '
                'dominant hand. A right-handed southpaw leads with his strong hand.</div>', unsafe_allow_html=True)
    ui.chart(fig, key="p_sh")


# =============================================================== right column charts
def split_bar(v, selected, bar=True):
    n = max(len(v), 1)
    segs = "".join(
        f'<div style="flex:{c};background:{SC[s]};color:{ui.on_color(SC[s])}" title="{s}">'
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
    st.markdown((f'<div class="split" role="img" aria-label="Stance split">{segs}</div>' if bar else "") + sel,
                unsafe_allow_html=True)


def winrate_curves(v):
    fig = go.Figure()
    xs = np.linspace(45, 102, 160)
    for s in STANCES:
        w = v.loc[v["stance"] == s, "win_rate"].dropna()
        if len(w) < 3:
            continue
        y = gaussian_kde(w)(xs)
        fig.add_scatter(x=xs, y=y, mode="lines", line=dict(color=SC[s], width=2), fill="tozeroy",
                        fillcolor=_rgba(SC[s], .05), name=s,
                        hovertemplate=f"{s}: median {w.median():.0f}%<extra></extra>")
    fig.update_layout(xaxis=dict(ticksuffix="%", range=[45, 102], dtick=10, showgrid=False),
                      yaxis=dict(visible=False))
    ui.chart(_mini(fig, "", f"How career win rates spread for {_stance_words()}. Hover for each median.",
                   height=262), key="p_kde")


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
                        mode="lines", line=dict(color=ui.RAISED, width=4), hoverinfo="skip")
        for s, x in means.items():
            fig.add_scatter(x=[x], y=[label], mode="markers", name=s,
                            marker=dict(color=SC[s], size=10, line=dict(color=ui.SURFACE, width=2)),
                            hovertemplate=f"{s}, {label.lower()}: %{{x:.0f}}th percentile<extra></extra>")
    fig.add_vline(x=50, line=dict(color=ui.INK_MUTED, width=1, dash="dot"))
    fig.update_layout(xaxis=dict(range=[25, 75], ticksuffix="th", dtick=25, showgrid=False),
                      yaxis=dict(autorange="reversed", showgrid=False))
    ui.chart(_mini(fig, "Where the styles differ", f"Average skill percentile for {_stance_words()}",
                   height=262),
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
    fig.add_vline(x=0, line=dict(color=ui.INK_MUTED, width=1))
    ui.chart(_mini(fig, "Reach beyond height",
                   f'Reach minus height: <span style="color:{ui.text_color(SC["Orthodox"])};font-weight:600">'
                   f'orthodox</span> left, <span style="color:{ui.text_color(SC["Southpaw"])};font-weight:600">'
                   'southpaw</span> right', height=262), key="p_fly")


def hand_foot(v):
    g = v.groupby(["foot", "hand"])["win_rate"].agg(["size", "mean"]).reset_index()
    x = g["hand"].map({"Right": 0, "Left": 1})
    y = g["foot"].map({"Right": 1, "Left": 0})
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="markers+text", text=g["size"].astype(str),
        textfont=dict(color=[ui.on_color("#3A3A3A" if m < 77.5 else "#E6E6E6") for m in g["mean"]],
                      size=12, family=ui.FONT),
        marker=dict(size=np.sqrt(g["size"]) * 3.6 + 16, color=g["mean"],
                    colorscale=[[0, "#3A3A3A"], [1, "#E6E6E6"]],
                    cmin=70, cmax=85, line=dict(width=0), showscale=False),
        customdata=np.stack([g["foot"], g["hand"], g["mean"]], axis=1),
        hovertemplate="%{customdata[0]} foot, %{customdata[1]} hand: %{text} fighters, "
                      "%{customdata[2]:.0f}% wins<extra></extra>"))
    fig.update_layout(xaxis=dict(range=[-0.9, 1.9], tickvals=[0, 1], showgrid=False, tickangle=0,
                                 ticktext=["Right<br>hand", "Left<br>hand"]),
                      yaxis=dict(range=[-0.6, 1.6], tickvals=[0, 1], showgrid=False,
                                 ticktext=["Left foot", "Right foot"]))
    ui.chart(_mini(fig, "Hand and foot", "Fighters per pairing; a brighter disc means a higher mean win rate. "
                   "Dominant foot is estimated.", height=232), key="p_bub")


def timeline(v_no_year, years):
    y = v_no_year["debut_year"].dropna().astype(int)
    lo, hi = years
    counts = y.value_counts().reindex(range(1993, 2025), fill_value=0)
    inside = (counts.index >= lo) & (counts.index <= hi)
    fig = go.Figure()
    fig.add_bar(x=counts.index, y=counts.values, marker=dict(
        color=[ui.INK_2 if i else ui.MUTED_FILL for i in inside], line=dict(width=0)),
        hovertemplate="%{x}: %{y} UFC debuts<extra></extra>")
    fig.update_layout(bargap=0.35, xaxis=dict(dtick=4, range=[1992.4, 2024.6], showgrid=False,
                                              tickfont=dict(size=10)),
                      yaxis=dict(visible=False))
    ui.layout(fig, height=100, margin=dict(l=2, r=2, t=2, b=20))
    ui.chart(fig, key="p_time")


CSS = f"""
<style>
  .cardh {{ font: 700 21px/1.1 {ui.DISPLAY}; text-transform: uppercase; letter-spacing: .01em; color: {ui.INK}; margin: 2px 0 12px; }}
  .ans {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  .ans span {{ display: block; font-size: 13px; color: {ui.INK_2}; }}
  .ans b {{ display: block; font: 800 56px/1 {ui.DISPLAY}; color: {ui.INK}; margin-top: 6px; font-variant-numeric: tabular-nums; }}
  .ans b.na {{ font: 400 14px/56px {ui.FONT}; color: {ui.INK_MUTED}; }}
  .ans small {{ font-size: 12px; color: {ui.INK_MUTED}; }}
  .strip {{ display: grid; grid-template-columns: repeat(7, 1fr); background: {ui.SURFACE}; border: 1px solid {ui.BORDER};
            border-radius: 4px; margin-bottom: 16px; }}
  .strip div {{ padding: 14px 18px; border-left: 1px solid {ui.BORDER}; }}
  .strip div:first-child {{ border-left: none; }}
  .strip span {{ display: block; font-size: 12px; color: {ui.INK_MUTED}; letter-spacing: .02em; }}
  .strip b {{ display: block; font: 800 30px/1.1 {ui.DISPLAY}; color: {ui.INK}; margin-top: 4px; font-variant-numeric: tabular-nums; }}
  .tsub {{ font-size: 12px; color: {ui.INK_MUTED}; margin: -6px 0 10px; line-height: 1.45; }}
  .tests {{ border-top: 1px solid {ui.BORDER}; }}
  .tr {{ display: grid; grid-template-columns: 1fr 170px 82px; gap: 14px; align-items: center; padding: 12px 0;
         border-bottom: 1px solid {ui.BORDER}; }}
  .tr b {{ display: block; font: 500 14px/1.3 {ui.FONT}; color: {ui.INK}; }}
  .tr span {{ font-size: 12px; color: {ui.INK_MUTED}; line-height: 1.4; }}
  .ci {{ position: relative; height: 18px; }}
  .ci::before {{ content: ""; position: absolute; left: 0; right: 0; top: 8px; height: 2px; background: {ui.RAISED}; }}
  .ci::after {{ content: ""; position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: {ui.INK_MUTED}; }}
  .ci i {{ position: absolute; top: 6px; height: 6px; background: rgba(229,56,59,.55); }}
  .ci u {{ position: absolute; top: 3px; width: 2px; height: 12px; margin-left: -1px; background: {ui.INK}; }}
  .tv {{ text-align: right; }}
  .tv b {{ font: 800 24px/1 {ui.DISPLAY}; font-variant-numeric: tabular-nums; }}
  .tv span {{ display: block; margin-top: 3px; font-variant-numeric: tabular-nums; }}
  .verdict {{ font-size: 13px; color: {ui.INK_2}; margin-top: 12px; line-height: 1.55; }}
  .mt {{ font: 700 19px/1.1 {ui.DISPLAY}; text-transform: uppercase; letter-spacing: .01em; color: {ui.INK}; margin: 2px 0 0; }}
  .ms {{ color: {ui.INK_MUTED}; font-size: 12px; margin: 4px 0 6px; line-height: 1.45; }}
  .selc {{ font-size: 13px; color: {ui.INK_2}; margin: 8px 0 2px; line-height: 1.45; }}
  .tlh {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-top: 10px; }}
  .tlh b {{ font: 700 16px/1.2 {ui.DISPLAY}; text-transform: uppercase; color: {ui.INK}; }}
  .tlh span {{ font-size: 12px; color: {ui.INK_MUTED}; }}
  .st-key-ovact {{ display: flex; justify-content: flex-end; }}
  .ph {{ margin-bottom: 14px !important; }}
  @media (max-width: 900px) {{ .strip {{ grid-template-columns: repeat(4, 1fr); }}
    .strip div:nth-child(5) {{ border-left: none; }} .strip div:nth-child(n+5) {{ border-top: 1px solid {ui.BORDER}; }} }}
  @media (max-width: 640px) {{ .ans b {{ font-size: 40px; }} .strip {{ grid-template-columns: 1fr 1fr; }}
    .strip div {{ border-left: none !important; border-top: 1px solid {ui.BORDER}; }} .strip div:nth-child(-n+2) {{ border-top: none; }}
    .strip div:nth-child(even) {{ border-left: 1px solid {ui.BORDER} !important; }}
    .strip div:last-child:nth-child(odd) {{ grid-column: 1 / -1; }} .tr {{ grid-template-columns: 1fr 70px; }} .ci {{ display: none; }} }}
</style>"""


def render(df: pd.DataFrame):
    df = df.assign(debut_year=pd.to_datetime(df["first_ufc_fight"], errors="coerce").dt.year)
    st.markdown(CSS, unsafe_allow_html=True)
    y_min, y_max = 1993, 2024
    years = st.session_state.get("ov_years", (y_min, y_max))
    continents = st.session_state.get("ov_cont") or []

    head = st.empty()
    t, act = st.columns([5, 1], vertical_alignment="center")
    with act, st.container(key="ovact"):
        f, names = _filters(df)
    v = _apply(df, f, continents, years)
    v_no_year = _apply(df, f, continents, None)
    with head:
        ui.page_header("Does the lead side decide fights?", finding(v), kicker="Intelligence dashboard")
    on = [x for x in (*[val for val in f.values() if val != ALL], *continents) if x]
    if years != (y_min, y_max):
        on.append(f"debuts {years[0]}–{years[1]}")
    t.caption(f"{len(v)} of {len(df)} fighters in view" + (f": {', '.join(on)}" if on else ", no filters on")
              + ". Every block and test below follows the filters.")

    if v.empty:
        st.markdown('<div class="empty">No fighters match these filters. Open Filters and set one back '
                    'to All.</div>', unsafe_allow_html=True)
        return
    counts(v)

    # 12 columns at 1208px: 7 + 5 with one 16px gutter, so every block lands on the same edges
    l1, r1 = st.columns([7, 5], gap="small")
    with l1, st.container(key="oct_answer", height=470, border=False):
        answer(v)
        winrate_curves(v)
    with r1, st.container(key="oct_tests", height=470, border=False):
        tests(v)

    l2, r2 = st.columns([6, 6], gap="small")
    with l2, st.container(key="oct_sh", height=330, border=False):
        stance_hand(v)
    with r2, st.container(key="oct_hf", height=330, border=False):
        hand_foot(v)

    l3, r3 = st.columns([7, 5], gap="small")
    with l3, st.container(key="oct_globe", border=False):
        st.markdown('<div class="mt">Where they fight from</div><div class="ms">Drag to turn, click a '
                    'country to list its fighters. Brighter countries hold more of them.</div>', unsafe_allow_html=True)
        st.pills("Continents", CONTINENTS, selection_mode="multi", key="ov_cont",
                 label_visibility="collapsed")
        selected = globe3d(country_payload(v), height=H_GLOBE, max_names=names, key="globe")
        if selected in {r["iso3"] for r in country_payload(v)}:
            split_bar(v, selected, bar=False)
        in_range = v["debut_year"].notna().sum()
        st.markdown(f'<div class="tlh"><b>UFC debuts by year</b><span>{in_range} fighters debuted '
                    f'{years[0]}–{years[1]}</span></div>', unsafe_allow_html=True)
        timeline(v_no_year, years)
        st.slider("Debut years", y_min, y_max, (y_min, y_max), key="ov_years",
                  label_visibility="collapsed")
    with r3:
        with st.container(key="oct_styles", border=False):
            fight_profile(v, df)
        with st.container(key="oct_reach", border=False):
            reach_butterfly(v)
