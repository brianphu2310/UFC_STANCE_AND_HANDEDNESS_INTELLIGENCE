"""Design system: fight intelligence.

Charcoal ground, panels one step lighter with a 1px border, square-ish corners. Headlines are Big
Shoulders Display set heavy and upright in capitals, like a broadcast lower third; everything else
is Inter. Red is the one accent: the active page, the primary action, and in charts the southpaw
(the side the research asks about). Orthodox is drawn in steel, switch in brass.
"""
import base64
from html import escape
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

# ---------------------------------------------------------------- tokens
BG = "#0B0B0D"          # ground: bar, page and gutters
SURFACE = "#131316"     # panels
SURFACE_2 = "#1A1A1F"   # inputs, nested areas, hover
RAISED = "#24242A"      # selected segment, tracks
BORDER = "#26262C"      # 1px panel edges and rules
CONTROL = "#3A3A42"     # control outlines
INK = "#F5F5F5"
INK_2 = "#A9A9B1"       # secondary text (8.2:1 on SURFACE)
INK_MUTED = "#86868F"   # meta (5.3:1 on SURFACE)
ACCENT = "#E5383B"      # fight red: the active page, the primary action, the southpaw in charts (4.9:1 on BG)
ACCENT_FILL = "#C81E2A" # red fill behind white text (5.9:1)
ON_ACCENT = "#FFFFFF"
STEEL = "#C9CCD3"       # orthodox in charts; the B corner in a matchup
BRASS = "#C9A227"       # switch in charts; the dominant side
ACCENT_2 = STEEL
ACCENT_2_TEXT = STEEL
RULE = BRASS
FIELD_BORDER = CONTROL
MUTED_FILL = "#2C2C33"  # bars outside a selection
SHADOW = "none"
NEGATIVE = "#F06A6C"

FONT = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"
BODY = FONT
DISPLAY = "'Big Shoulders Display', 'Arial Narrow', sans-serif"   # headlines and section titles

# Data palette in a fixed order per dimension (Orthodox, Southpaw, Switch / Right, Left / ...):
# the majority in steel, "the other side" in red, a third group in brass, then neutrals.
PALETTE = [STEEL, ACCENT, BRASS, "#6E6E78", "#4A4A52", "#34343B"]
SEQ_BLUE = [[0, "#2A2A30"], [1, "#F5F5F5"]]   # grey ramp: brighter means more
GRAD_BAR = [STEEL, ACCENT]
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
    return BG if (lum + 0.05) / 0.0535 > 1.05 / (lum + 0.05) else "#FFFFFF"   # 0.0535 = L(BG) + 0.05


def colors_for(dim_label: str) -> dict:
    _, order = core.GROUP_DIMS[dim_label]
    return dict(zip(order, PALETTE))


FONTS = [("Inter", "400 600", "inter-latin-variable.woff2")] + \
        [("Big Shoulders Display", w, f"big-shoulders-display-latin-{w}-normal.woff2") for w in (500, 700, 800)]


@st.cache_resource
def _font_faces() -> str:
    """@font-face rules with the fonts inlined: Community Cloud serves the app under a path prefix,
    so linked /app/static files can miss; data URIs load everywhere (about 75 KB once cached)."""
    d = Path(__file__).parent / "static" / "fonts"
    return "\n".join(
        f'  @font-face {{ font-family: "{fam}"; font-weight: {w}; font-display: swap; src: '
        f'url("data:font/woff2;base64,{base64.b64encode((d / f).read_bytes()).decode()}") format("woff2"); }}'
        for fam, w, f in FONTS)


MARK = ("data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2064%2064%22%3E"
        "%3Cdefs%3E%3CclipPath%20id%3D%22o%22%3E%3Cpolygon%20points%3D%2259.72%2C43.48%2043.48%2C59.72%2020.52%2C59.72%20"
        "4.28%2C43.48%204.28%2C20.52%2020.52%2C4.28%2043.48%2C4.28%2059.72%2C20.52%22/%3E%3C/clipPath%3E%3C/defs%3E"
        "%3Cg%20clip-path%3D%22url%28%23o%29%22%3E%3Crect%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%23C9CCD3%22/%3E"
        "%3Crect%20x%3D%2233.5%22%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%23E5383B%22/%3E%3C/g%3E%3C/svg%3E")
PAGES = {}     # st.Page objects by key, filled by the app so views can link with st.switch_page
COL = 1208     # the content column, px; the bar's wordmark sits on its left edge


