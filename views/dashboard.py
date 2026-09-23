"""Global dashboard: world map in the centre, stance / hand / foot panels around it."""
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui

ISO3 = {"USA": "USA", "Brazil": "BRA", "Russia": "RUS", "UK": "GBR", "Netherlands": "NLD",
        "Mexico": "MEX", "Poland": "POL", "France": "FRA", "Australia": "AUS", "Japan": "JPN",
        "Jamaica": "JAM", "Georgia": "GEO", "Canada": "CAN", "China": "CHN",
        "South Korea": "KOR", "Ecuador": "ECU", "Czech Rep.": "CZE", "Belarus": "BLR",
        "Croatia": "HRV", "Ukraine": "UKR", "Ireland": "IRL", "Denmark": "DNK",
        "Germany": "DEU", "Nigeria": "NGA", "Cameroon": "CMR", "New Zealand": "NZL",
        "Kyrgyzstan": "KGZ", "Belgium": "BEL"}

MAP_METRICS = {
    "Fighters": ("fighters", "{:.0f}", False),
    "Southpaw / switch share": ("sp_share", "{:.0%}", False),
    "Left-handed share": ("lh_share", "{:.0%}", False),
    "Mean win rate": ("win_rate", "{:.1f}%", False),
    "Mean popularity": ("popularity", "{:.0f}", False),
}

NUMERIC = [  # column, title, axis label, estimated?
    ("height_cm", "Height", "cm", False),
    ("reach_cm", "Reach", "cm", False),
    ("win_rate", "Win rate (career)", "%", False),
    ("age", "Age", "years", False),
    ("str_acc", "Striking accuracy", "% of sig. strikes landed", False),
    ("sapm", "Damage absorbed", "sig. strikes absorbed / min", False),
    ("slpm", "Striking output", "sig. strikes landed / min", False),
    ("popularity_index", "Popularity index", "0–100 (headliner + title fights)", False),
]


def _filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown('<div class="eyebrow">Dashboard filters</div>', unsafe_allow_html=True)
        gender = st.segmented_control("Division group", ["All", "Men", "Women"], default="All")
        divs = st.multiselect("Weight class",
                              [d for d in core.DIVISION_ORDER if d in set(df["weight_class"])])
        stances = st.multiselect("Stance", ["Orthodox", "Southpaw", "Switch"])
        hands = st.multiselect("Dominant hand", ["Right", "Left"])
        feet = st.multiselect("Dominant foot (estimated)", ["Right", "Left"])
        styles = st.multiselect("Fighting style", core.STYLES)
        champs = st.toggle("Champions only", False)
    v = df
    if gender and gender != "All":
        v = v[v["gender"] == gender]
    for col, sel in [("weight_class", divs), ("stance", stances), ("hand", hands),
                     ("foot", feet), ("fighting_style", styles)]:
        if sel:
            v = v[v[col].isin(sel)]
    if champs:
        v = v[v["champion"]]
    return v


def _kpis(v: pd.DataFrame):
    n = max(len(v), 1)
    cols = st.columns(6)
    items = [
        ("Fighters", f"{len(v)}", f"{v['country'].nunique()} countries"),
        ("Southpaw", f"{(v['stance'] == 'Southpaw').sum() / n:.0%}",
         f"{(v['stance'] == 'Southpaw').sum()} fighters"),
        ("Switch stance", f"{(v['stance'] == 'Switch').sum() / n:.0%}",
         f"{(v['stance'] == 'Switch').sum()} fighters"),
        ("Left-handed", f"{(v['hand'] == 'Left').sum() / n:.0%}",
         f"{(v['hand'] == 'Left').sum()} fighters"),
        ("Left-footed ≈", f"{(v['foot'] == 'Left').sum() / n:.0%}", "estimated"),
        ("Median win rate", f"{v['win_rate'].median():.1f}%" if len(v) else "—",
         f"{v['champion'].sum()} champions"),
    ]
    for c, (label, val, sub) in zip(cols, items):
        c.metric(label, val, sub, delta_color="off", delta_arrow="off")


