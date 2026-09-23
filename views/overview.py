"""Main dashboard — one screen: 3D globe in the centre, overview charts around it."""
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui
from globe3d import ISO3, country_payload, globe3d

STANCE_COLORS = dict(zip(["Orthodox", "Southpaw", "Switch"], ui.PALETTE))
ALL = "All"
H_MAIN = 490          # globe height; side charts are H_MAIN / 2 each
H_SMALL = 206         # bottom row


def _sidebar_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    with st.sidebar:
        st.markdown('<div class="eyebrow" style="margin-top:4px">Filters</div>',
                    unsafe_allow_html=True)
        divs = [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])]
        f = dict(
            weight_class=st.selectbox("Weight class", [ALL] + divs, key="ov_wc"),
            stance=st.selectbox("Stance", [ALL, "Orthodox", "Southpaw", "Switch"], key="ov_st"),
            hand=st.selectbox("Dominant hand", [ALL, "Right", "Left"], key="ov_hand"),
            foot=st.selectbox("Dominant foot ≈", [ALL, "Right", "Left"], key="ov_foot",
                              help="Estimated — no public source records dominant foot."),
            fighting_style=st.selectbox("Fighting style", [ALL] + core.STYLES, key="ov_style"),
        )
        names = st.slider("Names shown per country", 1, 6, 3, key="ov_names")
    v = df
    for col, val in f.items():
        if val != ALL:
            v = v[v[col] == val]
    return v, dict(filters=f, names=names)


def _kpi_strip(v: pd.DataFrame, total: int):
    n = max(len(v), 1)
    items = [
        ("Fighters", f"{len(v)}", f"of {total}"),
        ("Countries", f"{v['country'].nunique()}", "on the globe"),
        ("Southpaw", f"{(v['stance'] == 'Southpaw').mean():.0%}" if len(v) else "—",
         f"{(v['stance'] == 'Southpaw').sum()} fighters"),
        ("Switch", f"{(v['stance'] == 'Switch').mean():.0%}" if len(v) else "—",
         f"{(v['stance'] == 'Switch').sum()} fighters"),
        ("Left-handed", f"{(v['hand'] == 'Left').sum() / n:.0%}", f"{(v['hand'] == 'Left').sum()} fighters"),
        ("Left-footed ≈", f"{(v['foot'] == 'Left').sum() / n:.0%}", "estimated"),
        ("Median win rate", f"{v['win_rate'].median():.0f}%" if len(v) else "—",
         f"{int(v['champion'].sum())} champions"),
    ]
    cells = "".join(f'<div class="k"><div class="kl">{escape(a)}</div><div class="kv2">{escape(b)}</div>'
                    f'<div class="ks">{escape(c)}</div></div>' for a, b, c in items)
    st.markdown(f'<div class="kstrip">{cells}</div>', unsafe_allow_html=True)


def _tight(fig, title, height, **kw):
    ui.layout(fig, height=height, title=title,
              margin=kw.pop("margin", dict(l=6, r=8, t=34, b=6)), **kw)
    fig.update_layout(font=dict(size=11), title=dict(font=dict(size=13)))
    return fig


