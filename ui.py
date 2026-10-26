"""Design system: true-black flat, colour on data.

One ground (#000) for the bar and the page, panels one lightness step above it (#111), nested
areas a step above that, and no borders or shadows on panels. Inter is the one face on every app
screen; the landing page adds Big Shoulders Display for its headline. The red corner (orthodox)
and the blue corner (southpaw) are data colours, never chrome: buttons, tabs and nav stay neutral,
and the primary action is an inverted white pill.
"""
import base64
from html import escape
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import ufc_core as core

# ---------------------------------------------------------------- tokens
BG = "#000000"          # the ground: bar, page and gutters
SURFACE = "#111111"     # panels
SURFACE_2 = "#1C1C1C"   # nested areas, inputs, hover
RAISED = "#2A2A2A"      # selected segment, a panel inside a panel
BORDER = "#1F1F1F"      # rules inside panels and tables (panels themselves have none)
CONTROL = "#444444"     # outlines on controls
INK = "#FFFFFF"
INK_2 = "#B4B4B4"       # secondary text (9.9:1 on SURFACE)
INK_MUTED = "#949494"   # meta (6.7:1 on SURFACE, 4.9:1 on RAISED)
ACCENT = "#EB3F45"      # red corner, orthodox: data marks and figures (5.0:1 on BG, 4.6:1 on SURFACE)
ACCENT_2 = "#3B82F6"    # blue corner, southpaw: data marks
ACCENT_2_TEXT = "#5B9BFF"
RULE = "#E9B44C"        # gold: the dominant side and reference lines
ACCENT_FILL = INK       # the one primary action: an inverted pill
ON_ACCENT = BG
FIELD_BORDER = CONTROL
MUTED_FILL = "#2A2A2A"  # bars outside a selection
SHADOW = "none"
NEGATIVE = "#E5566F"

FONT = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"
BODY = FONT
DISPLAY = "'Big Shoulders Display', 'Arial Narrow', sans-serif"   # the landing page headline only

# Data palette, assigned in a fixed order per dimension: red, blue, gold, then neutrals.
PALETTE = ["#EB3F45", "#3B82F6", "#E9B44C", "#9A9A9A", "#6A6A6A", "#444444"]
SEQ_BLUE = [[0, "#2A0A0E"], [0.5, "#B3121A"], [1, "#FFB3B3"]]   # black -> red -> pale red
GRAD_BAR = ["#3B82F6", "#EB3F45"]
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


FONTS = [("Inter", "400 600", "inter-latin-variable.woff2")] + \
        [("Big Shoulders Display", w, f"big-shoulders-display-latin-{w}-normal.woff2") for w in (700, 800)]


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
        "%3Cg%20clip-path%3D%22url%28%23o%29%22%3E%3Crect%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%23EB3F45%22/%3E"
        "%3Crect%20x%3D%2233.5%22%20width%3D%2230.5%22%20height%3D%2264%22%20fill%3D%22%233B82F6%22/%3E%3C/g%3E%3C/svg%3E")
COL = 1208     # the content column, px; the bar's wordmark sits on its left edge