def _division_panel(v, dim_label, colors):
    col, order = core.present_order(v, dim_label)
    ct = (v.pivot_table(index="weight_class", columns=col, values="fighter", aggfunc="count",
                        fill_value=0)
          .reindex([d for d in core.DIVISION_ORDER if d in set(v["weight_class"])]))
    fig = go.Figure()
    for g in [o for o in order if o in ct.columns]:
        fig.add_bar(y=ct.index, x=ct[g], name=g, orientation="h",
                    marker=dict(color=colors[g], line=dict(color=ui.SURFACE, width=1.5)),
                    hovertemplate=f"<b>%{{y}}</b><br>{g}: %{{x}}<extra></extra>")
    fig.update_layout(barmode="stack", showlegend=False, xaxis=dict(title=None),
                      yaxis=dict(autorange="reversed", tickfont=dict(size=11)))
    ui.chart(ui.layout(fig, height=max(250, 60 + 27 * len(ct)), title="By weight class"))

    # small table: group share & win rate
    rows = []
    for g in order:
        s = v[v[col] == g]
        if len(s):
            rows.append(f'<div style="display:flex;justify-content:space-between;font-size:.78rem;'
                        f'padding:3px 0;border-bottom:1px solid {ui.BORDER}">'
                        f'<span><span class="dot" style="background:{colors[g]}"></span>{escape(g)}</span>'
                        f'<span style="color:{ui.INK_2}">{len(s)} · {s["win_rate"].mean():.0f}% W</span></div>')
    st.markdown(f'<div class="card">{"".join(rows)}</div>', unsafe_allow_html=True)


def _map(v, metric_label):
    col, fmt, _ = MAP_METRICS[metric_label]
    by = (v.groupby("country")
          .agg(fighters=("fighter", "size"), win_rate=("win_rate", "mean"),
               popularity=("popularity_index", "mean"),
               sp_share=("stance", lambda s: s.isin(["Southpaw", "Switch"]).mean()),
               lh_share=("hand", lambda s: (s == "Left").mean()),
               names=("fighter", lambda s: "<br>".join(s.head(8))))
          .reset_index())
    by["iso3"] = by["country"].map(ISO3)
    by["label"] = by[col].map(fmt.format)
    fig = go.Figure(go.Choropleth(
        locations=by["iso3"], z=by[col], colorscale=ui.SEQ_TEAL,
        marker_line_color=ui.SURFACE, marker_line_width=0.6,
        customdata=by[["country", "fighters", "label", "names"]],
        hovertemplate=(f"<b>%{{customdata[0]}}</b> · %{{customdata[1]}} fighters<br>"
                       f"{metric_label}: %{{customdata[2]}}<br><br>"
                       f"<span style='color:{ui.INK_MUTED}'>%{{customdata[3]}}</span><extra></extra>"),
        colorbar=dict(title=None, thickness=10, len=0.55, x=0.99, outlinewidth=0,
                      tickformat=".0%" if "share" in metric_label else None)))
    fig.update_geos(bgcolor=ui.SURFACE, showframe=False, showcoastlines=False, showland=True,
                    landcolor="#22222E", showcountries=True, countrycolor=ui.BORDER,
                    showocean=True, oceancolor=ui.SURFACE, projection_type="natural earth",
                    lataxis_range=[-56, 84], projection_scale=1.12, center=dict(lat=16, lon=10))
    ui.chart(ui.layout(fig, height=440, margin=dict(l=0, r=0, t=0, b=0)), key="world_map")
    top = by.sort_values("fighters", ascending=False).head(6)
    st.markdown(" ".join(f'<span class="pill">{escape(r.country)} · {r.fighters}</span>'
                         for r in top.itertuples()), unsafe_allow_html=True)