# ---------------------------------------------------------------------- charts
def chart_stance_hand(v):
    col, order = core.present_order(v, "Stance × hand")
    colors = ui.colors_for("Stance × hand")
    g = v.groupby(col)["win_rate"].agg(["size", "mean"]).reindex(order)
    fig = go.Figure(go.Bar(
        y=g.index, x=g["size"], orientation="h",
        marker=dict(color=[colors[o] for o in g.index], line=dict(width=0)),
        text=[f"{s} · {m:.0f}% W" for s, m in zip(g["size"], g["mean"])], textposition="outside",
        textfont=dict(color=ui.INK_2, size=11), cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x} fighters<extra></extra>"))
    fig.update_layout(xaxis=dict(visible=False, range=[0, g["size"].max() * 1.55]),
                      yaxis=dict(autorange="reversed", tickfont=dict(size=11)), bargap=0.32)
    return _tight(fig, "Stance × dominant hand", H_MAIN // 2 - 6)


def chart_foot_hand(v):
    ct = v.pivot_table(index="foot", columns="hand", values="win_rate", aggfunc=["count", "mean"])
    idx, cols = ["Right", "Left"], ["Right", "Left"]
    cnt = ct["count"].reindex(index=idx, columns=cols).fillna(0) if len(v) else pd.DataFrame(0, idx, cols)
    mean = ct["mean"].reindex(index=idx, columns=cols) if len(v) else pd.DataFrame(np.nan, idx, cols)
    text = [[f"<b>{int(cnt.iloc[i, j])}</b><br>{mean.iloc[i, j]:.0f}% W" if cnt.iloc[i, j] else "—"
             for j in range(2)] for i in range(2)]
    fig = go.Figure(go.Heatmap(
        z=cnt.values, x=["Right hand", "Left hand"], y=["Right foot", "Left foot"],
        colorscale=[[0, "#16302E"], [1, "#1B8A7D"]], showscale=False, text=text,
        texttemplate="%{text}", textfont=dict(color=ui.INK, size=12), xgap=3, ygap=3,
        hovertemplate="%{y} · %{x}<br>%{z} fighters<extra></extra>"))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _tight(fig, "Foot × hand ≈", H_MAIN // 2 - 6)


def chart_style_by_stance(v):
    stances = [s for s in ["Orthodox", "Southpaw", "Switch"] if s in set(v["stance"])]
    tab = pd.crosstab(v["stance"], v["fighting_style"], normalize="index").reindex(stances)
    fig = go.Figure()
    for i, sty in enumerate(core.STYLES):
        if sty in tab.columns:
            fig.add_bar(y=tab.index, x=tab[sty] * 100, name=sty, orientation="h",
                        marker=dict(color=ui.PALETTE[i], line=dict(color=ui.SURFACE, width=1.5)),
                        hovertemplate=f"%{{y}} · {sty}: %{{x:.0f}}%<extra></extra>")
    fig.update_layout(barmode="stack", xaxis=dict(range=[0, 100], ticksuffix="%"),
                      yaxis=dict(autorange="reversed"))
    return _tight(fig, "Striker / grappler / all-rounder", H_MAIN // 2 - 6,
                  margin=dict(l=6, r=8, t=34, b=40),
                  legend=dict(orientation="h", y=-0.2, yanchor="top", x=0, font=dict(size=10),
                              traceorder="normal"))


def chart_winrate_ci(v):
    col, order = core.present_order(v, "Stance × hand")
    colors = ui.colors_for("Stance × hand")
    rows = []
    for g in order:
        s = v.loc[v[col] == g, "win_rate"]
        if len(s) >= 2:
            lo, hi = core.bootstrap_mean_ci(s.to_numpy())
            rows.append((g, s.mean(), lo, hi, len(s)))
    fig = go.Figure()
    for g, m, lo, hi, n in rows:
        fig.add_scatter(x=[m], y=[g], mode="markers", marker=dict(size=10, color=colors[g],
                        line=dict(color=ui.SURFACE, width=2)),
                        error_x=dict(type="data", symmetric=False, array=[hi - m],
                                     arrayminus=[m - lo], color=colors[g], thickness=2, width=4),
                        hovertemplate=f"<b>{g}</b><br>mean %{{x:.1f}}% (n={n})<br>95% CI "
                                      f"{lo:.1f}–{hi:.1f}<extra></extra>", showlegend=False)
    fig.update_layout(xaxis=dict(ticksuffix="%", nticks=4, tickangle=0, tickfont=dict(size=10)), yaxis=dict(autorange="reversed"))
    return _tight(fig, "Mean win rate ± 95% CI", H_MAIN // 2 - 6)


def chart_weight_stance(v):
    ct = (v.pivot_table(index="weight_class", columns="stance", values="fighter",
                        aggfunc="count", fill_value=0)
          .reindex([d for d in core.DIVISION_ORDER if d in set(v["weight_class"])]))
    short = {d: d.replace("Women's ", "W ").replace("Light Heavyweight", "Light Heavy")
             for d in ct.index}
    fig = go.Figure()
    for s in ["Orthodox", "Southpaw", "Switch"]:
        if s in ct.columns:
            fig.add_bar(x=[short[d] for d in ct.index], y=ct[s], name=s,
                        marker=dict(color=STANCE_COLORS[s], line=dict(color=ui.SURFACE, width=1)),
                        hovertemplate=f"%{{x}} · {s}: %{{y}}<extra></extra>")
    fig.update_layout(barmode="stack", showlegend=False,
                      xaxis=dict(tickangle=-40, tickfont=dict(size=9)))
    return _tight(fig, "Weight class × stance", H_SMALL)


def _scatter(v, x, y, title, xl, yl):
    fig = go.Figure()
    for s in ["Orthodox", "Southpaw", "Switch"]:
        d = v[(v["stance"] == s) & v[x].notna() & v[y].notna()]
        if d.empty:
            continue
        fig.add_scatter(x=d[x], y=d[y], mode="markers", name=s, text=d["fighter"],
                        marker=dict(color=STANCE_COLORS[s], size=7, opacity=0.9,
                                    line=dict(color=ui.SURFACE, width=1)),
                        hovertemplate="<b>%{text}</b><br>" + xl + " %{x:.1f} · " + yl
                                      + " %{y:.1f}<extra></extra>")
    fig.update_layout(showlegend=False, xaxis=dict(title=dict(text=xl, font=dict(size=10))),
                      yaxis=dict(title=dict(text=yl, font=dict(size=10))))
    return _tight(fig, title, H_SMALL)


def _country_card(v, df, selected):
    if selected:
        name = next((c for c, iso in ISO3.items() if iso == selected), None)
        pool = v[v["country"] == name].sort_values("popularity_index", ascending=False)
        title = f"{name} · {len(pool)} fighters"
    else:
        pool = v.sort_values("popularity_index", ascending=False)
        title = "Most popular in view"
    rows = "".join(
        f'<div class="row"><span><span class="dot" style="background:{STANCE_COLORS[r.stance]}">'
        f'</span>{escape(r.fighter)}</span><span>{escape(r.hand[0])}H · {r.win_rate:.0f}%</span></div>'
        for r in pool.head(5).itertuples())
    hint = "Click a country on the globe" if not selected else "Click it again to clear"
    st.markdown(f'<div class="card ccard" style="height:{H_SMALL}px"><div class="t">{escape(title)}</div>'
                f'<div class="s">{hint}</div>{rows or "<div class=s>No fighters</div>"}</div>',
                unsafe_allow_html=True)


def render(df: pd.DataFrame):
    v, opts = _sidebar_filters(df)
    st.markdown("""
    <style>
      .block-container { padding-top: 3.1rem !important; padding-bottom: 0.3rem !important; }
      .kstrip { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin: 2px 0 8px; }
      .k { background: #15151F; border: 1px solid #2A2A3A; border-radius: 9px; padding: 6px 11px; }
      .kl { color: #80808F; font-size: .72rem; }
      .kv2 { color: #E8E8EF; font-size: 1.25rem; font-weight: 600; line-height: 1.2; }
      .ks { color: #80808F; font-size: .7rem; }
      .ccard .row { display:flex; justify-content:space-between; font-size:.8rem; color:#B4B4C3;
                    padding: 3px 0; border-bottom: 1px solid #2A2A3A; }
      .ccard .row span:last-child { color:#80808F; }
      div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
    </style>""", unsafe_allow_html=True)

    active = [f"{k.replace('_', ' ')}: {val}" for k, val in opts["filters"].items() if val != ALL]
    st.markdown(
        '<div style="display:flex;align-items:baseline;gap:14px;flex-wrap:wrap">'
        '<div class="title" style="font-size:1.45rem">UFC Stance &amp; Handedness — Global overview</div>'
        f'<div class="sub" style="margin:0">{escape(" · ".join(active)) if active else "All fighters"}'
        '</div></div>', unsafe_allow_html=True)
    _kpi_strip(v, len(df))

    left, mid, right = st.columns([1.02, 1.7, 1.02], gap="small")
    with mid:
        selected = globe3d(country_payload(v), height=H_MAIN, max_names=opts["names"],
                           key="globe")
    if v.empty:
        with left:
            st.info("No fighters match these filters.")
        return
    with left:
        ui.chart(chart_stance_hand(v), key="c_sh")
        ui.chart(chart_foot_hand(v), key="c_fh")
    with right:
        ui.chart(chart_style_by_stance(v), key="c_style")
        ui.chart(chart_winrate_ci(v), key="c_ci")

    a, b, c, d = st.columns([1.05, 1, 1, 0.95], gap="small")
    with a:
        ui.chart(chart_weight_stance(v), key="c_wc")
    with b:
        ui.chart(_scatter(v, "height_cm", "reach_cm", "Height vs reach", "height cm", "reach cm"),
                 key="c_hr")
    with c:
        ui.chart(_scatter(v, "str_acc", "sapm", "Accuracy vs damage absorbed",
                          "accuracy %", "absorbed / min"), key="c_acc")
    with d:
        _country_card(v, df, selected if selected in {r["iso3"] for r in country_payload(v)} else None)
    st.markdown(" ".join(f'<span class="pill"><span class="dot" style="background:{c}"></span>{s}</span>'
                         for s, c in STANCE_COLORS.items())
                + '<span class="pill">≈ estimated (dominant foot)</span>', unsafe_allow_html=True)
