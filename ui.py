"""Shared look & feel: colours, CSS, Plotly defaults, small HTML helpers."""
from html import escape

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

SURFACE = "#15151F"
SURFACE_2 = "#1C1C28"
BORDER = "#2A2A3A"
INK = "#E8E8EF"
INK_2 = "#B4B4C3"
INK_MUTED = "#80808F"
ACCENT = "#2BC4B0"

# Validated categorical palette (dark surface), assigned in fixed order per dimension.
PALETTE = ["#9A6CF0", "#179C8C", "#C47F22", "#4F86E0", "#D0568F", "#7A869A"]
SEQ_TEAL = [[0, "#123C3A"], [0.5, "#1B8A7D"], [1, "#6FE3D2"]]
STYLE_COLORS = dict(zip(core.STYLES, PALETTE))

# Plotly: serve the world map from this app (static/world_110m.json) instead of the CDN.
PLOTLY_CONFIG = {"displaylogo": False, "topojsonURL": "app/static/",
                 "modeBarButtonsToRemove": ["select2d", "lasso2d"]}


def colors_for(dim_label: str) -> dict:
    _, order = core.GROUP_DIMS[dim_label]
    return dict(zip(order, PALETTE))


def inject_css():
    st.markdown(f"""
<style>
  .block-container {{ padding-top: 2.6rem; max-width: 1400px; }}
  h1, h2, h3 {{ letter-spacing: -0.01em; }}
  .eyebrow {{ color: {ACCENT}; font-size: .72rem; font-weight: 700; letter-spacing: .12em;
             text-transform: uppercase; margin-bottom: .2rem; }}
  .title {{ font-size: 1.85rem; font-weight: 700; line-height: 1.15; margin: 0; color: {INK}; }}
  .sub {{ color: {INK_2}; font-size: .95rem; margin-top: .25rem; }}
  .card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
           padding: 14px 16px; }}
  .card .t {{ font-weight: 700; font-size: 1.02rem; color: {INK}; }}
  .card .s {{ color: {INK_MUTED}; font-size: .82rem; margin-top: 2px; }}
  .card .b {{ color: {INK_2}; font-size: .86rem; margin-top: 8px; line-height: 1.45; }}
  .card ul {{ margin: 6px 0 0 0; padding-left: 18px; }}
  .kv {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 14px; margin-top: 10px; }}
  .kv div {{ font-size: .82rem; color: {INK_MUTED}; }}
  .kv b {{ display:block; color: {INK}; font-size: .95rem; font-weight: 600; }}
  .pill {{ display:inline-block; padding: 1px 9px; border-radius: 999px; font-size: .74rem;
           border: 1px solid {BORDER}; color: {INK_2}; margin: 2px 4px 2px 0; }}
  .est {{ display:inline-block; padding: 0 7px; border-radius: 999px; font-size: .68rem;
          border: 1px dashed #C47F22; color: #E0A452; margin-left: 6px; vertical-align: middle;
          font-weight: 600; letter-spacing: .02em; }}
  .dot {{ display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:6px; }}
  .score {{ font-size: 1.5rem; font-weight: 700; color: {INK}; line-height: 1; }}
  .score small {{ font-size: .78rem; color: {INK_MUTED}; font-weight: 500; }}
  .callout {{ border-left: 3px solid {ACCENT}; background: {SURFACE}; padding: 11px 15px;
              border-radius: 0 8px 8px 0; color: {INK_2}; font-size: .9rem; line-height: 1.5; }}
  .callout b {{ color: {INK}; }}
  .sec {{ font-size: 1.05rem; font-weight: 700; color: {INK}; margin: 18px 0 2px 0; }}
  .secsub {{ color: {INK_MUTED}; font-size: .84rem; margin-bottom: 6px; }}
  [data-testid="stMetric"] {{ background: {SURFACE}; border: 1px solid {BORDER};
                              border-radius: 10px; padding: 10px 14px; }}
  [data-testid="stMetricLabel"] p {{ color: {INK_MUTED}; }}
  [data-testid="stMetricValue"] {{ font-size: 1.55rem; }}
  .foot {{ color: {INK_MUTED}; font-size: .8rem; text-align:center; padding: 26px 0 8px;
           border-top: 1px solid {BORDER}; margin-top: 30px; }}
</style>""", unsafe_allow_html=True)


def layout(fig: go.Figure, height: int = 320, title: str | None = None, **kw) -> go.Figure:
    base = dict(
        height=height, paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(color=INK_2, size=12), margin=dict(l=10, r=14, t=44 if title else 14, b=10),
        hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=BORDER, font_color=INK),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, bgcolor="rgba(0,0,0,0)",
                    traceorder="normal", font=dict(size=11)),
    )
    if title:
        base["title"] = dict(text=title, x=0.01, y=0.97, font=dict(size=14, color=INK))
    base.update(kw)
    fig.update_layout(**base)
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    return fig


def chart(fig, key=None):
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, key=key)


def section(title: str, sub: str | None = None, estimated: bool = False):
    badge = '<span class="est">ESTIMATED</span>' if estimated else ""
    st.markdown(f'<div class="sec">{escape(title)}{badge}</div>'
                + (f'<div class="secsub">{escape(sub)}</div>' if sub else ""),
                unsafe_allow_html=True)


def callout(html: str):
    st.markdown(f'<div class="callout">{html}</div>', unsafe_allow_html=True)


def fmt_p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def footer(n: int):
    st.markdown(f"""<div class="foot">UFC Stance &amp; Handedness Intelligence · {n} fighters ·
    Data: UFCSTATS, Tapology, Sherdog · Built by Brian Phu with Streamlit, Plotly, SciPy &amp; three.js ·
    <a href="https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE"
    style="color:{ACCENT}">GitHub</a></div>""", unsafe_allow_html=True)
