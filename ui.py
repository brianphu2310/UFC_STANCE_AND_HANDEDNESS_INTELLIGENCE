"""Design system: fight-night broadcast.

Smoky black arena, red corner and blue corner, gold for the dominant side. Display type is Big
Shoulders Display set heavy, italic and uppercase like a fight-game menu; body is Instrument Sans,
both self-hosted. Each page opens on a photo banner; panels are dark boxes with a hairline.
"""
import base64
from html import escape
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

# ---------------------------------------------------------------- tokens
BG = "#0A0A0A"          # canvas: arena black
SURFACE = "#151515"     # panels
SURFACE_2 = "#1F1F20"   # raised / hover, inputs
BORDER = "#2E2E30"      # hairlines
INK = "#F5F5F5"
INK_2 = "#C8C8C8"
INK_MUTED = "#8E8E8E"   # 5.9:1 on BG, 5.0:1 on SURFACE_2
ACCENT = "#E5252D"      # red corner: lines, marks and text (4.9:1 on BG)
ACCENT_FILL = "#C8102E" # red for filled buttons, chips, sliders (white text 5.9:1)
ACCENT_2 = "#3B82F6"    # blue corner (5.4:1 on BG)
ACCENT_2_TEXT = "#5B9BFF"
ON_ACCENT = "#FFFFFF"   # text on ACCENT_FILL
FIELD_BORDER = "#5C5C60"  # input outlines: 3.1:1 on SURFACE_2 (WCAG 1.4.11)
RULE = "#E9B44C"        # gold: reference lines, dominant side, focus ring
ACCENT_SOFT = "rgba(229, 37, 45, 0.14)"
MUTED_FILL = "#2A2A2C"   # de-emphasised bars (outside a selection)
SHADOW = "none"

DISPLAY = "'Big Shoulders Display', 'Oswald', 'Arial Narrow', sans-serif"
BODY = "'Instrument Sans', 'Segoe UI', system-ui, sans-serif"

# Categorical palette (dark surface), assigned in a fixed order per dimension.
PALETTE = ["#E5252D", "#3B82F6", "#E9B44C", "#2DBE8C", "#B8B8B8", "#6E6E72"]
SEQ_BLUE = [[0, "#2A0A0E"], [0.5, "#B3121A"], [1, "#FFB3B3"]]   # black -> red -> pale red
GRAD_BAR = ["#3B82F6", "#E5252D"]
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


FONTS = [("Instrument Sans", w, f"instrument-sans-latin-{w}-normal.woff2") for w in (400, 500, 600, 700)] + \
        [("Big Shoulders Display", w, f"big-shoulders-display-latin-{w}-normal.woff2") for w in (500, 700, 800)]


@st.cache_resource
def _font_faces() -> str:
    """@font-face rules with the fonts inlined: Community Cloud serves the app under a path prefix,
    so linked /app/static files can miss; data URIs load everywhere (about 110 KB once cached)."""
    d = Path(__file__).parent / "static" / "fonts"
    return "\n".join(
        f'  @font-face {{ font-family: "{fam}"; font-weight: {w}; font-display: swap; src: '
        f'url("data:font/woff2;base64,{base64.b64encode((d / f).read_bytes()).decode()}") format("woff2"); }}'
        for fam, w, f in FONTS)


