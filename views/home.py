"""Home: the landing page. A fight-poster hero, the tale of the tape for orthodox vs southpaw, then
the app's pages as tonight's fight card."""
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import ui


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


INTRO_LEN = 7.4   # seconds, the end of the doors opening below


def _intro(df: pd.DataFrame) -> float:
    """Once per session, before the page: a fight-night opener drawn in HTML and CSS, no video.
    A red and a blue light streak meet, the orthodox and southpaw corners slide in with VS between
    them, the roster counts up, the question lands, then the two halves open like doors on the page.

    It runs in a transparent component iframe stretched over the whole window, so the landing page is
    already there behind the doors. Returns the seconds the landing title should wait."""
    if st.session_state.get("intro_done"):
        return 0.0
    st.session_state["intro_done"] = True
    o, s = (df["stance"] == "Orthodox").sum(), (df["stance"] == "Southpaw").sum()
    st.markdown("""<style>
  .st-key-introbox { position: relative; z-index: 1000002 !important; height: 0; overflow: visible; }
  .st-key-introbox iframe { position: fixed !important; inset: 0; width: 100vw !important; height: 100vh !important;
                            height: 100dvh !important; border: 0; z-index: 1000002; background: transparent; }
  @media (prefers-reduced-motion: reduce) { .st-key-introbox { display: none; } }
</style>""", unsafe_allow_html=True)
    vals = {"__FONTS__": ui._font_faces(), "__RED__": ui.ACCENT, "__REDF__": ui.ACCENT_FILL, "__BLUE__": ui.ACCENT_2,
            "__DISPLAY__": ui.DISPLAY, "__O__": str(o), "__S__": str(s), "__N__": str(len(df)),
            "__C__": str(df["country"].nunique()), "__LEN__": str(INTRO_LEN)}
    page = INTRO_HTML
    for k, v in vals.items():
        page = page.replace(k, v)
    with st.container(key="introbox"):
        components.html(page, height=0)
    return INTRO_LEN - .8