def _spotlight(v, full):
    pool = v.sort_values("popularity_index", ascending=False)
    if pool.empty:
        st.info("No fighters match these filters.")
        return
    name = st.selectbox("Fighter spotlight", pool["fighter"], index=0)
    f = pool[pool["fighter"] == name].iloc[0]
    pct = core.skill_percentiles(full).loc[f.name]

    def val(x, fmt):
        return fmt.format(x) if pd.notna(x) else "—"
    badges = "".join(f'<span class="pill">{escape(b)}</span>' for b in
                     [f["stance"], f"{f['hand']}-handed", f["fighting_style"],
                      "Champion" if f["champion"] else None] if b)
    st.markdown(f"""
    <div class="card">
      <div class="t" style="font-size:1.15rem">{escape(f['fighter'])}</div>
      <div class="s">{escape(f['weight_class'])} · {escape(f['country'])}</div>
      <div style="margin-top:8px">{badges}</div>
      <div class="kv">
        <div>Record<b>{f['wins']}–{f['losses']} ({f['win_rate']:.0f}%)</b></div>
        <div>Age<b>{val(f['age'], '{:.0f}')}</b></div>
        <div>Height<b>{val(f['height_cm'], '{:.0f} cm')}</b></div>
        <div>Reach<b>{val(f['reach_cm'], '{:.0f} cm')}</b></div>
        <div>Str. accuracy<b>{val(f['str_acc'], '{:.0f}%')}</b></div>
        <div>Absorbed / min<b>{val(f['sapm'], '{:.2f}')}</b></div>
        <div>Dominant foot<b>{f['foot']} <span class="est">EST</span></b></div>
        <div>Popularity<b>{f['popularity_index']}/100</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    labels = [core.SKILLS[c][0] for c in core.SKILLS]
    vals = [pct[c] if pd.notna(pct[c]) else 0 for c in core.SKILLS]
    fig = go.Figure(go.Bar(
        y=labels, x=vals, orientation="h", marker=dict(color=ui.ACCENT, line=dict(width=0)),
        text=[f"{x:.0f}" for x in vals], textposition="outside", textfont=dict(color=ui.INK_2, size=11),
        hovertemplate="%{y}: %{x:.0f}th percentile<extra></extra>"))
    fig.update_layout(xaxis=dict(range=[0, 115], visible=False),
                      yaxis=dict(autorange="reversed", tickfont=dict(size=11)), bargap=0.35)
    ui.chart(ui.layout(fig, height=275, title="Percentile vs all 117 fighters"))


def _categorical_row(v, dim_label, colors):
    gcol, order = core.present_order(v, dim_label)
    specs = [("hand", "Dominant hand", ["Right", "Left"], False),
             ("foot", "Dominant foot", ["Right", "Left"], True),
             ("stance", "Stance", ["Orthodox", "Southpaw", "Switch"], False),
             ("fighting_style", "Grappler, striker or all-rounder", core.STYLES, False)]
    cols = st.columns(4)
    for c, (col, title, cats, est) in zip(cols, specs):
        with c:
            fig = go.Figure()
            cats = [x for x in cats if x in set(v[col])]
            if col == gcol:
                counts = v[col].value_counts().reindex(cats).fillna(0)
                fig.add_bar(x=cats, y=counts, marker=dict(color=[colors[x] for x in cats]),
                            text=counts.astype(int), textposition="outside",
                            textfont=dict(color=ui.INK_2),
                            hovertemplate="%{x}: %{y}<extra></extra>")
            else:
                for g in order:
                    s = v[v[gcol] == g][col].value_counts().reindex(cats).fillna(0)
                    fig.add_bar(x=cats, y=s, name=g,
                                marker=dict(color=colors[g], line=dict(color=ui.SURFACE, width=1.5)),
                                hovertemplate=f"{g}<br>%{{x}}: %{{y}}<extra></extra>")
                fig.update_layout(barmode="stack")
            fig.update_layout(showlegend=False, yaxis=dict(title=None))
            ui.chart(ui.layout(fig, height=260, title=title + (" ≈" if est else "")))


def _foot_hand_heatmap(v):
    ct = v.pivot_table(index="foot", columns="hand", values="win_rate",
                       aggfunc=["count", "mean"]).reindex(index=["Right", "Left"])
    counts = ct["count"].reindex(columns=["Right", "Left"]).fillna(0)
    means = ct["mean"].reindex(columns=["Right", "Left"])
    text = [[f"{int(counts.iloc[i, j])} fighters<br>{means.iloc[i, j]:.0f}% W"
             if counts.iloc[i, j] else "—" for j in range(2)] for i in range(2)]
    fig = go.Figure(go.Heatmap(
        z=counts.values, x=["Right hand", "Left hand"], y=["Right foot", "Left foot"],
        colorscale=[[0, "#16302E"], [1, "#1B8A7D"]], showscale=False, text=text,
        texttemplate="%{text}",
        textfont=dict(color=ui.INK, size=13), xgap=3, ygap=3,
        hovertemplate="%{y} · %{x}<br>%{text}<extra></extra>"))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    ui.chart(ui.layout(fig, height=260, title="Foot × hand combinations ≈"))


def _group_share(v, dim_label, colors, col, cats, title):
    gcol, order = core.present_order(v, dim_label)
    fig = go.Figure()
    tab = pd.crosstab(v[gcol], v[col], normalize="index").reindex(order)
    for i, cat in enumerate(cats):
        if cat not in tab.columns:
            continue
        fig.add_bar(y=tab.index, x=tab[cat] * 100, name=str(cat), orientation="h",
                    marker=dict(color=ui.PALETTE[i], line=dict(color=ui.SURFACE, width=1.5)),
                    hovertemplate=f"%{{y}}<br>{cat}: %{{x:.0f}}%<extra></extra>")
    fig.update_layout(barmode="stack", xaxis=dict(range=[0, 100], ticksuffix="%"),
                      yaxis=dict(autorange="reversed"))
    ui.chart(ui.layout(fig, height=110 + 34 * len(order), title=title,
                       margin=dict(l=10, r=14, t=70, b=10)))


def _distribution(v, dim_label, colors, col, title, unit):
    gcol, order = core.present_order(v, dim_label)
    fig = go.Figure()
    for g in order:
        s = v[(v[gcol] == g) & v[col].notna()]
        if s.empty:
            continue
        fig.add_box(y=[g] * len(s), x=s[col], name=g, orientation="h", boxpoints="all",
                    jitter=0.5, pointpos=0, fillcolor="rgba(0,0,0,0)",
                    marker=dict(color=colors[g], size=6, opacity=0.8,
                                line=dict(color=ui.SURFACE, width=1)),
                    line=dict(color=colors[g], width=1.4), text=s["fighter"],
                    hovertemplate="<b>%{text}</b><br>%{x:.1f} " + unit + "<extra></extra>")
    fig.update_layout(showlegend=False, xaxis=dict(title=dict(text=unit, font=dict(size=11))),
                      yaxis=dict(autorange="reversed", tickfont=dict(size=10)))
    ui.chart(ui.layout(fig, height=110 + 38 * len(order), title=title))


def _record_scatter(v, dim_label, colors):
    gcol, order = core.present_order(v, dim_label)
    fig = go.Figure()
    for g in order:
        s = v[v[gcol] == g]
        fig.add_scatter(x=s["losses"], y=s["wins"], mode="markers", name=g,
                        marker=dict(color=colors[g], size=np.clip(s["popularity_index"] / 6, 6, 16),
                                    line=dict(color=ui.SURFACE, width=1.5)),
                        text=s["fighter"],
                        hovertemplate="<b>%{text}</b><br>%{y}–%{x}<extra></extra>")
    fig.update_layout(xaxis=dict(title="losses"), yaxis=dict(title="wins"))
    ui.chart(ui.layout(fig, height=360, title="Career record (size = popularity)",
                       margin=dict(l=10, r=14, t=70, b=10)))


def render(df: pd.DataFrame):
    v = _filters(df)
    top = st.columns([3, 2])
    with top[0]:
        st.markdown('<div class="eyebrow">Global dashboard</div>'
                    '<div class="title">Where the southpaws, lefties and switch-hitters come from</div>'
                    f'<div class="sub">{len(v)} of {len(df)} fighters in view · every chart is split '
                    'by the dimension you pick →</div>', unsafe_allow_html=True)
    with top[1]:
        c1, c2 = st.columns(2)
        dim = c1.selectbox("Group every chart by", list(core.GROUP_DIMS), index=3, key="dim")
        metric = c2.selectbox("Colour the map by", list(MAP_METRICS), key="map_metric")
    colors = ui.colors_for(dim)
    st.write("")
    _kpis(v)
    if v.empty:
        st.warning("No fighters match these filters.")
        return

    st.write("")
    left, mid, right = st.columns([1.25, 2.3, 1.15], gap="small")
    with left:
        _division_panel(v, dim, colors)
    with mid:
        _map(v, metric)
    with right:
        _spotlight(v, df)

    # legend for the grouping, shown once
    _, order = core.present_order(v, dim)
    st.markdown(" ".join(f'<span class="pill"><span class="dot" style="background:{colors[g]}">'
                         f'</span>{escape(g)}</span>' for g in order), unsafe_allow_html=True)

    ui.section("Hand, foot & stance", "Counts in the current view, stacked by your grouping. "
               "Dominant foot is estimated — no public source records it.", estimated=False)
    _categorical_row(v, dim, colors)
    c1, c2, c3 = st.columns([1, 1.4, 1.4])
    with c1:
        _foot_hand_heatmap(v)
    with c2:
        _group_share(v, dim, colors, "fighting_style", core.STYLES, "Fighting style mix")
    with c3:
        v2 = v.assign(champ=np.where(v["champion"], "Champion", "Contender"))
        _group_share(v2, dim, colors, "champ", ["Champion", "Contender"], "Title holders")

    ui.section("Body, record & output", "Each dot is a fighter; boxes show the middle 50%. "
               "UFC-only stats (accuracy, output, damage) come from UFCSTATS fight logs.")
    for i in range(0, len(NUMERIC), 2):
        a, b = st.columns(2)
        for c, (col, title, unit, _) in zip((a, b), NUMERIC[i:i + 2]):
            with c:
                _distribution(v, dim, colors, col, title, unit)
    _record_scatter(v, dim, colors)
