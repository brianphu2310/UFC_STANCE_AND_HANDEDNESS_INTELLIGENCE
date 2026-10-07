"""Design system: the "fight card" look.

Two corners — magenta and indigo — carry every comparison; a tan rule marks references.
Display type is Big Shoulders Display (condensed, scoreboard-like), body is Instrument Sans.
One signature device: the primary panel on each page has an octagon-cut corner.
"""
from html import escape

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

# ---------------------------------------------------------------- tokens
BG = "#0E0A17"          # canvas
SURFACE = "#151024"     # panels
SURFACE_2 = "#1D1631"   # raised / hover
BORDER = "#2B2242"      # hairlines
INK = "#EFEAF6"         # bone
INK_2 = "#BDB4D2"
INK_MUTED = "#8A81A3"
ACCENT = "#C862CE"      # magenta corner
ACCENT_2 = "#5A54D8"    # indigo corner
RULE = "#E4C49B"        # tan reference line
ACCENT_SOFT = "rgba(200, 98, 206, 0.14)"
SHADOW = "none"

DISPLAY = "'Big Shoulders Display', 'Oswald', 'Arial Narrow', sans-serif"
BODY = "'Instrument Sans', 'Segoe UI', system-ui, sans-serif"

# Validated categorical palette (dark surface), assigned in fixed order per dimension.
PALETTE = ["#C862CE", "#5A54D8", "#B8813A", "#2BA59A", "#9480E4", "#7E7896"]
SEQ_BLUE = [[0, "#2A1F4A"], [0.5, "#5A54D8"], [1, "#E08BE6"]]   # indigo -> magenta
GRAD_BAR = ["#5A54D8", "#C862CE"]
STYLE_COLORS = dict(zip(core.STYLES, PALETTE))

PLOTLY_CONFIG = {"displaylogo": False, "displayModeBar": False, "topojsonURL": "app/static/"}


def colors_for(dim_label: str) -> dict:
    _, order = core.GROUP_DIMS[dim_label]
    return dict(zip(order, PALETTE))


