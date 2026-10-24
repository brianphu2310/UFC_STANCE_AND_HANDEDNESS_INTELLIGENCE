"""Home: the landing page. A fight-poster hero, the tale of the tape for orthodox vs southpaw, then
the app's pages as tonight's fight card."""
import base64
import json
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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


def _intro() -> float:
    """Once per session, before the page: a southpaw and an orthodox 3D fighter trade until the
    southpaw dips under a right hand and digs a left to the liver. The orthodox folds, kneels and falls,
    K.O., the camera swings behind the winner and the scene dissolves into the real thing: Davis's
    left to Garcia's body. Then the page fades in.

    It runs in a component iframe stretched over the whole window, so its script can follow the
    video's own clock (static/hero/intro.json holds the beats) and remove itself when the clip ends.
    Returns the seconds the landing page should wait before its own entrance."""
    if st.session_state.get("intro_done"):
        return 0.0
    st.session_state["intro_done"] = True
    video, photo = _intro_video(), ui._hero_photo("intro-photo")[0]
    tf = INTRO / "intro.json"
    if not video or not tf.exists():
        return 0.0
    T = json.loads(tf.read_text())
    st.markdown("""<style>
  .st-key-introbox {{ position: relative; z-index: 1000002 !important; height: 0; overflow: visible; }}
  .st-key-introbox iframe {{ position: fixed !important; inset: 0; width: 100vw !important; height: 100vh !important;
                             height: 100dvh !important; border: 0; z-index: 1000002; background: #000; }}
  @media (prefers-reduced-motion: reduce) {{ .st-key-introbox {{ display: none; }} }}
</style>""".format(), unsafe_allow_html=True)
    page = INTRO_HTML.replace("__FONTS__", ui._font_faces()).replace("__VIDEO__", video).replace("__PHOTO__", photo) \
        .replace("__T__", json.dumps(T)).replace("__RED__", ui.ACCENT).replace("__DISPLAY__", ui.DISPLAY)
    with st.container(key="introbox"):
        components.html(page, height=0)
    return T["total"] + .3


INTRO_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
__FONTS__
  html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
  #wrap { position: fixed; inset: 0; transition: opacity .8s ease; }
  video, .photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  .photo { background: center / cover no-repeat url(__PHOTO__); opacity: 0; transform-origin: 60% 45%; }
  .cap { position: absolute; left: 0; right: 0; bottom: 9vh; text-align: center; opacity: 0; }
  .cap b { display: block; font-family: __DISPLAY__; font-style: italic; font-weight: 800; text-transform: uppercase;
           color: #fff; font-size: clamp(2rem, 5vw, 3.8rem); line-height: 1; text-shadow: 0 3px 18px #000; }
  .cap span { color: __RED__; font-family: __DISPLAY__; font-style: italic; font-weight: 800; text-transform: uppercase;
              font-size: 1.25rem; letter-spacing: .06em; text-shadow: 0 2px 10px #000; }
  .ko { position: absolute; inset: 0; display: grid; place-items: center; font-family: __DISPLAY__; font-style: italic;
        font-weight: 800; color: __RED__; font-size: clamp(6rem, 22vw, 20rem); letter-spacing: -.02em; opacity: 0;
        text-shadow: 0 8px 0 #000, 0 0 60px rgba(229,37,45,.6); }
  button { position: absolute; right: 18px; bottom: 18px; color: #fff; border: 1px solid rgba(255,255,255,.6);
           padding: 8px 16px; font: 600 13px system-ui, sans-serif; text-transform: uppercase; letter-spacing: .08em;
           background: rgba(0,0,0,.5); cursor: pointer; }
  button:focus-visible { outline: 2px solid __RED__; outline-offset: 2px; }
</style></head><body><div id="wrap">
  <video id="v" muted playsinline preload="auto">__VIDEO__</video>
  <div class="photo" id="ph"></div>
  <div class="cap" id="cap"><b>Davis vs Garcia</b><span>The southpaw's left to the liver</span></div>
  <div class="ko" id="ko">K.O.</div>
  <button id="skip" type="button">Skip intro</button>
</div><script>
const T = __T__, v = document.getElementById("v"), ph = document.getElementById("ph"),
      cap = document.getElementById("cap"), ko = document.getElementById("ko"), wrap = document.getElementById("wrap");
const clamp = x => Math.max(0, Math.min(1, x)), ease = x => x * x * (3 - 2 * x);
let done = false, held = false;
const hold = () => { if (!held) { held = true; setTimeout(finish, Math.max(0, (T.total - v.duration) * 1000)); } };
function finish() {
  if (done) return; done = true;
  wrap.style.opacity = 0;
  setTimeout(() => { try { window.frameElement.closest('[class*="st-key-introbox"]').style.display = "none"; }
                     catch (e) { document.body.style.display = "none"; } }, 850);
}
function tick() {
  if (done) return;
  const t = v.currentTime;
  // K.O. slams in as he lands, then the 3D shot from behind the winner dissolves into the photo
  const k = clamp((t - T.ko + .1) / .35), kout = ease(clamp((t - T.photo - .2) / .5));
  ko.style.opacity = k * (1 - kout); ko.style.transform = `scale(${2.4 - 1.4 * ease(k)}) skewX(${-10 * (1 - k)}deg)`;
  const inn = ease(clamp((t - T.photo) / .9));
  ph.style.opacity = inn; ph.style.transform = `scale(${1.06 - .06 * inn})`;
  cap.style.opacity = ease(clamp((t - T.photo - .6) / .5));
  requestAnimationFrame(tick);
}
document.getElementById("skip").onclick = finish;
v.addEventListener("ended", hold);     // the photo stays up past the clip, then the page
v.addEventListener("error", finish);
const go = v.play();
if (go && go.catch) go.catch(finish);          // autoplay refused: go straight to the page
requestAnimationFrame(tick);
setTimeout(finish, (T.total + 6) * 1000);       // never trap the page behind the intro
</script></body></html>"""


def render(df: pd.DataFrame):
    wait = _intro()
    delay = f"--land-delay: {wait:.1f}s; " if wait else ""
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
  @keyframes punch {{ from {{ opacity: 0; transform: translateX(-30px) skewX(-8deg); }} to {{ opacity: 1; transform: none; }} }}
  @media (max-width: 900px) {{
    .bouts {{ grid-template-columns: 1fr; }} .bout:first-child, .bout:not(:first-child) {{ grid-row: auto; grid-column: 1; }}
    .land .in {{ padding: 36px 22px 24px; }} .strip {{ grid-template-columns: repeat(2, 1fr); }}
    .strip div:first-child {{ padding-left: 20px; }} }}
</style>"""