def inject_css():
    st.markdown(f"""
<style>
{_font_faces()}

  .stApp {{ font-family: {BODY}; }}
  /* smoky arena: haze from the lights, a few soft bokeh discs and film grain */
  html, body {{ background: {BG}; }}
  .stApp {{ background: transparent !important; }}
  .bgshow .smoke {{ position: absolute; inset: 0; background:
      radial-gradient(circle at 8% 22%, rgba(255,255,255,.05) 0 70px, transparent 120px),
      radial-gradient(circle at 92% 12%, rgba(255,255,255,.045) 0 90px, transparent 150px),
      radial-gradient(circle at 78% 64%, rgba(255,255,255,.03) 0 60px, transparent 110px),
      radial-gradient(circle at 20% 86%, rgba(255,255,255,.03) 0 80px, transparent 140px),
      radial-gradient(1400px 700px at 50% -20%, rgba(255,255,255,.07), transparent 60%),
      url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .05 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"),
      rgba(10,10,10,.82); }}
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
    background: {BG}; height: 3.7rem;
    border-bottom: 1px solid {BORDER};
  }}
  header[data-testid="stHeader"]::before {{
    content: "Stance Intelligence"; position: absolute; left: 28px; top: 50%;
    transform: translateY(-50%); font-family: {DISPLAY}; font-weight: 800; font-size: 1.45rem;
    color: {INK}; letter-spacing: .01em; padding-left: 36px; line-height: 28px;
    background: url("data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2064%2064%22%20role%3D%22img%22%20aria-label%3D%22Stance%20Intelligence%20mark%22%3E%3Cdefs%3E%3CclipPath%20id%3D%22o%22%3E%3Cpolygon%20points%3D%2259.72%2C43.48%2043.48%2C59.72%2020.52%2C59.72%204.28%2C43.48%204.28%2C20.52%2020.52%2C4.28%2043.48%2C4.28%2059.72%2C20.52%22/%3E%3C/clipPath%3E%3C/defs%3E%3Cg%20clip-path%3D%22url%28%23o%29%22%3E%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%23E5252D%22/%3E%3Crect%20x%3D%2233.5%22%20y%3D%220%22%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%233B82F6%22/%3E%3C/g%3E%3C/svg%3E") no-repeat left center / 26px 26px;
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
  section[data-testid="stSidebar"] label p {{ color: {INK_2}; font-size: .86rem; }}
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
  .secsub {{ color: {INK_MUTED}; font-size: .95rem; margin-bottom: 10px; max-width: 75ch; }}

  /* ---------- panels: the octagon cut is the one signature device ---------- */
  .card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 4px; padding: 16px 18px; }}
  .card.oct, .oct {{ border: none; position: relative; background:
      linear-gradient({SURFACE}, {SURFACE}) padding-box;
      clip-path: polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 22px 100%, 0 calc(100% - 22px)); }}
  .card .t {{ font-family: {DISPLAY}; font-weight: 700; font-size: 1.35rem; color: {INK}; line-height: 1.05; }}
  .card .s {{ color: {INK_MUTED}; font-size: .86rem; margin-top: 3px; }}
  .card .b {{ color: {INK_2}; font-size: .94rem; margin-top: 10px; line-height: 1.5; }}
  .card ul {{ margin: 6px 0 0; padding-left: 18px; }}
  .kv {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px; margin-top: 14px; }}
  .kv div {{ font-size: .82rem; color: {INK_MUTED}; }}
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
  [class*="st-key-oct_"] {{ padding: 18px 22px; background: {SURFACE};
      clip-path: polygon(0 0, calc(100% - 30px) 0, 100% 30px, 100% 100%, 30px 100%, 0 calc(100% - 30px)); }}
  [class*="st-key-oct_"] .card {{ background: transparent; border: none; padding: 4px 0; }}
  [class*="st-key-oct_"] [data-testid="stPlotlyChart"] {{ border: none; background: transparent; }}

  .simlist {{ border-top: 1px solid {BORDER}; }}
  .simrow {{ display: grid; grid-template-columns: 1fr 90px 34px; gap: 12px; align-items: center;
             padding: 9px 0; border-bottom: 1px solid {BORDER}; }}
  .simrow b {{ display: block; font-family: {DISPLAY}; font-size: 1.15rem; font-weight: 700; color: {INK}; }}
  .simrow span {{ font-size: .84rem; color: {INK_MUTED}; }}
  .simbar {{ height: 4px; background: {SURFACE_2}; }}
  .simbar i {{ display: block; height: 4px; background: {INK}; }}
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

  .foot {{ color: {INK_MUTED}; font-size: .86rem; padding: 26px 0 8px; border-top: 1px solid {BORDER};
           margin-top: 40px; display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; }}
  .foot a {{ color: {INK_2}; }}
  /* ================= broadcast layer: fight-game menu type, red corner, photo banners ================= */
  h1, h2, h3, .sec, .card .t, .sbh, .kv b, .score, [data-testid="stMetricValue"], .simrow b {{
    font-style: italic; text-transform: uppercase; letter-spacing: .005em; }}
  header[data-testid="stHeader"] {{ background: linear-gradient(#141414, #0A0A0A) !important; border-bottom: 1px solid #262628; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{ margin: 0 5px !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span {{ font-family: {DISPLAY}; font-style: italic; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0; font-size: .95rem !important; color: {INK} !important; white-space: nowrap; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] {{ border-bottom: 3px solid {ACCENT} !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] span {{ color: {ACCENT} !important; }}

  /* page banner: a photo framed in white, the title set over its dark side */
  .hero {{ position: relative; height: 300px; margin: 0 0 26px; border: 4px solid #E9E9E9;
           background: #0B0B0B right center / auto 100% no-repeat;
           box-shadow: 0 18px 40px rgba(0,0,0,.6); overflow: hidden; }}
  .hero::before {{ content: ""; position: absolute; inset: 0;
           background: linear-gradient(90deg, #0B0B0B 0%, #0B0B0B 30%, rgba(11,11,11,.75) 50%, rgba(11,11,11,0) 72%); }}
  .hero .in {{ position: absolute; left: 34px; bottom: 30px; right: 40%; }}
  .hero .kicker {{ font-family: {DISPLAY}; font-style: italic; font-weight: 800; font-size: 1.05rem; letter-spacing: .03em;
           text-transform: uppercase; color: {ACCENT}; margin: 0 0 6px; }}
  .hero .kicker i {{ font-style: italic; color: #fff; background: {ACCENT_FILL}; padding: 0 7px; margin-right: 8px; }}
  .hero h1 {{ font-family: {DISPLAY} !important; font-weight: 800 !important; font-size: 3.6rem !important; line-height: .95 !important; margin: 0 !important; color: #fff !important;
           text-shadow: 0 2px 0 rgba(0,0,0,.4); }}
  .hero p {{ color: #DADADA !important; font-size: 1.02rem !important; margin: 10px 0 0 !important; max-width: 62ch; }}
  .hero .credit {{ position: absolute; right: 10px; bottom: 6px; font-size: .68rem; color: rgba(255,255,255,.6); }}

  /* panels: dark boxes with a hairline and a lighter top edge, like the game's menu tiles */
  .card, [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{ border-radius: 0 !important;
    background: linear-gradient(#1A1A1A, #121212 120px) !important; border: 1px solid #2E2E30 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.05); }}
  [class*="st-key-oct_"] {{ background: linear-gradient(#1A1A1A, #111 160px) !important; border: 1px solid #2E2E30;
    clip-path: none !important; }}
  [class*="st-key-oct_"] .card {{ background: transparent !important; border: none !important; box-shadow: none; }}

  /* section heads: big italic caps over a red underline stub */
  .sec {{ font-size: 1.9rem !important; font-weight: 800 !important; border-top: 1px solid #2E2E30 !important; padding-top: 18px !important; }}
  .sec::after {{ content: ""; display: block; width: 48px; height: 3px; background: {ACCENT}; margin-top: 6px; }}
  .sbh {{ font-weight: 800; font-size: 1.45rem; padding-bottom: 6px; border-bottom: 3px solid {ACCENT}; display: inline-block; }}

  /* controls: the chosen option is a red block */
  [data-testid="stSlider"] [role="group"] > div > div:has(input[type="range"]) {{
    width: 16px !important; height: 16px !important; border-radius: 50% !important; background: #fff !important;
    border: 3px solid {ACCENT_FILL} !important; box-shadow: none !important; }}
  [data-testid="stSliderThumbValue"] p {{ font-family: {DISPLAY}; font-style: italic; font-weight: 800; font-size: 1.05rem !important; color: #fff !important; }}
  [data-testid="stSliderTickBar"] p {{ color: {INK_MUTED} !important; font-size: .74rem !important; }}
  [data-testid="stRadioGroup"] {{ display: inline-flex !important; flex-direction: row !important; gap: 0 !important;
    border: 1px solid {FIELD_BORDER}; overflow: hidden; }}
  [data-testid="stRadioGroup"] {{ flex-wrap: nowrap !important; width: auto !important; }}
  [data-testid="stRadioGroup"] > div {{ margin: 0 !important; width: auto !important; flex: 0 0 auto !important; }}
  [data-testid="stRadioGroup"] > div + div {{ border-left: 1px solid {FIELD_BORDER}; }}
  [data-testid="stRadioOption"] {{ padding: 6px 16px !important; margin: 0 !important; cursor: pointer; }}
  [data-testid="stRadioOption"] > div > div:first-child {{ display: none !important; }}
  [data-testid="stRadioOption"] p {{ color: {INK_2} !important; font-weight: 700; text-transform: uppercase; font-size: .82rem; letter-spacing: .04em; }}
  [data-testid="stRadioOption"][data-selected="true"] {{ background: {ACCENT_FILL}; }}
  [data-testid="stRadioOption"][data-selected="true"] p {{ color: #fff !important; }}
  [data-testid="stButtonGroup"] button {{ border-color: {FIELD_BORDER} !important; border-radius: 0 !important;
    padding-left: 12px !important; padding-right: 12px !important; }}
  [data-testid="stButtonGroup"] button p {{ font-weight: 700; color: {INK_2}; text-transform: uppercase; font-size: .8rem; letter-spacing: .02em; }}
  [data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-pressed="true"],
  [data-testid="stBaseButton-segmented_controlActive"], [data-testid="stBaseButton-pillsActive"] {{
    background: {ACCENT_FILL} !important; border-color: {ACCENT_FILL} !important; }}
  [data-testid="stButtonGroup"] button[aria-checked="true"] p, [data-testid="stButtonGroup"] button[aria-pressed="true"] p,
  [data-testid="stBaseButton-segmented_controlActive"] p, [data-testid="stBaseButton-pillsActive"] p {{ color: #fff !important; }}

  /* tabs: italic caps, red bar under the open one */
  [data-testid="stTabs"] [role="tablist"] {{ gap: 28px; border-bottom: 1px solid #2E2E30; }}
  [data-testid="stTab"] {{ padding: 10px 0 !important; }}
  [data-testid="stTab"] p {{ font-family: {DISPLAY}; font-style: italic; font-weight: 800; font-size: 1.15rem !important;
    text-transform: uppercase; color: {INK_MUTED}; }}
  [data-testid="stTab"][aria-selected="true"] p {{ color: #fff; }}
  [data-testid="stTabs"] .react-aria-SelectionIndicator {{ background: {ACCENT} !important; height: 3px !important; }}

  /* buttons: red with a play arrow, the game's "Watch trailer" button */
  [data-baseweb="select"] > div, [data-testid="stTextInputRootElement"] {{ border-radius: 0 !important; }}
  .stDownloadButton button, .stButton button[kind="primary"] {{ border-radius: 0 !important;
    background: linear-gradient(#E0202B, #A80D1A) !important; border: 1px solid #FF5A62 !important; }}
  .stDownloadButton button p, .stButton button[kind="primary"] p {{ color: #fff !important; font-family: {DISPLAY};
    font-style: italic; font-weight: 800; text-transform: uppercase; font-size: 1.05rem; letter-spacing: .02em; }}
  .stDownloadButton button p::after {{ content: ""; display: inline-block; margin-left: 8px; border: 6px solid transparent; border-left: 9px solid #fff; border-right: 0; vertical-align: 1px; }}
  [data-testid="stMetricDelta"] {{ color: {INK_2} !important; }}
  section[data-testid="stSidebar"] {{ background: linear-gradient(#161616, #0C0C0C) !important; border-right: 1px solid #262628 !important; }}
  .callout {{ border-left-color: {ACCENT} !important; }}
  .st-key-globepanel [data-testid="stButtonGroup"] button p {{ text-transform: none; font-size: .9rem; letter-spacing: 0; }}
  .ph h1 {{ font-weight: 800; }}
  /* phones: the sidebar starts closed; keep its open and close buttons so the filters stay reachable */
  @media (max-width: 640px) {{
    [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"] {{ display: inline-flex !important; }}
    header[data-testid="stHeader"]::before {{ display: none; }}
    header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 8px; }}
  }}
  /* ================= motion: page entrance, scroll reveal, tab switch, running state ================= */
  [data-testid="stMain"] {{ scroll-behavior: smooth; }}
  /* page entrance: the blocks of a page rise in one after another the first time it renders */
  .block-container > div > [data-testid="stVerticalBlock"] > div:not(:has([class*="st-key-introbox"])):not(:has(.bgshow)) {{ animation: riseIn .55s cubic-bezier(.2,.7,.2,1) both; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(2) {{ animation-delay: .06s; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(3) {{ animation-delay: .12s; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(4) {{ animation-delay: .18s; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(n+5) {{ animation-delay: .24s; }}
  /* scrolling: cards, charts and tables slide up and sharpen as they come into view, in both directions */
  @supports (animation-timeline: view()) {{
    .card, .mcard, .bout, .tape, [data-testid="stPlotlyChart"], [data-testid="stDataFrame"], .simrow, .sec {{
      animation: scrollIn linear both; animation-timeline: view(); animation-range: entry 0% entry 70%; }}
  }}
  /* tabs: the new panel fades and slides in, the red bar glides under the tab */
  [role="tabpanel"] {{ animation: tabIn .38s cubic-bezier(.2,.7,.2,1) both; }}
  [data-testid="stTabs"] .react-aria-SelectionIndicator {{ transition: left .3s cubic-bezier(.2,.7,.2,1), width .3s ease !important; }}
  [data-testid="stTab"] p {{ transition: color .2s ease; }}
  /* hover: panels lift, buttons press */
  .card, .bout, [data-testid="stPlotlyChart"] {{ transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease; }}
  .card:hover, [data-testid="stPlotlyChart"]:hover {{ border-color: #4a4a4e !important; box-shadow: 0 14px 30px -18px rgba(0,0,0,.9); }}
  .stButton button, .stDownloadButton button, [data-testid="stButtonGroup"] button, [data-testid="stRadioOption"] {{
    transition: transform .12s ease, background-color .2s ease, filter .2s ease; }}
  .stButton button:active, .stDownloadButton button:active, [data-testid="stButtonGroup"] button:active {{ transform: scale(.96); }}
  /* running: a red bar sweeps under the nav and the stale content dims and blurs a touch */
  .stApp[data-test-script-state="running"] header[data-testid="stHeader"]::after {{
    content: "" !important; position: absolute; left: 0; bottom: -1px; height: 3px; width: 32%;
    background: linear-gradient(90deg, transparent, {ACCENT}, #FF7A7F, {ACCENT}, transparent);
    animation: sweep 1s cubic-bezier(.4,0,.2,1) infinite; z-index: 5; }}
  .stApp[data-test-script-state="running"] [data-stale="true"]:not(:has(.bgshow)) {{ opacity: .45 !important; filter: blur(1.5px) saturate(.6);
    transition: opacity .25s ease .15s, filter .25s ease .15s; }}
  [data-stale="false"] {{ transition: opacity .3s ease, filter .3s ease; }}
  @keyframes riseIn {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes scrollIn {{ from {{ opacity: .15; transform: translateY(36px) scale(.985); filter: blur(3px); }}
                         to {{ opacity: 1; transform: none; filter: none; }} }}
  @keyframes tabIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes sweep {{ from {{ left: -32%; }} to {{ left: 100%; }} }}
  /* backdrop: fight photos cross-fading behind every page, in a random order, under a dark smoky veil */
  .st-key-backdrop {{ position: absolute; height: 0; overflow: visible; margin: 0 !important; }}
  .bgshow {{ position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; background: {BG}; }}
  .bgshow i {{ position: absolute; inset: -4%; background: center 30% / cover no-repeat; opacity: 0;
               filter: grayscale(.35) contrast(1.05); animation: bgCycle var(--cycle) linear infinite; animation-delay: var(--d); }}
  @keyframes bgCycle {{ 0% {{ opacity: 0; transform: scale(1.08); }} 4% {{ opacity: 1; }} 18% {{ opacity: 1; }}
                        24% {{ opacity: 0; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(1); }} }}
  /* the nav takes the whole header row, so all pages fit before "N more" kicks in */
  header[data-testid="stHeader"] [data-testid="stToolbar"] > div {{ flex: 1 1 auto !important; min-width: 0; }}
  header[data-testid="stHeader"] nav[data-testid="stTopNav"] {{ flex: 1 1 auto !important; min-width: 0; max-width: none !important; }}
  /* the deploy / menu group keeps only the room its buttons need */
  header[data-testid="stHeader"] [data-testid="stToolbar"] > div > div:has(> [data-testid="stToolbarActions"]) {{ min-width: 0 !important; width: auto !important; }}
  /* laptops with the sidebar open: tighter items so the whole nav still fits */
  @media (max-width: 1400px) {{
    .stApp:has(section[data-testid="stSidebar"]) header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 236px; }}
    .stApp:has(section[data-testid="stSidebar"]) header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{ margin: 0 1px !important; padding-left: 4px !important; padding-right: 4px !important; }}
    .stApp:has(section[data-testid="stSidebar"]) header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span {{ font-size: .86rem !important; letter-spacing: 0 !important; }}
  }}
  /* phones: the banner grows with its text, photo behind a top-down fade */
  @media (max-width: 640px) {{
    .hero {{ height: auto; min-height: 220px; background-position: 70% center; background-size: cover; }}
    .hero::before {{ background: linear-gradient(0deg, rgba(0,0,0,.94) 0%, rgba(0,0,0,.75) 55%, rgba(0,0,0,.35) 100%); }}
    .hero .in {{ position: relative; left: auto; right: auto; bottom: auto; padding: 70px 18px 20px; }}
    .hero h1 {{ font-size: 2.3rem !important; }}
    .hero p {{ font-size: .92rem !important; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
</style>""", unsafe_allow_html=True)


