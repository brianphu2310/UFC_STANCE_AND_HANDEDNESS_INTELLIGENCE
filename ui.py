"""Design system: future-purple fight night.

Violet-black arena with a violet corner and a cyan corner; a gold rule marks references and the
dominant side. Display type is Big Shoulders Display (condensed, scoreboard-like), body is
Instrument Sans, both self-hosted. Signature devices: the octagon-cut primary panel on each page
and a faint chain-link diamond in the page background, taken from the cage fence.
"""
from html import escape

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

# ---------------------------------------------------------------- tokens
BG = "#0B0A12"          # canvas: violet-black arena
SURFACE = "#14121E"     # panels
SURFACE_2 = "#1D1A2A"   # raised / hover, inputs
BORDER = "#2B2740"      # decorative hairlines only
INK = "#F1EEF8"         # near-white with a violet cast
INK_2 = "#C6C0D8"
INK_MUTED = "#958EAD"   # 6.3:1 on BG, 5.3:1 on SURFACE_2
ACCENT = "#A77BFF"      # violet corner: lines, marks and text (6.4:1 on BG)
ACCENT_FILL = "#7C4DFF" # violet for filled buttons, chips, sliders (white text 4.8:1)
ACCENT_2 = "#48D1E0"    # cyan corner (10.6:1 on BG)
ACCENT_2_TEXT = "#48D1E0"
ON_ACCENT = "#FFFFFF"   # text on ACCENT_FILL
FIELD_BORDER = "#6F6890"  # input outlines: 3.3:1 on SURFACE_2 (WCAG 1.4.11)
RULE = "#E9B44C"        # gold: reference lines, dominant side, focus ring
ACCENT_SOFT = "rgba(167, 123, 255, 0.14)"
MUTED_FILL = "#2A2640"   # de-emphasised bars (outside a selection)
SHADOW = "none"

DISPLAY = "'Big Shoulders Display', 'Oswald', 'Arial Narrow', sans-serif"
BODY = "'Instrument Sans', 'Segoe UI', system-ui, sans-serif"

# Categorical palette (dark surface), assigned in a fixed order per dimension.
PALETTE = ["#A77BFF", "#48D1E0", "#E9B44C", "#F062A8", "#6BDB9A", "#7D7896"]
SEQ_BLUE = [[0, "#1E1733"], [0.5, "#5B34B8"], [1, "#C9A9FF"]]   # violet-black -> lavender
GRAD_BAR = ["#48D1E0", "#A77BFF"]
STYLE_COLORS = dict(zip(core.STYLES, PALETTE))

PLOTLY_CONFIG = {"displaylogo": False, "displayModeBar": False, "topojsonURL": "app/static/"}


def text_color(c: str) -> str:
    """Colour for text drawn in a series colour (swaps in a text-safe variant where one exists)."""
    return ACCENT_2_TEXT if c.upper() == ACCENT_2.upper() else c


