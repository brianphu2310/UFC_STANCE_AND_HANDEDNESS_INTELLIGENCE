"""Home: the landing page. A fight-poster hero, the tale of the tape for orthodox vs southpaw, then
the app's pages as tonight's fight card."""
import base64
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

import ui

INTRO = Path(__file__).resolve().parents[1] / "static" / "hero"   # intro.webm and intro.mp4

CARD = [  # (page url, slug for the photo, billing, title, what you get)
    ("build-your-fighter", "default", "Main event", "Build your fighter",
     "Your height, reach and dominant side give you a stance, fighters to study, a training roadmap "
     "and the gear to buy."),
    ("explorer", "explorer", "Co-main event", "Two fighters, side by side",
     "Put any two of the 117 fighters in the Octagon and compare their frames and nine UFC skills."),
    ("stance-lab", "stance-lab", "Main card", "Does stance decide fights?",
     "Test every stance, hand and foot group with intervals and corrections, not hunches."),
    ("spar-vs-brian", "spar-vs-brian", "Main card", "Spar a right-handed southpaw",
     "A game plan against Brian's open-stance setup, sized to your own reach."),
]


def _tape(df: pd.DataFrame) -> str:
    """Orthodox (red corner) against southpaw (blue corner), read like a tale of the tape."""
    o, s = df[df["stance"] == "Orthodox"], df[df["stance"] == "Southpaw"]
    rows = [
        ("Fighters", f"{len(o)}", f"{len(s)}"),
        ("Share of the roster", f"{len(o) / len(df):.0%}", f"{len(s) / len(df):.0%}"),
        ("Mean career win rate", f"{o['win_rate'].mean():.1f}%", f"{s['win_rate'].mean():.1f}%"),
        ("Champions", f"{int(o['champion'].sum())}", f"{int(s['champion'].sum())}"),
        ("Median reach", f"{o['reach_cm'].median():.0f} cm", f"{s['reach_cm'].median():.0f} cm"),
    ]
    body = "".join(f'<div class="tr"><b class="r">{a}</b><span>{escape(k)}</span><b class="b">{b}</b></div>'
                   for k, a, b in rows)
    return f"""<div class="tape">
      <div class="th"><em class="r">Orthodox</em><span>Tale of the tape</span><em class="b">Southpaw</em></div>
      {body}
      <p>{len(s)} southpaws in a roster of {len(df)} win almost exactly as often as the orthodox majority.
      The lab tests whether that gap is real.</p></div>"""


@st.cache_data
def _intro_video() -> str:
    """<source> tags for the intro clip: WebM for Chrome and Firefox, MP4 for Safari."""
    out = ""
    for ext in ("webm", "mp4"):
        f = INTRO / f"intro.{ext}"
        if f.exists():
            out += f'<source src="data:video/{ext};base64,{base64.b64encode(f.read_bytes()).decode()}" type="video/{ext}">'
    return out


def _intro():
    """Once per session: two 3D fighters trade until one is knocked out, then the Topuria vs Holloway
    photo, then the page. Pure CSS timing; 'Skip intro' or reduced motion removes it."""
    if st.session_state.get("intro_done"):
        return False
    st.session_state["intro_done"] = True
    video, photo = _intro_video(), ui._hero_photo("explorer")[0]
    if not video:
        return False
    st.markdown(f"""
<div id="skipintro" class="intro" aria-hidden="true">
  <video autoplay muted playsinline>{video}</video>
  <div class="ko">K.O.</div>
  <div class="flash"></div>
  <div class="shot"><div class="frame" style="background-image:url({photo})"></div>
    <div class="cap"><b>Topuria vs Holloway</b><span>Every fight starts with a stance</span></div></div>
  <a class="introskip" href="#skipintro">Skip intro</a>
</div>""", unsafe_allow_html=True)
    return True