def inject_css():
    st.markdown(f"""
<style>
{_font_faces()}
  html, body, .stApp {{ background: {BG} !important; }}
  .stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp td, .stApp th {{
    font-family: {FONT}; }}
  .stApp {{ color: {INK}; }}
  p, li {{ color: {INK_2}; font-size: 14px; line-height: 1.6; }}
  h1, h2, h3, h4 {{ font-family: {DISPLAY}; color: {INK}; }}
  b, strong {{ color: {INK}; font-weight: 600; }}
  .num, [data-testid="stMetricValue"], [data-testid="stSliderThumbValue"] {{ font-variant-numeric: tabular-nums; }}
  :focus-visible {{ outline: 2px solid {ACCENT} !important; outline-offset: 2px; }}
  ::selection {{ background: {ACCENT_FILL}; color: #fff; }}
  .sr-only {{ position: absolute !important; width: 1px; height: 1px; padding: 0; margin: -1px;
             overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }}

  /* ---------- shell: a 56px bar over one centred 1208px column ---------- */
  .block-container {{ max-width: {COL + 48}px; padding: 88px 24px 40px !important; }}
  header[data-testid="stHeader"] {{ background: {BG}; height: 56px; border-bottom: 1px solid {BORDER}; }}
  header[data-testid="stHeader"]::before {{
    content: "STANCE INTELLIGENCE"; position: absolute; top: 50%; transform: translateY(-50%);
    left: max(24px, calc((100vw - {COL}px) / 2)); padding-left: 32px;
    font: 800 19px/24px {DISPLAY}; letter-spacing: .04em; color: {INK}; white-space: nowrap;
    background: url("{MARK}") no-repeat left center / 22px 22px; }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: calc(max(24px, calc((100vw - {COL}px) / 2)) + 230px); }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] > div {{ flex: 1 1 auto !important; min-width: 0; }}
  header[data-testid="stHeader"] nav[data-testid="stTopNav"] {{ flex: 1 1 auto !important; min-width: 0; max-width: none !important; }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] > div > div:has(> [data-testid="stToolbarActions"]) {{ min-width: 0 !important; width: auto !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{ background: transparent !important; border-radius: 0;
    padding: 17px 9px 15px !important; margin: 0 !important; border-bottom: 2px solid transparent; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span {{ font: 500 13px/20px {FONT}; color: {INK_2} !important;
    letter-spacing: .02em; white-space: nowrap; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"]:hover span,
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] span {{ color: {INK} !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] {{ border-bottom-color: {ACCENT}; }}
  [data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] {{ display: none !important; }}
  /* phones: Streamlit moves the page list into the sidebar, so it stays, styled as a plain menu sheet */
  section[data-testid="stSidebar"] {{ background: {SURFACE} !important; border-right: 1px solid {BORDER}; }}
  section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{ border-radius: 2px; min-height: 44px; padding: 0 14px !important; }}
  section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] span {{ font: 500 15px/1.4 {FONT}; color: {INK_2}; }}
  section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {{ background: {RAISED}; box-shadow: inset 2px 0 0 {ACCENT}; }}
  section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] span {{ color: {INK}; }}
  [data-testid="stExpandSidebarButton"] {{ color: {INK} !important; }}
  @media (max-width: 1100px) {{
    header[data-testid="stHeader"]::before {{ content: ""; width: 22px; padding-left: 0; }}
    header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 64px; }}
    header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{ padding: 17px 7px 15px !important; }}
  }}
  @media (max-width: 640px) {{
    header[data-testid="stHeader"]::before {{ display: none; }}
    header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 8px; }}
    .block-container {{ padding: 72px 16px 32px !important; }}
  }}

  /* ---------- the title row ---------- */
  .ph {{ margin: 0 0 24px; padding-bottom: 20px; border-bottom: 1px solid {BORDER}; }}
  .ph .k {{ font: 600 12px/1 {FONT}; letter-spacing: .14em; text-transform: uppercase; color: {ACCENT}; margin: 0 0 10px; }}
  .ph h1 {{ font: 800 44px/0.98 {DISPLAY} !important; text-transform: uppercase; letter-spacing: .005em;
            color: {INK}; margin: 0 !important; padding: 0 !important; }}
  .ph p {{ font-size: 15px; color: {INK_2}; margin: 10px 0 0; max-width: 82ch; line-height: 1.55; }}
  .ph p b {{ color: {INK}; font-weight: 600; }}
  @media (max-width: 640px) {{ .ph h1 {{ font-size: 32px !important; }} }}

  /* ---------- sections ---------- */
  .sec {{ font: 700 24px/1.05 {DISPLAY}; text-transform: uppercase; letter-spacing: .01em; color: {INK}; margin: 44px 0 4px; }}
  .secsub {{ color: {INK_MUTED}; font-size: 13px; margin: 0 0 14px; max-width: 82ch; line-height: 1.5; }}

  /* ---------- panels: 1px edge, 4px corners, no shadow ---------- */
  .card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 4px; padding: 18px 20px; }}
  .card .t {{ font: 700 20px/1.1 {DISPLAY}; text-transform: uppercase; letter-spacing: .01em; color: {INK}; }}
  .card .s {{ color: {INK_MUTED}; font-size: 13px; margin-top: 4px; line-height: 1.4; }}
  .card .b {{ color: {INK_2}; font-size: 14px; margin-top: 10px; line-height: 1.6; }}
  .card ul {{ margin: 6px 0 0; padding-left: 18px; }}
  .card li {{ margin: 2px 0; }}
  .kv {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 14px 16px; margin-top: 16px; }}
  .kv div {{ min-width: 0; overflow-wrap: anywhere; }}
  .kv div {{ font-size: 12px; color: {INK_MUTED}; }}
  .kv b {{ display: block; color: {INK}; font: 500 20px/1.2 {FONT}; margin-top: 2px; font-variant-numeric: tabular-nums; }}
  .kv b small {{ font-size: 13px; color: {INK_MUTED}; font-weight: 400; }}
  .pill {{ display: inline-block; padding: 2px 8px; border-radius: 2px; font-size: 12px; font-weight: 500;
           border: 1px solid {CONTROL}; color: {INK_2}; margin: 2px 4px 2px 0; white-space: nowrap; }}
  .est {{ display: inline-block; padding: 0 5px; border-radius: 2px; font-size: 11px; font-weight: 500;
          border: 1px solid rgba(201,162,39,.5); color: {BRASS}; margin-left: 6px; vertical-align: 2px; font-family: {FONT}; }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; vertical-align: 1px; }}
  .score {{ font: 800 30px/1 {DISPLAY}; color: {INK}; font-variant-numeric: tabular-nums; }}
  .score small {{ font: 400 13px {FONT}; color: {INK_MUTED}; }}
  .callout {{ background: {SURFACE}; border: 1px solid {BORDER}; border-left: 2px solid {ACCENT}; border-radius: 0 4px 4px 0;
              padding: 14px 18px; color: {INK_2}; font-size: 14px; line-height: 1.6; }}
  .callout b {{ color: {INK}; }}
  [class*="st-key-oct_"] {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 4px; padding: 16px 20px 12px; }}
  [class*="st-key-oct_"] .card {{ background: {SURFACE_2}; }}
  [class*="st-key-oct_"] [data-testid="stPlotlyChart"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}

  .simlist {{ padding: 0; }}
  .simrow {{ display: grid; grid-template-columns: 1fr 72px 32px; gap: 12px; align-items: center;
             padding: 10px 0; border-bottom: 1px solid {BORDER}; min-height: 44px; }}
  .simrow:last-child {{ border-bottom: none; }}
  .simrow b {{ display: block; font: 500 14px/1.3 {FONT}; color: {INK}; }}
  .simrow span {{ font-size: 12px; color: {INK_MUTED}; }}
  .simbar {{ height: 3px; background: {RAISED}; }}
  .simbar i {{ display: block; height: 3px; background: {INK_2}; }}
  .simrow em {{ font: 500 14px/1 {FONT}; font-style: normal; color: {INK}; text-align: right; font-variant-numeric: tabular-nums; }}

  /* ---------- widgets ---------- */
  [data-testid="stMetric"] {{ background: transparent; padding: 0; }}
  [data-testid="stMetricLabel"] p {{ color: {INK_MUTED}; font-size: 12px; }}
  [data-testid="stMetricValue"] {{ font: 800 30px/1.1 {DISPLAY}; color: {INK}; }}
  [data-testid="stMetricDelta"] {{ color: {INK_2} !important; font-size: 13px; }}
  [data-testid="stPlotlyChart"] {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 4px; padding: 6px 4px 2px; overflow: hidden; }}
  [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 4px; overflow: hidden; }}
  [data-testid="stWidgetLabel"] p, label p {{ color: {INK_2} !important; font-size: 12px !important; font-weight: 500; letter-spacing: .02em; }}
  [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-testid="stTextInputRootElement"] {{
    background: {SURFACE} !important; border: 1px solid {CONTROL} !important; border-radius: 3px !important; min-height: 38px; }}
  [data-baseweb="select"] > div:focus-within, [data-testid="stTextInputRootElement"]:focus-within {{ border-color: {INK_2} !important; }}
  .stButton button, .stDownloadButton button, [data-testid="stPopover"] button, .stLinkButton a {{
    border-radius: 2px !important; min-height: 38px; padding: 0 16px !important; background: transparent !important;
    border: 1px solid {CONTROL} !important; box-shadow: none !important; }}
  .stButton button p, .stDownloadButton button p, [data-testid="stPopover"] button p, .stLinkButton a p {{
    color: {INK} !important; font-weight: 600; font-size: 13px; letter-spacing: .04em; text-transform: uppercase; }}
  .stButton button[kind="primary"], .stDownloadButton button[kind="primary"], .stLinkButton a[kind="primary"] {{
    background: {ACCENT_FILL} !important; border-color: {ACCENT_FILL} !important; }}
  .stButton button:hover, .stDownloadButton button:hover, [data-testid="stPopover"] button:hover, .stLinkButton a:hover {{ border-color: {INK_2} !important; }}
  .stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover {{ background: #DA2532 !important; border-color: #DA2532 !important; }}
  [data-testid="stPopoverBody"] {{ background: {SURFACE_2} !important; border: 1px solid {CONTROL} !important; border-radius: 4px !important; }}

  [data-testid="stButtonGroup"] {{ gap: 0 !important; }}
  [data-testid="stButtonGroup"] button {{ background: transparent !important; border: 1px solid {CONTROL} !important;
    border-radius: 0 !important; min-height: 34px; padding: 0 12px !important; box-shadow: none !important; }}
  [data-testid="stButtonGroup"] button + button {{ margin-left: -1px; }}
  [data-testid="stButtonGroup"] button:first-child {{ border-radius: 3px 0 0 3px !important; }}
  [data-testid="stButtonGroup"] button:last-child {{ border-radius: 0 3px 3px 0 !important; }}
  [data-testid="stButtonGroup"] button p {{ color: {INK_2} !important; font-weight: 500; font-size: 13px; }}
  [data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stBaseButton-segmented_controlActive"],
  [data-testid="stBaseButton-pillsActive"] {{
    background: {RAISED} !important; border-color: {INK_2} !important; position: relative; z-index: 1; }}
  [data-testid="stButtonGroup"] button[aria-checked="true"] p, [data-testid="stBaseButton-segmented_controlActive"] p,
  [data-testid="stBaseButton-pillsActive"] p {{ color: {INK} !important; }}
  [data-testid="stButtonGroup"] button:hover p {{ color: {INK} !important; }}
  [data-testid="stRadioGroup"] {{ display: inline-flex !important; flex-direction: row !important; flex-wrap: nowrap !important;
    gap: 0 !important; width: auto !important; border: 1px solid {CONTROL}; border-radius: 3px; overflow: hidden; }}
  [data-testid="stRadioGroup"] > div {{ margin: 0 !important; width: auto !important; flex: 0 0 auto !important; }}
  [data-testid="stRadioGroup"] > div + div {{ border-left: 1px solid {CONTROL}; }}
  [data-testid="stRadioOption"] {{ padding: 7px 14px !important; margin: 0 !important; cursor: pointer; }}
  [data-testid="stRadioOption"] > div > div:first-child {{ display: none !important; }}
  [data-testid="stRadioOption"] p {{ color: {INK_2} !important; font-weight: 500; font-size: 13px; }}
  [data-testid="stRadioOption"][data-selected="true"] {{ background: {RAISED}; }}
  [data-testid="stRadioOption"][data-selected="true"] p {{ color: {INK} !important; }}
  [data-testid="stSlider"] [role="group"] > div > div:has(input[type="range"]) {{
    width: 14px !important; height: 14px !important; border-radius: 50% !important; background: {INK} !important;
    border: 3px solid {ACCENT_FILL} !important; box-shadow: none !important; }}
  [data-testid="stSliderThumbValue"] p {{ font: 600 13px/1 {FONT} !important; color: {INK} !important; }}
  [data-testid="stSliderTickBar"] p {{ color: {INK_MUTED} !important; font-size: 12px !important; }}

  [data-testid="stTabs"] [role="tablist"] {{ gap: 28px; border-bottom: 1px solid {BORDER}; }}
  [data-testid="stTab"] {{ padding: 12px 0 !important; }}
  [data-testid="stTab"] p {{ font: 700 17px/1 {DISPLAY} !important; text-transform: uppercase; letter-spacing: .03em; color: {INK_MUTED}; }}
  [data-testid="stTab"]:hover p, [data-testid="stTab"][aria-selected="true"] p {{ color: {INK}; }}
  [data-testid="stTabs"] .react-aria-SelectionIndicator {{ background: {ACCENT} !important; height: 2px !important;
    transition: left .3s cubic-bezier(.2,.7,.2,1), width .3s ease !important; }}

  [data-testid="stElementContainer"]:has(.sr-only:only-child) {{ margin-bottom: -1rem; height: 0; overflow: hidden; }}
  [data-testid="stCaptionContainer"] p, .stCaption p {{ font-size: 12px !important; color: {INK_MUTED} !important; }}
  [data-testid="stAlert"] {{ border-radius: 4px; }}
  .empty {{ border: 1px dashed {CONTROL}; border-radius: 4px; padding: 14px 18px; font-size: 14px; color: {INK_2}; }}

  .foot {{ color: {INK_MUTED}; font-size: 12px; padding: 22px 0 4px; margin-top: 56px; border-top: 1px solid {BORDER};
           display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; }}
  .foot a {{ color: {INK_2}; }}

  /* ---------- motion: a quiet rise on arrival, feedback on every control ---------- */
  .block-container > div > [data-testid="stVerticalBlock"] > div:not(:has([class*="st-key-introbox"])) {{
    animation: rise .45s cubic-bezier(.2,.7,.2,1) both; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(2) {{ animation-delay: .04s; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(3) {{ animation-delay: .08s; }}
  .block-container > div > [data-testid="stVerticalBlock"] > div:nth-child(n+4) {{ animation-delay: .12s; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
  [role="tabpanel"] {{ animation: rise .3s ease both; }}
  .stButton button, .stDownloadButton button, [data-testid="stButtonGroup"] button, [data-testid="stRadioOption"],
  .card, [data-testid="stPlotlyChart"], header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{
    transition: background-color .15s ease, border-color .15s ease, transform .1s ease; }}
  .card:hover, [data-testid="stPlotlyChart"]:hover {{ border-color: #34343C; }}
  .stButton button:active, .stDownloadButton button:active, [data-testid="stButtonGroup"] button:active {{ transform: scale(.98); }}
  .stApp[data-test-script-state="running"] header[data-testid="stHeader"]::after {{
    content: ""; position: absolute; left: 0; bottom: -1px; height: 2px; width: 24%; background: {ACCENT};
    animation: sweep 1.1s cubic-bezier(.4,0,.2,1) infinite; z-index: 5; }}
  .stApp[data-test-script-state="running"] [data-stale="true"] {{ opacity: .55; transition: opacity .2s ease .2s; }}
  @keyframes sweep {{ from {{ transform: translateX(-100%); }} to {{ transform: translateX(420%); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; scroll-behavior: auto !important; }} }}
</style>""", unsafe_allow_html=True)


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


