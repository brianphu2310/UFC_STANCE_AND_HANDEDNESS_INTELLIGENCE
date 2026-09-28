"""Shared look & feel: light "soft card" theme, Plotly defaults, app chrome, HTML helpers."""
from html import escape

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

# ---------------------------------------------------------------- tokens
# Colour theme: deep violet-black with magenta / indigo accents and a warm tan rule line.
BG = "#120C20"          # page (a violet glow is layered on top in CSS)
SURFACE = "#0C0818"     # cards
SURFACE_2 = "#1A1230"   # inset / hover
BORDER = "#34264F"
INK = "#F3EEFB"
INK_2 = "#C9C0DD"
INK_MUTED = "#8D84A6"
ACCENT = "#C862CE"      # magenta
ACCENT_2 = "#5A54D8"    # indigo
RULE = "#E4C49B"        # tan reference line
ACCENT_SOFT = "rgba(200, 98, 206, 0.16)"
SHADOW = "0 12px 32px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(200, 98, 206, 0.05)"

# Validated categorical palette (dark surface), assigned in fixed order per dimension.
PALETTE = ["#C862CE", "#5A54D8", "#B8813A", "#2BA59A", "#9480E4", "#7E7896"]
SEQ_BLUE = [[0, "#2A1F4A"], [0.5, "#5A54D8"], [1, "#E08BE6"]]   # indigo -> magenta
GRAD_BAR = ["#5A54D8", "#C862CE"]                                # bar gradient ends
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
  /* ---------- page ---------- */
  .stApp {{ background:
      radial-gradient(1200px 700px at 85% -10%, rgba(120, 60, 160, .35), transparent 60%),
      radial-gradient(900px 600px at 0% 110%, rgba(90, 84, 216, .18), transparent 60%), {BG}; }}
  .block-container {{ padding-top: 4.6rem; max-width: 1480px; }}
  h1, h2, h3 {{ letter-spacing: -0.01em; color: {INK}; }}

  /* ---------- fixed top bar (page navigation) ---------- */
  header[data-testid="stHeader"] {{
    background: rgba(12, 8, 24, .92); backdrop-filter: blur(8px); height: 3.6rem;
    border-bottom: 1px solid {BORDER}; box-shadow: 0 8px 24px rgba(0,0,0,.35);
  }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{
    border-radius: 999px; padding: 4px 14px; margin: 0 2px; border: 1px solid transparent;
  }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span {{ color: {INK_2}; font-weight: 600; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"]:hover {{ background: {SURFACE_2}; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] {{
    background: {ACCENT_SOFT}; border-color: rgba(200, 98, 206, .55); }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] span {{ color: {INK}; }}

  /* ---------- no icons / chrome clutter ---------- */
  [data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
  [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"],
  [data-testid="stTooltipIcon"] {{ display: none !important; }}
  section[data-testid="stSidebar"] {{ width: 250px !important; min-width: 250px !important; }}

  /* ---------- floating sidebar block ---------- */
  section[data-testid="stSidebar"] {{ background: transparent; border: none; }}
  section[data-testid="stSidebar"] > div:first-child {{
    background: {SURFACE}; margin: 4.4rem 0 12px 12px; border-radius: 18px;
    border: 1px solid {BORDER}; box-shadow: {SHADOW}; height: calc(100vh - 4.4rem - 12px);
  }}
  section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{ padding-top: 1rem; }}

  /* ---------- building blocks ---------- */
  .eyebrow {{ color: {ACCENT}; font-size: .72rem; font-weight: 700; letter-spacing: .12em;
             text-transform: uppercase; margin-bottom: .2rem; }}
  .title {{ font-size: 1.85rem; font-weight: 700; line-height: 1.15; margin: 0; color: {INK}; }}
  .sub {{ color: {INK_2}; font-size: .95rem; margin-top: .25rem; }}
  .card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 16px;
           padding: 14px 16px; box-shadow: {SHADOW}; }}
  .card .t {{ font-weight: 700; font-size: 1.02rem; color: {INK}; }}
  .card .s {{ color: {INK_MUTED}; font-size: .82rem; margin-top: 2px; }}
  .card .b {{ color: {INK_2}; font-size: .86rem; margin-top: 8px; line-height: 1.45; }}
  .card ul {{ margin: 6px 0 0 0; padding-left: 18px; }}
  .kv {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 14px; margin-top: 10px; }}
  .kv div {{ font-size: .82rem; color: {INK_MUTED}; }}
  .kv b {{ display:block; color: {INK}; font-size: .95rem; font-weight: 600; }}
  .pill {{ display:inline-block; padding: 1px 9px; border-radius: 999px; font-size: .74rem;
           border: 1px solid {BORDER}; background: {SURFACE}; color: {INK_2}; margin: 2px 4px 2px 0; }}
  .est {{ display:inline-block; padding: 0 7px; border-radius: 999px; font-size: .68rem;
          border: 1px dashed #B8813A; color: #E4C49B; margin-left: 6px; vertical-align: middle;
          font-weight: 600; letter-spacing: .02em; }}
  .dot {{ display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:6px; }}
  .score {{ font-size: 1.5rem; font-weight: 700; color: {INK}; line-height: 1; }}
  .score small {{ font-size: .78rem; color: {INK_MUTED}; font-weight: 500; }}
  .callout {{ border-left: 3px solid {ACCENT}; background: {SURFACE}; padding: 11px 15px;
              border-radius: 0 12px 12px 0; color: {INK_2}; font-size: .9rem; line-height: 1.5;
              box-shadow: {SHADOW}; }}
  .callout b {{ color: {INK}; }}
  .sec {{ font-size: 1.05rem; font-weight: 700; color: {INK}; margin: 18px 0 2px 0; }}
  .secsub {{ color: {INK_MUTED}; font-size: .84rem; margin-bottom: 6px; }}
  [data-testid="stMetric"] {{ background: {SURFACE}; border: 1px solid {BORDER};
                              border-radius: 14px; padding: 10px 14px; box-shadow: {SHADOW}; }}
  [data-testid="stMetricLabel"] p {{ color: {INK_MUTED}; }}
  [data-testid="stMetricValue"] {{ font-size: 1.55rem; color: {INK}; }}
  [data-testid="stPlotlyChart"] {{ border-radius: 16px; overflow: hidden; box-shadow: {SHADOW};
                                   background: {SURFACE}; }}
  [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; box-shadow: {SHADOW}; }}
  .foot {{ color: {INK_MUTED}; font-size: .8rem; text-align:center; padding: 26px 0 8px;
           border-top: 1px solid {BORDER}; margin-top: 30px; }}
</style>""", unsafe_allow_html=True)


def layout(fig: go.Figure, height: int = 320, title: str | None = None, **kw) -> go.Figure:
    base = dict(
        height=height, paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(color=INK_2, size=12, family="Inter, Segoe UI, system-ui, sans-serif"),
        margin=dict(l=12, r=14, t=46 if title else 14, b=10),
        hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=ACCENT, font_color=INK),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, bgcolor="rgba(0,0,0,0)",
                    traceorder="normal", font=dict(size=11)),
    )
    if title:
        base["title"] = dict(text=title, x=0.02, y=0.97, font=dict(size=14, color=INK))
    base.update(kw)
    fig.update_layout(**base)
    fig.update_xaxes(gridcolor="#221838", zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor="#221838", zerolinecolor=BORDER, linecolor=BORDER)
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