def render(df: pd.DataFrame):
    delay = "--land-delay: 9.4s; " if _intro() else ""
    hero, _ = ui._hero_photo("home")
    southpaw = (df["stance"] == "Southpaw").mean()
    st.markdown(f"""
<div class="land" style="{delay}background-image:url({hero})">
  <div class="in">
    <div class="kick">UFC stance &amp; handedness intelligence</div>
    <div class="h1" role="heading" aria-level="1">Which side<br>do you <em>lead</em> with?</div>
    <p>{len(df)} elite UFC fighters from {df['country'].nunique()} countries, measured on stance, dominant
    hand and nine skills from their fight logs. Then the same lens turned on you.</p>
    <div class="cta"><a class="go" href="build-your-fighter" target="_self">Build your fighter</a>
      <a class="alt" href="overview" target="_self">See the findings</a></div>
  </div>
  <div class="strip">
    <div><b>{len(df)}</b>fighters</div><div><b>{df['country'].nunique()}</b>countries</div>
    <div><b>{southpaw:.0%}</b>southpaw</div><div><b>9</b>skills per fighter</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(_tape(df), unsafe_allow_html=True)

    cards = "".join(f"""
<a class="bout" href="{url}" target="_self">
  <div class="ph" style="background-image:url({ui._hero_photo(slug)[0]})"></div>
  <div class="bt"><i>{escape(bill)}</i><div class="h3" role="heading" aria-level="3">{escape(title)}</div><p>{escape(text)}</p><u>Enter</u></div>
</a>""" for url, slug, bill, title, text in CARD)
    st.markdown(f'<div class="cardh"><div class="h2" role="heading" aria-level="2">Tonight\'s card</div><span>Four ways into the data</span></div>'
                f'<div class="bouts">{cards}</div>', unsafe_allow_html=True)
    st.markdown(CSS, unsafe_allow_html=True)


CSS = f"""<style>
  .block-container {{ padding-top: 4.2rem !important; }}
  .land {{ position: relative; min-height: 560px; border: 4px solid #E9E9E9; overflow: hidden;
           background: #0B0B0B right 30% / cover no-repeat; display: flex; flex-direction: column;
           justify-content: flex-end; box-shadow: 0 30px 60px rgba(0,0,0,.6); }}
  .land::before {{ content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg, #0B0B0B 0%, rgba(11,11,11,.94) 32%, rgba(11,11,11,.35) 62%, rgba(11,11,11,0) 80%),
                linear-gradient(0deg, rgba(11,11,11,.95) 0%, rgba(11,11,11,0) 38%); }}
  .land .in {{ position: relative; padding: 56px 48px 30px; max-width: 760px; }}
  .land .kick {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
                 color: {ui.ACCENT}; font-size: 1.15rem; letter-spacing: .04em; }}
  .land .h1 {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
              font-size: clamp(3.4rem, 7.4vw, 6.6rem); line-height: .86; margin: 10px 0 0; padding: 0;
              color: #fff !important; letter-spacing: -.005em; animation: punch .7s cubic-bezier(.2,.9,.3,1.2) both; animation-delay: var(--land-delay, 0s); }}
  .land .h1 em {{ color: {ui.ACCENT}; font-style: italic; }}
  .land p {{ color: #D8D8D8 !important; font-size: 1.1rem; line-height: 1.5; max-width: 54ch; margin: 18px 0 0; }}
  .cta {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 26px; }}
  .cta a {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
            font-size: 1.25rem; padding: 12px 26px; text-decoration: none !important; letter-spacing: .02em; }}
  .cta .go {{ background: linear-gradient(#E0202B, #A80D1A); color: #fff !important; border: 1px solid #FF5A62; }}
  .cta .go::after {{ content: ""; display: inline-block; margin-left: 10px; border: 7px solid transparent;
                     border-left: 11px solid #fff; border-right: 0; vertical-align: 1px; }}
  .cta .alt {{ color: #fff !important; border: 2px solid #E9E9E9; }}
  .cta a:hover {{ filter: brightness(1.15); }}
  .strip {{ position: relative; display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid #2E2E30;
            background: rgba(11,11,11,.85); }}
  .strip div {{ padding: 14px 20px; color: {ui.INK_MUTED}; font-size: .85rem; text-transform: uppercase;
                letter-spacing: .06em; border-left: 1px solid #2E2E30; }}
  .strip div:first-child {{ border-left: none; padding-left: 48px; }}
  .strip b {{ display: block; font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; font-size: 2.3rem;
              color: #fff; letter-spacing: 0; line-height: 1; }}

  .tape {{ margin: 40px auto 0; max-width: 820px; background: linear-gradient(#1A1A1A, #111);
           border: 1px solid #2E2E30; padding: 22px 28px 18px; }}
  .tape .th, .tape .tr {{ display: grid; grid-template-columns: 1fr 1.4fr 1fr; align-items: center; text-align: center; }}
  .tape .th {{ padding-bottom: 12px; border-bottom: 2px solid #E9E9E9; }}
  .tape .th em {{ font-family: {ui.DISPLAY}; font-weight: 800; font-size: 2.2rem; text-transform: uppercase; }}
  .tape .th span {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
                    color: {ui.INK_MUTED}; font-size: 1.05rem; letter-spacing: .06em; }}
  .tape .tr {{ padding: 9px 0; border-bottom: 1px solid #2E2E30; }}
  .tape .tr span {{ color: {ui.INK_2}; font-size: .92rem; text-transform: uppercase; letter-spacing: .05em; }}
  .tape .tr b {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; font-size: 1.7rem;
                 font-variant-numeric: tabular-nums; }}
  .tape .r {{ color: {ui.ACCENT}; }} .tape .b {{ color: {ui.ACCENT_2_TEXT}; }}
  .tape p {{ color: {ui.INK_MUTED} !important; font-size: .92rem; text-align: center; margin: 14px 0 0; }}

  .cardh {{ display: flex; align-items: baseline; gap: 16px; margin: 48px 0 16px; border-bottom: 1px solid #2E2E30;
            padding-bottom: 10px; flex-wrap: wrap; }}
  .cardh .h2 {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
               font-size: 2.6rem !important; margin: 0; padding: 0; color: #fff !important; }}
  .cardh .h2::after {{ content: ""; display: block; width: 56px; height: 4px; background: {ui.ACCENT}; margin-top: 4px; }}
  .cardh span {{ color: {ui.INK_MUTED}; text-transform: uppercase; letter-spacing: .08em; font-size: .85rem; }}
  .bouts {{ display: grid; grid-template-columns: 1.35fr 1fr; grid-auto-flow: dense; gap: 16px; }}
  .bout {{ display: grid; grid-template-rows: 190px auto; background: linear-gradient(#1A1A1A, #111);
           border: 1px solid #2E2E30; text-decoration: none !important; color: inherit; transition: border-color .15s, transform .15s; }}
  .bout:first-child {{ grid-column: 1; grid-row: 1 / span 3; grid-template-rows: 1fr auto; }}
  .bout:not(:first-child) {{ grid-column: 2; grid-template-rows: 130px auto; }}
  .bout:first-child .ph {{ min-height: 300px; background-position: 82% center; }}
  .bout:hover {{ border-color: {ui.ACCENT}; transform: translateY(-2px); }}
  .bout .ph {{ background: #0B0B0B center 25% / cover no-repeat; border-bottom: 3px solid {ui.ACCENT_FILL}; }}
  .bout .bt {{ padding: 16px 20px 18px; display: grid; gap: 6px; }}
  .bout i {{ font-family: {ui.DISPLAY}; font-weight: 800; text-transform: uppercase; color: {ui.ACCENT}; font-size: 1rem; }}
  .bout .h3 {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase; color: #fff;
              font-size: 1.9rem !important; line-height: .95; margin: 0; padding: 0; }}
  .bout:first-child .h3 {{ font-size: 2.8rem !important; }}
  .bout p {{ color: {ui.INK_2} !important; font-size: .95rem; margin: 0; line-height: 1.45; }}
  .bout u {{ text-decoration: none; font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
             color: #fff; font-size: 1.05rem; margin-top: 4px; }}
  .bout u::after {{ content: ""; display: inline-block; margin-left: 8px; border: 6px solid transparent;
                    border-left: 9px solid {ui.ACCENT}; border-right: 0; vertical-align: 1px; }}
  /* intro: 0-4.8s the 3D fight, 4.8s K.O., 6.6s flash to the photo, 9.2s fade into the page */
  /* lift the element that holds the intro above the page that follows it */
  [data-testid="stElementContainer"]:has(.intro), .stMarkdown:has(.intro), [data-testid="stMarkdownContainer"]:has(.intro) {{
    position: relative; z-index: 1000002 !important; }}
  .intro {{ position: fixed; inset: 0; z-index: 1000002; background: #000; overflow: hidden;
            animation: introOut .7s ease 9.2s forwards; }}
  .intro video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
  .intro .ko {{ position: absolute; inset: 0; display: grid; place-items: center; font-family: {ui.DISPLAY};
                font-style: italic; font-weight: 800; color: {ui.ACCENT}; font-size: clamp(6rem, 22vw, 20rem);
                letter-spacing: -.02em; text-shadow: 0 8px 0 #000, 0 0 60px rgba(229,37,45,.6); opacity: 0;
                animation: koIn .35s cubic-bezier(.2,1.4,.4,1) 4.8s forwards, fadeAway .3s ease 6.5s forwards; }}
  .intro .flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; animation: flash .45s ease 6.5s forwards; }}
  .intro .shot {{ position: absolute; inset: 0; display: grid; place-items: center; align-content: center; gap: 18px;
                  background: #0B0B0B; opacity: 0; animation: show .01s linear 6.6s forwards; }}
  .intro .frame {{ width: min(86vw, 1100px); aspect-ratio: 738 / 414; max-width: 100%; border: 5px solid #E9E9E9;
                   background: center / cover no-repeat; box-shadow: 0 30px 80px rgba(0,0,0,.8);
                   animation: kenburns 3s ease-out 6.6s both; }}
  .intro .cap {{ text-align: center; }}
  .intro .cap b {{ display: block; font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
                   color: #fff !important; font-size: clamp(2rem, 5vw, 3.6rem); line-height: 1; }}
  .intro .cap span {{ color: {ui.ACCENT}; font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800;
                      text-transform: uppercase; font-size: 1.2rem; letter-spacing: .06em; }}
  .intro .introskip {{ position: absolute; right: max(18px, env(safe-area-inset-right, 0px)); bottom: max(18px, env(safe-area-inset-bottom, 0px));
                  color: #fff !important; border: 1px solid rgba(255,255,255,.6); padding: 8px 16px; font-size: .85rem;
                  text-transform: uppercase; letter-spacing: .08em; text-decoration: none !important; background: rgba(0,0,0,.5); }}
  .intro:target {{ display: none; }}
  @keyframes koIn {{ from {{ opacity: 0; transform: scale(2.4) skewX(-10deg); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes fadeAway {{ to {{ opacity: 0; }} }}
  @keyframes flash {{ 0% {{ opacity: 0; }} 25% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
  @keyframes show {{ to {{ opacity: 1; }} }}
  @keyframes kenburns {{ from {{ transform: scale(1.08); }} to {{ transform: scale(1); }} }}
  @keyframes introOut {{ to {{ opacity: 0; visibility: hidden; pointer-events: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ .intro {{ display: none; }} }}
  @keyframes punch {{ from {{ opacity: 0; transform: translateX(-30px) skewX(-8deg); }} to {{ opacity: 1; transform: none; }} }}
  @media (max-width: 900px) {{
    .bouts {{ grid-template-columns: 1fr; }} .bout:first-child, .bout:not(:first-child) {{ grid-row: auto; grid-column: 1; }}
    .land .in {{ padding: 36px 22px 24px; }} .strip {{ grid-template-columns: repeat(2, 1fr); }}
    .strip div:first-child {{ padding-left: 20px; }} }}
</style>"""