def page_header(title: str, finding: str | None = None, kicker: str | None = None):
    """The title row: a red section label, the screen's name as the h1, and the finding in one
    sentence under it. `finding` may hold <b> for the figure that matters; the caller escapes the rest."""
    st.markdown('<div class="ph">' + (f'<div class="k">{escape(kicker)}</div>' if kicker else "")
                + f'<h1>{escape(title)}</h1>' + (f'<p>{finding}</p>' if finding else "") + '</div>',
                unsafe_allow_html=True)


def layout(fig: go.Figure, height: int = 320, title: str | None = None, **kw) -> go.Figure:
    base = dict(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK_2, size=12, family=FONT),
        margin=dict(l=14, r=16, t=48 if title else 14, b=12),
        hoverlabel=dict(bgcolor="#202026", bordercolor=CONTROL, font=dict(color=INK, family=FONT, size=13)),
        transition=dict(duration=300, easing="cubic-in-out"),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, bgcolor="rgba(0,0,0,0)",
                    traceorder="normal", font=dict(size=12, color=INK_2)),
    )
    if title:
        base["title"] = dict(text=title.upper(), x=0.02, y=0.96, xanchor="left",
                             font=dict(size=19, color=INK, family=DISPLAY, weight=700))
    base.update(kw)
    fig.update_layout(**base)
    for ax in (fig.update_xaxes, fig.update_yaxes):
        ax(gridcolor="#222228", zeroline=False, linecolor="#2E2E35", showline=False,
           tickfont=dict(color=INK_MUTED, size=12, family=FONT), title_font=dict(color=INK_MUTED, size=12))
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
    UFCSTATS, Tapology and Sherdog. Not affiliated with any promotion.</span><span>Built by Brian Phu.
    <a href="https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE">Source on GitHub</a>
    </span></div>""", unsafe_allow_html=True)