def inject_css():
    st.markdown(f"""
<style>
{_font_faces()}
  html, body, .stApp {{ background: {BG} !important; }}
  .stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp td, .stApp th {{
    font-family: {FONT}; }}
  .stApp {{ color: {INK}; font-feature-settings: "cv11", "ss01"; }}
  p, li {{ color: {INK_2}; font-size: 14px; line-height: 1.55; }}
  h1, h2, h3, h4 {{ font-family: {FONT}; color: {INK}; letter-spacing: 0; }}
  b, strong {{ color: {INK}; font-weight: 600; }}
  .num, [data-testid="stMetricValue"], [data-testid="stSliderThumbValue"] {{ font-variant-numeric: tabular-nums; }}
  :focus-visible {{ outline: 2px solid {INK} !important; outline-offset: 2px; }}
  .sr-only {{ position: absolute !important; width: 1px; height: 1px; padding: 0; margin: -1px;
             overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }}

  /* ---------- shell: a 48px bar on the ground over one centred column ---------- */
  .block-container {{ max-width: {COL + 48}px; padding: 76px 24px 40px !important; }}
  header[data-testid="stHeader"] {{ background: {BG}; height: 48px; border-bottom: 1px solid {BORDER}; }}
  header[data-testid="stHeader"]::before {{
    content: "Stance Intelligence"; position: absolute; top: 50%; transform: translateY(-50%);
    left: max(24px, calc((100vw - {COL}px) / 2)); padding-left: 30px; line-height: 22px;
    font: 600 15px/22px {FONT}; color: {INK}; white-space: nowrap;
    background: url("{MARK}") no-repeat left center / 22px 22px; }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: calc(max(24px, calc((100vw - {COL}px) / 2)) + 196px); }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] > div {{ flex: 1 1 auto !important; min-width: 0; }}
  header[data-testid="stHeader"] nav[data-testid="stTopNav"] {{ flex: 1 1 auto !important; min-width: 0; max-width: none !important; }}
  header[data-testid="stHeader"] [data-testid="stToolbar"] > div > div:has(> [data-testid="stToolbarActions"]) {{ min-width: 0 !important; width: auto !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{ background: transparent !important; border-radius: 6px;
    padding: 6px 10px !important; margin: 0 1px !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span {{ font: 600 14px/20px {FONT}; color: #BBBBBB !important;
    white-space: nowrap; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"]:hover span,
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] span {{ color: {INK} !important; }}
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"]:hover {{ background: {SURFACE} !important; }}
  [data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"], [data-testid="stSidebarCollapseButton"],
  [data-testid="stExpandSidebarButton"], section[data-testid="stSidebar"] {{ display: none !important; }}
  @media (max-width: 640px) {{
    header[data-testid="stHeader"]::before {{ display: none; }}
    header[data-testid="stHeader"] [data-testid="stToolbar"] {{ padding-left: 8px; }}
    .block-container {{ padding: 64px 16px 32px !important; }}
  }}

  /* ---------- the title row: a noun, the finding under it ---------- */
  .ph {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; margin: 0 0 20px; }}
  .ph h1 {{ font: 600 24px/1.25 {FONT} !important; letter-spacing: -.01em; color: {INK}; margin: 0 !important; padding: 0 !important; }}
  .ph p {{ font-size: 15px; color: {INK_2}; margin: 6px 0 0; max-width: 80ch; line-height: 1.5; }}
  .ph p b {{ color: {INK}; font-weight: 600; }}

  /* ---------- sections: a 16px title, 40px of air above ---------- */
  .sec {{ font: 500 16px/1.3 {FONT}; color: {INK}; margin: 40px 0 2px; }}
  .secsub {{ color: {INK_MUTED}; font-size: 13px; margin: 0 0 12px; max-width: 80ch; line-height: 1.45; }}

  /* ---------- panels: one lightness step, no border, no shadow ---------- */
  .card {{ background: {SURFACE}; border-radius: 10px; padding: 18px 20px; }}
  .card .t {{ font: 600 16px/1.3 {FONT}; color: {INK}; }}
  .card .s {{ color: {INK_MUTED}; font-size: 13px; margin-top: 3px; line-height: 1.4; }}
  .card .b {{ color: {INK_2}; font-size: 14px; margin-top: 10px; line-height: 1.55; }}
  .card ul {{ margin: 6px 0 0; padding-left: 18px; }}
  .card li {{ margin: 2px 0; }}
  .kv {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px 16px; margin-top: 16px; }}
  .kv div {{ font-size: 12px; color: {INK_MUTED}; }}
  .kv b {{ display: block; color: {INK}; font: 400 20px/1.2 {FONT}; margin-top: 2px; font-variant-numeric: tabular-nums; }}
  .kv b small {{ font-size: 13px; color: {INK_MUTED}; }}
  .pill {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;
           background: {SURFACE_2}; color: {INK_2}; margin: 2px 4px 2px 0; white-space: nowrap; }}
  .est {{ display: inline-block; padding: 0 6px; border-radius: 4px; font-size: 11px; font-weight: 500;
          background: rgba(233,180,76,.14); color: {RULE}; margin-left: 6px; vertical-align: 2px; font-family: {FONT}; }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }}
  .score {{ font: 400 24px/1 {FONT}; color: {INK}; font-variant-numeric: tabular-nums; }}
  .score small {{ font-size: 13px; color: {INK_MUTED}; }}
  .callout {{ background: {SURFACE}; border-radius: 10px; padding: 14px 18px; color: {INK_2};
              font-size: 14px; line-height: 1.6; }}
  .callout b {{ color: {INK}; }}
  [class*="st-key-oct_"] {{ background: {SURFACE}; border-radius: 12px; padding: 14px; }}
  [class*="st-key-oct_"] .card {{ background: {SURFACE_2}; }}

  .simlist {{ background: {SURFACE}; border-radius: 10px; padding: 4px 18px; }}
  .simrow {{ display: grid; grid-template-columns: 1fr 72px 32px; gap: 12px; align-items: center;
             padding: 10px 0; border-bottom: 1px solid {BORDER}; min-height: 44px; }}
  .simrow:last-child {{ border-bottom: none; }}
  .simrow b {{ display: block; font: 500 14px/1.3 {FONT}; color: {INK}; }}
  .simrow span {{ font-size: 12px; color: {INK_MUTED}; }}
  .simbar {{ height: 3px; background: {RAISED}; border-radius: 2px; }}
  .simbar i {{ display: block; height: 3px; background: {INK_2}; border-radius: 2px; }}
  .simrow em {{ font: 400 14px/1 {FONT}; font-style: normal; color: {INK}; text-align: right; font-variant-numeric: tabular-nums; }}

  /* ---------- streamlit widgets, neutral ---------- */
  [data-testid="stMetric"] {{ background: transparent; padding: 0; }}
  [data-testid="stMetricLabel"] p {{ color: {INK_MUTED}; font-size: 12px; }}
  [data-testid="stMetricValue"] {{ font: 400 24px/1.2 {FONT}; color: {INK}; }}
  [data-testid="stMetricDelta"] {{ color: {INK_2} !important; font-size: 13px; }}
  [data-testid="stPlotlyChart"] {{ background: {SURFACE}; border-radius: 10px; padding: 6px 4px 2px; overflow: hidden; }}
  [data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}
  [data-testid="stWidgetLabel"] p, label p {{ color: {INK_2} !important; font-size: 13px !important; font-weight: 500; }}
  [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-testid="stTextInputRootElement"] {{
    background: {SURFACE} !important; border: 1px solid {CONTROL} !important; border-radius: 8px !important; min-height: 36px; }}
  [data-baseweb="select"] > div:focus-within, [data-testid="stTextInputRootElement"]:focus-within {{ border-color: {INK} !important; }}
  .stButton button, .stDownloadButton button, [data-testid="stPopover"] button {{
    border-radius: 999px !important; min-height: 36px; padding: 0 16px !important; background: {SURFACE} !important;
    border: 1px solid {CONTROL} !important; box-shadow: none !important; }}
  .stButton button p, .stDownloadButton button p, [data-testid="stPopover"] button p {{ color: {INK} !important; font-weight: 500; font-size: 14px; }}
  .stButton button[kind="primary"], .stDownloadButton button[kind="primary"] {{ background: {INK} !important; border-color: {INK} !important; }}
  .stButton button[kind="primary"] p, .stDownloadButton button[kind="primary"] p {{ color: {BG} !important; font-weight: 600; }}
  .stButton button:hover, .stDownloadButton button:hover, [data-testid="stPopover"] button:hover {{ border-color: #6A6A6A !important; }}
  .stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover {{ background: #E6E6E6 !important; }}
  [data-testid="stPopoverBody"] {{ background: {SURFACE_2} !important; border: 1px solid {CONTROL} !important; border-radius: 10px !important; }}

  /* segmented controls, pills and radios: a neutral track, the chosen option one step lighter */
  [data-testid="stButtonGroup"] {{ gap: 0 !important; }}
  [data-testid="stButtonGroup"] button {{ background: {SURFACE} !important; border: 1px solid {CONTROL} !important;
    border-radius: 0 !important; min-height: 32px; padding: 0 12px !important; box-shadow: none !important; }}
  [data-testid="stButtonGroup"] button:first-child {{ border-radius: 8px 0 0 8px !important; }}
  [data-testid="stButtonGroup"] button:last-child {{ border-radius: 0 8px 8px 0 !important; }}
  [data-testid="stButtonGroup"] button p {{ color: {INK_2} !important; font-weight: 500; font-size: 13px; }}
  [data-testid="stBaseButton-segmented_controlActive"], [data-testid="stBaseButton-pillsActive"] {{
    background: {RAISED} !important; border-color: {CONTROL} !important; }}
  [data-testid="stBaseButton-segmented_controlActive"] p, [data-testid="stBaseButton-pillsActive"] p {{ color: {INK} !important; }}
  [data-testid="stPills"] [data-testid="stButtonGroup"] {{ gap: 6px !important; }}
  [data-testid="stPills"] [data-testid="stButtonGroup"] button {{ border-radius: 999px !important; }}
  [data-testid="stRadioGroup"] {{ display: inline-flex !important; flex-direction: row !important; flex-wrap: nowrap !important;
    gap: 0 !important; width: auto !important; border: 1px solid {CONTROL}; border-radius: 8px; overflow: hidden; }}
  [data-testid="stRadioGroup"] > div {{ margin: 0 !important; width: auto !important; flex: 0 0 auto !important; }}
  [data-testid="stRadioGroup"] > div + div {{ border-left: 1px solid {CONTROL}; }}
  [data-testid="stRadioOption"] {{ padding: 6px 14px !important; margin: 0 !important; cursor: pointer; background: {SURFACE}; }}
  [data-testid="stRadioOption"] > div > div:first-child {{ display: none !important; }}
  [data-testid="stRadioOption"] p {{ color: {INK_2} !important; font-weight: 500; font-size: 13px; }}
  [data-testid="stRadioOption"][data-selected="true"] {{ background: {RAISED}; }}
  [data-testid="stRadioOption"][data-selected="true"] p {{ color: {INK} !important; }}
  [data-testid="stSlider"] [role="group"] > div > div:has(input[type="range"]) {{
    width: 16px !important; height: 16px !important; border-radius: 50% !important; background: {INK} !important;
    border: none !important; box-shadow: none !important; }}
  [data-testid="stSliderThumbValue"] p {{ font: 500 13px/1 {FONT} !important; color: {INK} !important; }}
  [data-testid="stSliderTickBar"] p {{ color: {INK_MUTED} !important; font-size: 12px !important; }}

  /* tabs: underline on a full-width rule, the indicator in ink */
  [data-testid="stTabs"] [role="tablist"] {{ gap: 24px; border-bottom: 1px solid {BORDER}; }}
  [data-testid="stTab"] {{ padding: 10px 0 !important; }}
  [data-testid="stTab"] p {{ font: 500 14px/1.3 {FONT} !important; color: {INK_MUTED}; }}
  [data-testid="stTab"]:hover p, [data-testid="stTab"][aria-selected="true"] p {{ color: {INK}; }}
  [data-testid="stTabs"] .react-aria-SelectionIndicator {{ background: {INK} !important; height: 2px !important; }}

  /* the screen-reader line before each chart takes no room */
  [data-testid="stElementContainer"]:has(> div > div > .sr-only), [data-testid="stElementContainer"]:has(.sr-only:only-child) {{
    margin-bottom: -1rem; height: 0; overflow: hidden; }}
  [data-testid="stCaptionContainer"] p, .stCaption p {{ font-size: 12px !important; color: {INK_MUTED} !important; }}
  .foot {{ color: {INK_MUTED}; font-size: 12px; padding: 20px 0 4px; margin-top: 48px; display: flex;
           justify-content: space-between; gap: 20px; flex-wrap: wrap; }}
  .foot a {{ color: {INK_2}; }}

  /* ---------- feedback: press, hover, a running bar; nothing performs an entrance ---------- */
  .stButton button, .stDownloadButton button, [data-testid="stButtonGroup"] button, [data-testid="stRadioOption"],
  header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {{ transition: background-color .15s ease, border-color .15s ease, transform .1s ease; }}
  .stButton button:active, .stDownloadButton button:active, [data-testid="stButtonGroup"] button:active {{ transform: scale(.97); }}
  .stApp[data-test-script-state="running"] header[data-testid="stHeader"]::after {{
    content: ""; position: absolute; left: 0; bottom: -1px; height: 2px; width: 24%; background: {INK};
    animation: sweep 1.1s cubic-bezier(.4,0,.2,1) infinite; z-index: 5; }}
  .stApp[data-test-script-state="running"] [data-stale="true"] {{ opacity: .5; transition: opacity .2s ease .2s; }}
  @keyframes sweep {{ from {{ transform: translateX(-100%); }} to {{ transform: translateX(420%); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
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


def page_header(title: str, finding: str | None = None):
    """The title row: the screen's name as the h1, and the finding in one sentence under it.
    `finding` may hold <b> for the figure that matters; everything else is escaped by the caller."""
    st.markdown(f'<div class="ph"><div><h1>{escape(title)}</h1>'
                + (f'<p>{finding}</p>' if finding else "") + '</div></div>', unsafe_allow_html=True)


def layout(fig: go.Figure, height: int = 320, title: str | None = None, **kw) -> go.Figure:
    base = dict(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK_2, size=12, family=FONT),
        margin=dict(l=14, r=16, t=48 if title else 14, b=12),
        hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=CONTROL, font=dict(color=INK, family=FONT, size=13)),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, bgcolor="rgba(0,0,0,0)",
                    traceorder="normal", font=dict(size=12, color=INK_2)),
    )
    if title:
        base["title"] = dict(text=title, x=0.02, y=0.96, xanchor="left",
                             font=dict(size=16, color=INK, family=FONT, weight=500))
    base.update(kw)
    fig.update_layout(**base)
    for ax in (fig.update_xaxes, fig.update_yaxes):
        ax(gridcolor="#2B2B2B", zeroline=False, linecolor="#2B2B2B", showline=False,
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
    UFCSTATS, Tapology and Sherdog.</span><span>Built by Brian Phu.
    <a href="https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE">Source on GitHub</a>
    </span></div>""", unsafe_allow_html=True)