def inject_css():
    st.markdown(f"""
<style>

  .stApp {{ font-family: {BODY}; }}
  .stApp {{ background:
      radial-gradient(1100px 620px at 92% -12%, rgba(200, 98, 206, .16), transparent 62%),
      radial-gradient(900px 560px at -6% 108%, rgba(90, 84, 216, .14), transparent 60%), {BG}; }}
  .block-container {{ padding-top: 4.9rem; max-width: 1440px; }}
  h1, h2, h3, h4 {{ font-family: {DISPLAY}; color: {INK}; letter-spacing: .005em; }}
  p, li {{ color: {INK_2}; }}
  :focus-visible {{ outline: 2px solid {RULE} !important; outline-offset: 2px; }}

  /* ---------- top bar: wordmark + underline tabs ---------- */
  header[data-testid="stHeader"] {{
    background: rgba(14, 10, 23, .94); backdrop-filter: blur(10px); height: 3.7rem;
    border-bottom: 1px solid {BORDER};
  }}
  header[data-testid="stHeader"]::before {{
    content: "Stance Intelligence"; position: absolute; left: 28px; top: 50%;
    transform: translateY(-50%); font-family: {DISPLAY}; font-weight: 800; font-size: 1.45rem;
    color: {INK}; letter-spacing: .01em;
  }}
  header[data-testid="stHeader"]::after {{
    content: ""; position: absolute; left: 28px; bottom: 9px; width: 34px; height: 3px;
    background: linear-gradient(90deg, {ACCENT} 50%, {ACCENT_2} 50%);
  }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 230px; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{
    border-radius: 0; padding: 8px 4px 6px; margin: 0 12px; background: transparent !important;
    border-bottom: 2px solid transparent;
  }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span {{
    color: {INK_MUTED}; font-weight: 600; font-size: .92rem; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"]:hover span {{ color: {INK}; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] {{
    border-bottom-color: {ACCENT}; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] span {{ color: {INK}; }}

  [data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"], [data-testid="stSidebarCollapseButton"],
  [data-testid="stExpandSidebarButton"], [data-testid="stTooltipIcon"] {{ display: none !important; }}

  /* ---------- sidebar: a quiet rail, not a floating card ---------- */
  section[data-testid="stSidebar"] {{ width: 248px !important; min-width: 248px !important;
    background: rgba(21, 16, 36, .72); border-right: 1px solid {BORDER}; }}
  section[data-testid="stSidebar"] > div:first-child {{ background: transparent; padding-top: 3.7rem; }}
  [data-testid="stSidebarHeader"] {{ height: .6rem !important; min-height: 0 !important; padding: 0 !important; }}
  section[data-testid="stSidebar"] label p {{ color: {INK_MUTED}; font-size: .8rem; }}
  .sbh {{ font-family: {DISPLAY}; font-weight: 700; font-size: 1.3rem; color: {INK}; margin: 4px 0 10px; }}

  /* ---------- page header ---------- */
  .ph {{ margin: 0 0 18px; max-width: 980px; }}
  .ph h1 {{ font-family: {DISPLAY}; font-weight: 800; font-size: 3.1rem; line-height: .98;
            margin: 0; padding: 0; color: {INK}; }}
  .ph p {{ font-size: 1.02rem; color: {INK_2}; margin: 8px 0 0; max-width: 70ch; line-height: 1.5; }}
  .eyebrow {{ display: none; }}
  .title {{ font-family: {DISPLAY}; font-weight: 800; font-size: 3.1rem; line-height: .98; color: {INK}; }}
  .sub {{ color: {INK_2}; font-size: 1.02rem; margin-top: 8px; max-width: 70ch; }}

  /* ---------- sections ---------- */
  .sec {{ font-family: {DISPLAY}; font-weight: 700; font-size: 1.6rem; color: {INK};
          margin: 30px 0 2px; padding-top: 14px; border-top: 1px solid {BORDER}; line-height: 1.05; }}
  .secsub {{ color: {INK_MUTED}; font-size: .88rem; margin-bottom: 10px; max-width: 75ch; }}

  /* ---------- panels: the octagon cut is the one signature device ---------- */
  .card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 4px; padding: 16px 18px; }}
  .card.oct, .oct {{ border: none; position: relative; background:
      linear-gradient({SURFACE}, {SURFACE}) padding-box;
      clip-path: polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 22px 100%, 0 calc(100% - 22px)); }}
  .card .t {{ font-family: {DISPLAY}; font-weight: 700; font-size: 1.35rem; color: {INK}; line-height: 1.05; }}
  .card .s {{ color: {INK_MUTED}; font-size: .82rem; margin-top: 3px; }}
  .card .b {{ color: {INK_2}; font-size: .88rem; margin-top: 10px; line-height: 1.5; }}
  .card ul {{ margin: 6px 0 0; padding-left: 18px; }}
  .kv {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px; margin-top: 14px; }}
  .kv div {{ font-size: .78rem; color: {INK_MUTED}; }}
  .kv b {{ display: block; color: {INK}; font-family: {DISPLAY}; font-size: 1.35rem; font-weight: 700;
           line-height: 1.05; margin-top: 1px; }}
  .pill {{ display: inline-block; padding: 1px 9px; border-radius: 3px; font-size: .76rem;
           border: 1px solid {BORDER}; background: transparent; color: {INK_2}; margin: 2px 4px 2px 0; }}
  .est {{ display: inline-block; padding: 0 6px; border-radius: 3px; font-size: .66rem;
          border: 1px dashed #B8813A; color: {RULE}; margin-left: 6px; vertical-align: middle;
          font-weight: 600; font-family: {BODY}; }}
  .dot {{ display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px; }}
  .score {{ font-family: {DISPLAY}; font-size: 2.2rem; font-weight: 800; color: {INK}; line-height: .9; }}
  .score small {{ font-family: {BODY}; font-size: .78rem; color: {INK_MUTED}; font-weight: 500; }}
  .callout {{ border-left: 3px solid {RULE}; background: transparent; padding: 4px 0 4px 16px;
              color: {INK_2}; font-size: .95rem; line-height: 1.55; max-width: 110ch; }}
  .callout b {{ color: {INK}; }}

  /* keyed hero containers: st.container(key="oct_...") */
  [class*="st-key-oct_"] {{ padding: 18px 22px; background:
      radial-gradient(700px 360px at 50% 30%, rgba(90,84,216,.16), transparent 70%), {SURFACE};
      clip-path: polygon(0 0, calc(100% - 30px) 0, 100% 30px, 100% 100%, 30px 100%, 0 calc(100% - 30px)); }}
  [class*="st-key-oct_"] .card {{ background: transparent; border: none; padding: 4px 0; }}
  [class*="st-key-oct_"] [data-testid="stPlotlyChart"] {{ border: none; background: transparent; }}

  .simlist {{ border-top: 1px solid {BORDER}; }}
  .simrow {{ display: grid; grid-template-columns: 1fr 90px 34px; gap: 12px; align-items: center;
             padding: 9px 0; border-bottom: 1px solid {BORDER}; }}
  .simrow b {{ display: block; font-family: {DISPLAY}; font-size: 1.15rem; font-weight: 700; color: {INK}; }}
  .simrow span {{ font-size: .78rem; color: {INK_MUTED}; }}
  .simbar {{ height: 4px; background: {SURFACE_2}; }}
  .simbar i {{ display: block; height: 4px; background: linear-gradient(90deg, {ACCENT_2}, {ACCENT}); }}
  .simrow em {{ font-style: normal; font-family: {DISPLAY}; font-weight: 800; font-size: 1.35rem;
                color: {INK}; text-align: right; }}

  /* ---------- streamlit widgets ---------- */
  [data-testid="stMetric"] {{ background: transparent; border-top: 1px solid {BORDER};
                              padding: 10px 0 0; border-radius: 0; }}
  [data-testid="stMetricLabel"] p {{ color: {INK_MUTED}; font-size: .8rem; }}
  [data-testid="stMetricValue"] {{ font-family: {DISPLAY}; font-size: 2.1rem; font-weight: 700; color: {INK}; }}
  [data-testid="stPlotlyChart"] {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 4px; }}
  [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 4px; }}
  .stDownloadButton button, .stButton button {{ border-radius: 3px; font-weight: 600; }}
  .stDownloadButton button[kind="primary"], .stButton button[kind="primary"] {{ color: #fff !important; }}
  .stDownloadButton button[kind="primary"] p {{ color: #fff !important; }}
  [data-baseweb="select"] > div, [data-baseweb="input"] > div {{ border-radius: 3px !important; }}

  .foot {{ color: {INK_MUTED}; font-size: .8rem; padding: 26px 0 8px; border-top: 1px solid {BORDER};
           margin-top: 40px; display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; }}
  .foot a {{ color: {INK_2}; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
</style>""", unsafe_allow_html=True)