# Beats (s): 0-.7 streaks meet, .7 flash, .8 corners slide in, 1.35 VS, 2.5-3.9 the counts,
# 3.95 the question, 6.4 doors open, 7.4 gone.
INTRO_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
__FONTS__
  html, body { margin: 0; height: 100%; background: transparent; overflow: hidden; }
  * { box-sizing: border-box; }
  #wrap { position: fixed; inset: 0; font-family: __DISPLAY__; font-style: italic; font-weight: 800;
          text-transform: uppercase; color: #fff; }
  .door { position: absolute; top: 0; bottom: 0; width: 50.5%; overflow: hidden; background: #070707;
          animation: open .95s cubic-bezier(.7,0,.25,1) 6.4s forwards; }
  .door.l { left: 0; --dir: -1; }
  .door.r { right: 0; --dir: 1; }
  .door::before { content: ""; position: absolute; inset: 0; opacity: 0; animation: fadeIn .5s ease .75s forwards; }
  .door.l::before { background: radial-gradient(120% 80% at 100% 50%, rgba(200,16,46,.55), rgba(200,16,46,.08) 55%, transparent 75%); }
  .door.r::before { background: radial-gradient(120% 80% at 0% 50%, rgba(59,130,246,.5), rgba(59,130,246,.07) 55%, transparent 75%); }
  /* chain-link fence over both halves */
  .door::after { content: ""; position: absolute; inset: 0; opacity: .16;
    background: repeating-linear-gradient(45deg, transparent 0 22px, #9a9a9a 22px 23.5px),
                repeating-linear-gradient(-45deg, transparent 0 22px, #9a9a9a 22px 23.5px); }
  .door.l { border-right: 3px solid __RED__; } .door.r { border-left: 3px solid __BLUE__; }
  @keyframes open { to { transform: translateX(calc(var(--dir) * 102%)); } }
  @keyframes fadeIn { to { opacity: 1; } }
  @keyframes fadeOut { to { opacity: 0; } }

  .streak { position: absolute; top: 50%; height: 4px; width: 50%; margin-top: -2px; z-index: 3;
            animation: streak .7s cubic-bezier(.6,0,.3,1) forwards, fadeOut .25s ease .75s forwards; }
  .streak.l { left: 0; background: linear-gradient(90deg, transparent, __RED__); transform-origin: left; transform: scaleX(0);
              box-shadow: 0 0 24px __RED__; }
  .streak.r { right: 0; background: linear-gradient(270deg, transparent, __BLUE__); transform-origin: right; transform: scaleX(0);
              box-shadow: 0 0 24px __BLUE__; }
  @keyframes streak { to { transform: scaleX(1); } }
  .flash { position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 4; pointer-events: none;
           animation: flash .45s ease-out .7s; }
  @keyframes flash { 0% { opacity: .85; } 100% { opacity: 0; } }

  .corner { position: absolute; top: 50%; width: 100%; transform: translateY(-50%); padding: 0 6vw; z-index: 2; }
  .door.l .corner { text-align: right; } .door.r .corner { text-align: left; }
  .corner small { display: block; font-size: clamp(.9rem, 1.6vw, 1.3rem); letter-spacing: .14em; opacity: .85; }
  .corner b { display: block; font-size: clamp(3rem, 9.5vw, 9rem); line-height: .9; letter-spacing: -.01em; }
  .door.l .corner b { color: __RED__; text-shadow: 0 0 40px rgba(200,16,46,.55); }
  .door.r .corner b { color: __BLUE__; text-shadow: 0 0 40px rgba(59,130,246,.55); }
  .corner span { display: block; font-size: clamp(1rem, 2vw, 1.6rem); margin-top: 8px; color: #ddd; }
  .door.l .corner { opacity: 0; animation: inL .55s cubic-bezier(.2,.9,.3,1.15) .8s forwards, fadeOut .35s ease 2.25s forwards; }
  .door.r .corner { opacity: 0; animation: inR .55s cubic-bezier(.2,.9,.3,1.15) .95s forwards, fadeOut .35s ease 2.25s forwards; }
  @keyframes inL { from { opacity: 0; transform: translate(-40vw, -50%) skewX(-12deg); } to { opacity: 1; transform: translate(0, -50%); } }
  @keyframes inR { from { opacity: 0; transform: translate(40vw, -50%) skewX(-12deg); } to { opacity: 1; transform: translate(0, -50%); } }

  .mid { position: absolute; inset: 0; display: grid; place-items: center; z-index: 5; pointer-events: none;
         animation: fadeOut .3s ease 6.3s forwards; }
  .vs { grid-area: 1 / 1; font-size: clamp(3rem, 8vw, 7rem); color: #fff; opacity: 0;
        text-shadow: 0 0 0 #000, 4px 4px 0 __REDF__, -4px -4px 0 __BLUE__;
        animation: slam .45s cubic-bezier(.2,.9,.3,1.3) 1.35s forwards, fadeOut .3s ease 2.25s forwards; }
  @keyframes slam { from { opacity: 0; transform: scale(3.2) rotate(-8deg); } to { opacity: 1; transform: none; } }
  #wrap.shake { animation: shake .35s linear 1.6s; }
  @keyframes shake { 20% { transform: translate(-7px, 4px); } 40% { transform: translate(6px, -5px); }
                     60% { transform: translate(-4px, 3px); } 80% { transform: translate(3px, -2px); } }

  .count { grid-area: 1 / 1; display: flex; gap: 6vw; opacity: 0; animation: fadeIn .01s linear 2.5s forwards, fadeOut .3s ease 3.85s forwards; }
  .count div { text-align: center; opacity: 0; transform: translateY(24px); }
  .count div:nth-child(1) { animation: up .4s ease-out 2.5s forwards; }
  .count div:nth-child(2) { animation: up .4s ease-out 2.8s forwards; }
  .count div:nth-child(3) { animation: up .4s ease-out 3.1s forwards; }
  @keyframes up { to { opacity: 1; transform: none; } }
  .count b { display: block; font-size: clamp(3rem, 8vw, 7.5rem); line-height: 1; }
  .count div:nth-child(2) b { color: __RED__; } .count div:nth-child(3) b { color: __BLUE__; }
  .count span { font-size: clamp(.85rem, 1.5vw, 1.2rem); letter-spacing: .14em; color: #cfcfcf; }

  .q { grid-area: 1 / 1; text-align: center; font-size: clamp(2.6rem, 7.4vw, 7rem); line-height: .9; }
  .q i { display: inline-block; font-style: inherit; opacity: 0; }
  .q i:nth-of-type(1) { animation: word .35s cubic-bezier(.2,.9,.3,1.3) 3.95s forwards; }
  .q i:nth-of-type(2) { animation: word .35s cubic-bezier(.2,.9,.3,1.3) 4.1s forwards; }
  .q i:nth-of-type(3) { animation: word .35s cubic-bezier(.2,.9,.3,1.3) 4.35s forwards; }
  .q i:nth-of-type(4) { animation: word .35s cubic-bezier(.2,.9,.3,1.3) 4.5s forwards; }
  .q i:nth-of-type(5) { animation: word .45s cubic-bezier(.2,.9,.3,1.4) 4.7s forwards; color: __RED__;
                        text-shadow: 0 0 36px rgba(229,37,45,.6); }
  .q i:nth-of-type(6) { animation: word .35s cubic-bezier(.2,.9,.3,1.3) 4.92s forwards; }
  @keyframes word { from { opacity: 0; transform: scale(1.9) skewX(-10deg); } to { opacity: 1; transform: none; } }

  button { position: absolute; right: 18px; bottom: 18px; z-index: 6; color: #fff; border: 1px solid rgba(255,255,255,.6);
           padding: 8px 16px; font: 600 13px system-ui, sans-serif; text-transform: uppercase; letter-spacing: .08em;
           background: rgba(0,0,0,.5); cursor: pointer; animation: fadeOut .3s ease 6.3s forwards; }
  button:focus-visible { outline: 2px solid __RED__; outline-offset: 2px; }
  #wrap.gone { opacity: 0; transition: opacity .45s ease; }
</style></head><body><div id="wrap" class="shake">
  <div class="door l"><div class="corner"><small>Red corner</small><b>Orthodox</b><span>__O__ fighters</span></div></div>
  <div class="door r"><div class="corner"><small>Blue corner</small><b>Southpaw</b><span>__S__ fighters</span></div></div>
  <div class="streak l"></div><div class="streak r"></div><div class="flash"></div>
  <div class="mid">
    <div class="vs">VS</div>
    <div class="count"><div><b data-n="__N__">0</b><span>Fighters</span></div><div><b data-n="__C__">0</b><span>Countries</span></div>
      <div><b data-n="9">0</b><span>Skills each</span></div></div>
    <div class="q" role="heading" aria-level="2"><i>Which</i> <i>side</i><br><i>do</i> <i>you</i> <i>lead</i> <i>with?</i></div>
  </div>
  <button id="skip" type="button">Skip intro</button>
</div><script>
const LEN = __LEN__, wrap = document.getElementById("wrap");
let done = false;
// the counts tick up as each one rises in
document.querySelectorAll(".count b").forEach((b, i) => {
  const n = +b.dataset.n, t0 = 2500 + i * 300;
  setTimeout(() => { const s = performance.now();
    const step = now => { const k = Math.min(1, (now - s) / 650); b.textContent = Math.round(n * (1 - Math.pow(1 - k, 3)));
                          if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step); }, t0);
});
function remove() { try { window.frameElement.closest('[class*="st-key-introbox"]').style.display = "none"; }
                    catch (e) { document.body.style.display = "none"; } }
function finish(skipped) {
  if (done) return; done = true;
  if (skipped) {
    wrap.classList.add("gone");
    // the landing title was timed for the full intro, so play it now instead
    try { const h = window.parent.document.querySelector(".land .h1");
          if (h) { h.style.animation = "none"; void h.offsetWidth; h.style.animation = ""; h.style.animationDelay = ".2s"; } }
    catch (e) {}
    setTimeout(remove, 480);
  } else remove();
}
document.getElementById("skip").onclick = () => finish(true);
setTimeout(() => finish(false), LEN * 1000);
</script></body></html>"""


def render(df: pd.DataFrame):
    wait = _intro(df)
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
  @keyframes punch {{ from {{ opacity: 0; transform: translateX(-30px) skewX(-8deg); }} to {{ opacity: 1; transform: none; }} }}
  @media (max-width: 900px) {{
    .bouts {{ grid-template-columns: 1fr; }} .bout:first-child, .bout:not(:first-child) {{ grid-row: auto; grid-column: 1; }}
    .land .in {{ padding: 36px 22px 24px; }} .strip {{ grid-template-columns: repeat(2, 1fr); }}
    .strip div:first-child {{ padding-left: 20px; }} }}
</style>"""