KICKER = {"value": "", "slug": ""}   # "02 · Explorer" and its photo slug, set per page by the app
HERO_DIR = Path(__file__).parent / "static" / "hero"


@st.cache_data
def _hero_photo(slug: str) -> tuple[str, str]:
    """(data URI, credit) for static/hero/<slug>.*, falling back to default.*; ("", "") when none."""
    credits = {}
    f = HERO_DIR / "credits.csv"
    if f.exists():
        import csv
        credits = {r["key"]: r["credit"] for r in csv.DictReader(f.open())}
    for key in (slug, "default"):
        for img in sorted(HERO_DIR.glob(f"{key}.*")):
            if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                mime = "image/jpeg" if img.suffix.lower() in (".jpg", ".jpeg") else f"image/{img.suffix[1:].lower()}"
                return (f"data:{mime};base64,{base64.b64encode(img.read_bytes()).decode()}", credits.get(key, ""))
    return "", ""


BACKDROP = ["home", "explorer", "stance-lab", "build-a-fighter", "spar-vs-brian", "data", "intro-photo"]


def backdrop():
    """Fight photos cross-fading behind every page, in a fresh random order each session."""
    import random
    order = st.session_state.setdefault("bg_order", random.sample(BACKDROP, len(BACKDROP)))
    photos = [u for u in (_hero_photo(k)[0] for k in order) if u]
    if not photos:
        return
    step = 6.0                                           # seconds each photo leads
    cycle = step * len(photos)
    layers = "".join(f'<i style="background-image:url({u});--d:{i * step:.1f}s"></i>' for i, u in enumerate(photos))
    # every photo holds about a fifth of the cycle; with seven photos that overlaps a little, a slow dissolve
    with st.container(key="backdrop"):
        st.markdown(f'<div class="bgshow" aria-hidden="true" style="--cycle:{cycle:.0f}s">{layers}'
                    '<div class="smoke"></div></div>', unsafe_allow_html=True)


def page_header(title: str, dek: str | None = None):
    """The page banner: a photo from static/hero, the page number and title over its dark side."""
    k = KICKER["value"]
    uri, credit = _hero_photo(KICKER["slug"])
    bg = f' style="background-image:url({uri})"' if uri else ""
    st.markdown(f'<div class="hero"{bg}><div class="in">' + (f'<div class="kicker">{k}</div>' if k else "")
                + f'<h1>{escape(title)}</h1>' + (f'<p>{escape(dek)}</p>' if dek else "") + '</div>'
                + (f'<div class="credit">Photo: {escape(credit)}</div>' if credit else "") + '</div>',
                unsafe_allow_html=True)


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