def page_header(title: str, dek: str | None = None):
    st.markdown(f'<div class="ph"><h1>{escape(title)}</h1>'
                + (f'<p>{escape(dek)}</p>' if dek else "") + '</div>', unsafe_allow_html=True)


def layout(fig: go.Figure, height: int = 320, title: str | None = None, **kw) -> go.Figure:
    base = dict(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK_2, size=12, family=BODY),
        margin=dict(l=14, r=16, t=52 if title else 14, b=12),
        hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=BORDER, font=dict(color=INK, family=BODY)),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, bgcolor="rgba(0,0,0,0)",
                    traceorder="normal", font=dict(size=11, color=INK_2)),
    )
    if title:
        base["title"] = dict(text=title, x=0.015, y=0.965, xanchor="left",
                             font=dict(size=19, color=INK, family=DISPLAY))
    base.update(kw)
    fig.update_layout(**base)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.045)", zeroline=False, linecolor=BORDER,
                     tickfont=dict(color=INK_MUTED), title_font=dict(color=INK_MUTED, size=11))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.045)", zeroline=False, linecolor=BORDER,
                     tickfont=dict(color=INK_MUTED), title_font=dict(color=INK_MUTED, size=11))
    return fig


def chart(fig, key=None):
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, key=key)


def section(title: str, sub: str | None = None, estimated: bool = False):
    badge = '<span class="est">estimated</span>' if estimated else ""
    st.markdown(f'<div class="sec">{escape(title)}{badge}</div>'
                + (f'<div class="secsub">{escape(sub)}</div>' if sub else ""),
                unsafe_allow_html=True)


def callout(html: str):
    st.markdown(f'<div class="callout">{html}</div>', unsafe_allow_html=True)


def fmt_p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def footer(n: int):
    st.markdown(f"""<div class="foot"><span>{n} fighters. Stance, record and fight stats from
    UFCSTATS, Tapology and Sherdog.</span><span>Built by Brian Phu.
    <a href="https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE">Source on GitHub</a>
    </span></div>""", unsafe_allow_html=True)