def on_color(c: str) -> str:
    """Text colour for labels sitting on a fill of colour c (whichever contrasts more)."""
    h = c.lstrip("#")
    lin = [(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in lin]
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return BG if (lum + 0.05) / 0.0537 > 1.05 / (lum + 0.05) else "#FFFFFF"   # 0.0537 = L(BG) + 0.05


def colors_for(dim_label: str) -> dict:
    _, order = core.GROUP_DIMS[dim_label]
    return dict(zip(order, PALETTE))


def inject_css():
    st.markdown(f"""
<style>
  @font-face {{ font-family: "Instrument Sans"; font-weight: 400; font-display: swap;
               src: url("/app/static/fonts/instrument-sans-latin-400-normal.woff2") format("woff2"); }}
  @font-face {{ font-family: "Instrument Sans"; font-weight: 500; font-display: swap;
               src: url("/app/static/fonts/instrument-sans-latin-500-normal.woff2") format("woff2"); }}
  @font-face {{ font-family: "Instrument Sans"; font-weight: 600; font-display: swap;
               src: url("/app/static/fonts/instrument-sans-latin-600-normal.woff2") format("woff2"); }}
  @font-face {{ font-family: "Instrument Sans"; font-weight: 700; font-display: swap;
               src: url("/app/static/fonts/instrument-sans-latin-700-normal.woff2") format("woff2"); }}
  @font-face {{ font-family: "Big Shoulders Display"; font-weight: 500; font-display: swap;
               src: url("/app/static/fonts/big-shoulders-display-latin-500-normal.woff2") format("woff2"); }}
  @font-face {{ font-family: "Big Shoulders Display"; font-weight: 700; font-display: swap;
               src: url("/app/static/fonts/big-shoulders-display-latin-700-normal.woff2") format("woff2"); }}
  @font-face {{ font-family: "Big Shoulders Display"; font-weight: 800; font-display: swap;
               src: url("/app/static/fonts/big-shoulders-display-latin-800-normal.woff2") format("woff2"); }}

  .stApp {{ font-family: {BODY}; }}
  /* arena light from above, and the cage's chain-link diamond at 3% in the background */
  .stApp {{ background:
      radial-gradient(1000px 560px at 88% -14%, rgba(124, 77, 255, .20), transparent 62%),
      radial-gradient(800px 520px at -8% 110%, rgba(72, 209, 224, .07), transparent 60%),
      repeating-linear-gradient(45deg, rgba(167, 123, 255, .03) 0 1px, transparent 1px 22px),
      repeating-linear-gradient(-45deg, rgba(167, 123, 255, .03) 0 1px, transparent 1px 22px), {BG}; }}
  .block-container {{ padding-top: 4.5rem; max-width: 1440px; }}
  .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button {{ font-family: {BODY}; }}
  h1, h2, h3, h4 {{ font-family: {DISPLAY}; color: {INK}; letter-spacing: .005em; }}
  p, li {{ color: {INK_2}; }}
  :focus-visible {{ outline: 2px solid {RULE} !important; outline-offset: 2px; }}
  .sr-only {{ position: absolute !important; width: 1px; height: 1px; padding: 0; margin: -1px;
             overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }}
  .skip {{ position: absolute; left: -9999px; top: 8px; z-index: 1000000; background: {RULE}; color: {BG};
          padding: 8px 14px; font-weight: 600; border-radius: 3px; }}
  .skip:focus {{ left: 16px; }}

  /* ---------- top bar: wordmark + underline tabs ---------- */
  header[data-testid="stHeader"] {{
    background: rgba(11, 10, 18, .9); backdrop-filter: blur(10px); height: 3.7rem;
    border-bottom: 1px solid {BORDER};
  }}
  header[data-testid="stHeader"]::before {{
    content: "Stance Intelligence"; position: absolute; left: 28px; top: 50%;
    transform: translateY(-50%); font-family: {DISPLAY}; font-weight: 800; font-size: 1.45rem;
    color: {INK}; letter-spacing: .01em; padding-left: 36px; line-height: 28px;
    background: url("data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2064%2064%22%20role%3D%22img%22%20aria-label%3D%22Stance%20Intelligence%20mark%22%3E%3Cdefs%3E%3CclipPath%20id%3D%22o%22%3E%3Cpolygon%20points%3D%2259.72%2C43.48%2043.48%2C59.72%2020.52%2C59.72%204.28%2C43.48%204.28%2C20.52%2020.52%2C4.28%2043.48%2C4.28%2059.72%2C20.52%22/%3E%3C/clipPath%3E%3C/defs%3E%3Cg%20clip-path%3D%22url%28%23o%29%22%3E%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%23A77BFF%22/%3E%3Crect%20x%3D%2233.5%22%20y%3D%220%22%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%2348D1E0%22/%3E%3C/g%3E%3C/svg%3E") no-repeat left center / 26px 26px;
  }}
  header[data-testid="stHeader"]::after {{
    content: none;
  }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 266px; }}
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
    background: rgba(20, 18, 30, .78); border-right: 1px solid {BORDER}; }}
  section[data-testid="stSidebar"] > div:first-child {{ background: transparent; padding-top: 3.7rem; }}
  [data-testid="stSidebarHeader"] {{ height: .6rem !important; min-height: 0 !important; padding: 0 !important; }}
  section[data-testid="stSidebar"] label p {{ color: {INK_MUTED}; font-size: .8rem; }}
  .sbh {{ font-family: {DISPLAY}; font-weight: 700; font-size: 1.3rem; color: {INK}; margin: 4px 0 10px; }}

  /* ---------- page header ---------- */
  .ph {{ margin: 0 0 18px; max-width: 980px; }}
  .ph h1 {{ font-family: {DISPLAY}; font-weight: 800; font-size: 2.45rem; line-height: 1; text-wrap: balance;
            margin: 0; padding: 0; color: {INK}; }}
  .ph p {{ font-size: 1.02rem; color: {INK_2}; margin: 8px 0 0; max-width: 70ch; line-height: 1.5; }}
  .eyebrow {{ display: none; }}
  .title {{ font-family: {DISPLAY}; font-weight: 800; font-size: 2.45rem; line-height: 1; color: {INK}; }}
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
      radial-gradient(700px 360px at 50% 30%, rgba(124,77,255,.14), transparent 70%), {SURFACE};
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
  .stDownloadButton button[kind="primary"], .stButton button[kind="primary"],
  .stDownloadButton button[kind="primary"] p, .stButton button[kind="primary"] p {{ color: {ON_ACCENT} !important; }}
  [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {{
    border-radius: 3px !important; border: 1px solid {FIELD_BORDER} !important; }}
  [data-baseweb="select"] > div:focus-within, [data-baseweb="input"] > div:focus-within {{
    border-color: {RULE} !important; }}
  [data-testid="stSelectbox"] [role="group"], [data-testid="stMultiSelect"] [role="group"],
  [data-testid="stTextInputRootElement"] {{
    border: 1px solid {FIELD_BORDER} !important; border-radius: 3px !important; }}
  [data-testid="stSelectbox"] [role="group"]:focus-within, [data-testid="stMultiSelect"] [role="group"]:focus-within,
  [data-testid="stTextInputRootElement"]:focus-within {{ border-color: {RULE} !important; }}
  /* selected pills / segmented buttons: white text on the deep-red fill */
  [data-testid="stBaseButton-segmented_controlActive"], [data-testid="stBaseButton-pillsActive"] {{
    background: {ACCENT_FILL} !important; border-color: {ACCENT_FILL} !important; }}
  .stDownloadButton button[kind="primary"], .stButton button[kind="primary"] {{
    background: {ACCENT_FILL} !important; border-color: {ACCENT_FILL} !important; }}
  [data-testid="stBaseButton-segmented_controlActive"] p, [data-testid="stBaseButton-pillsActive"] p {{
    color: {ON_ACCENT} !important; font-weight: 600; }}

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


def _alt(fig) -> str:
    """Short text alternative for a Plotly figure: its title plus the series it draws."""
    title = (fig.layout.title.text or "").replace("<br>", " ") if fig.layout.title else ""
    names = [t.name for t in fig.data if getattr(t, "name", None)]
    kinds = sorted({t.type for t in fig.data})
    desc = f"Chart: {title}." if title else "Chart."
    if names:
        desc += " Series: " + ", ".join(dict.fromkeys(names)) + "."
    return desc + f" ({', '.join(kinds)})"


def chart(fig, key=None, alt: str | None = None):
    """Render a Plotly figure with a screen-reader description (WCAG 1.1.1)."""
    import re
    text = re.sub(r"<[^>]+>", "", alt or _alt(fig))
    st.markdown(f'<p class="sr-only">{escape(text)}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, key=key)


def section(title: str, sub: str | None = None, estimated: bool = False):
    badge = '<span class="est">estimated</span>' if estimated else ""
    st.markdown(f'<div class="sec" role="heading" aria-level="2">{escape(title)}{badge}</div>'
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
