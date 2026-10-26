"""Home: the landing page. A fight-poster hero, the tale of the tape for orthodox vs southpaw, then
the app's pages as tonight's fight card."""
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import ufc_core as core
import ui


TILES = [  # (page url, photo slug, title, what you get)
    ("dashboard", "data", "Intelligence dashboard",
     "Sample sizes, stance and hand distributions, win rate by stance and the tests behind each gap."),
    ("fighters", "explorer", "Fighter directory",
     "All 117 fighters with stance, hand, division, record, frame and UFC fight-log rates."),
    ("matchup", "stance-lab", "Matchup lab",
     "Two fighters side by side: the tale of the tape, nine skill percentiles and a 3D face-off."),
    ("analysis", "spar-vs-brian", "Statistical analysis",
     "Welch and Mann-Whitney tests, bootstrap intervals, effect sizes, Holm correction and power."),
    ("build-your-fighter", "build-a-fighter", "Build a fighter",
     "Your frame and dominant side become a stance, fighters to study, a roadmap and kit."),
    ("methodology", "default", "Methodology",
     "Sources, cleaning, the 43 stance corrections, feature definitions and limitations."),
]


def _tape(df: pd.DataFrame) -> str:
    """Orthodox against southpaw, read like a tale of the tape."""
    o, s = df[df["stance"] == "Orthodox"], df[df["stance"] == "Southpaw"]
    rows = [
        ("Fighters", f"{len(o)}", f"{len(s)}"),
        ("Share of the roster", f"{len(o) / len(df):.0%}", f"{len(s) / len(df):.0%}"),
        ("Mean career win rate", f"{o['win_rate'].mean():.1f}%", f"{s['win_rate'].mean():.1f}%"),
        ("Former champions", f"{int(o['champion'].sum())}", f"{int(s['champion'].sum())}"),
        ("Median reach", f"{o['reach_cm'].median():.0f} cm", f"{s['reach_cm'].median():.0f} cm"),
        ("Median ape index", f"{o['ape_index_cm'].median():+.0f} cm", f"{s['ape_index_cm'].median():+.0f} cm"),
    ]
    body = "".join(f'<div class="tr"><b class="o">{a}</b><span>{escape(k)}</span><b class="s">{b}</b></div>'
                   for k, a, b in rows)
    return f"""<div class="tape">
      <div class="th"><em class="o">Orthodox</em><span>Tale of the tape</span><em class="s">Southpaw</em></div>
      {body}</div>"""


OCTAGON = """<svg class="octa" viewBox="0 0 400 400" aria-hidden="true" focusable="false">
  <polygon points="117,10 283,10 390,117 390,283 283,390 117,390 10,283 10,117"/>
  <polygon class="i" points="134,52 266,52 348,134 348,266 266,348 134,348 52,266 52,134"/>
  <line x1="200" y1="10" x2="200" y2="390"/><line x1="10" y1="200" x2="390" y2="200"/>
  <circle cx="200" cy="200" r="58"/></svg>"""


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
    hero, credit = ui._hero_photo("home")
    other = df["stance"].isin(["Southpaw", "Switch"])
    sp = core.compare_groups(df, df["stance"] == "Southpaw", df["stance"] == "Orthodox", "Southpaw", "Orthodox")
    sw = core.compare_groups(df, df["stance"] == "Switch", df["stance"] != "Switch", "Switch", "Single")
    fixed = int((~df["stance_matches_project"]).sum())

    st.markdown(f"""
<section class="land" style="{delay}" aria-labelledby="land-h">
  <div class="in">
    <div class="kick">Fight intelligence · {len(df)} elite fighters · {df['country'].nunique()} countries</div>
    <h1 class="h1" id="land-h">Read the fight beyond the octagon.</h1>
    <p>Explore the relationship between stance, handedness, fighter attributes, and competitive outcomes
    through data-driven analysis.</p>
    <div class="cta"><a class="go" href="dashboard" target="_self">Explore the data</a>
      <a class="alt" href="matchup" target="_self">Open the matchup lab</a></div>
  </div>
  <figure class="pic">{OCTAGON}<div class="frame" style="background-image:url({hero})" role="img"
    aria-label="{escape(credit) or 'Fight photograph'}"></div>
    <figcaption>{escape(credit)}</figcaption></figure>
</section>

<section class="q" aria-labelledby="q-h">
  <div class="qt"><div class="k">The research question</div>
    <h2 id="q-h">Does leading with the other side change who wins?</h2>
    <p>About one in five fighters stands southpaw, and some lead with their strong hand. That looks like an
    edge: opponents rarely practise against it. This project tests it on {len(df)} elite fighters, using the
    official UFCSTATS stance, full pro records and nine skills measured from UFC fight logs.</p></div>
  <div class="qn">
    <div><b>{other.mean():.0%}</b><span>fight southpaw or switch</span></div>
    <div><b>{sp.diff:+.1f}</b><span>points of win rate, southpaw against orthodox (95% CI {sp.ci_low:+.1f} to {sp.ci_high:+.1f})</span></div>
    <div><b>{ui.fmt_p(sp.welch_p)}</b><span>Welch p-value for that gap, Cohen's d {sp.d:+.2f}</span></div>
  </div>
</section>

<section class="f" aria-labelledby="f-h">
  <h2 id="f-h">What the data says</h2>
  <div class="fs">
    <article><b>No reliable stance advantage</b><p>Southpaws ({sp.n_a}) and orthodox fighters ({sp.n_b}) win at almost
      the same rate: a gap of {sp.diff:+.1f} points whose interval crosses zero. Among elite fighters, stance alone
      does not separate winners.</p></article>
    <article><b>Switch-hitters: large gap, tiny group</b><p>The {sw.n_a} switch-stance fighters are {sw.diff:+.1f} points
      ahead, but with so few the interval runs {sw.ci_low:+.1f} to {sw.ci_high:+.1f}. About {sw.power_n_per_group} per group
      would be needed to test it properly.</p></article>
    <article><b>{fixed} stances corrected</b><p>The original spreadsheet disagreed with the official UFCSTATS stance for
      {fixed} of {len(df)} fighters. Corrected, the "southpaw edge" in earlier versions of this project disappears.</p></article>
  </div>
</section>
""", unsafe_allow_html=True)

    st.markdown(_tape(df), unsafe_allow_html=True)

    tiles = "".join(f"""
<a class="tile" href="{url}" target="_self">
  <div class="tp" style="background-image:url({ui._hero_photo(slug)[0]})"></div>
  <div class="tb"><h3>{escape(title)}</h3><p>{escape(text)}</p><u>Open</u></div>
</a>""" for url, slug, title, text in TILES)
    st.markdown(f'<section class="tiles" aria-labelledby="t-h"><h2 id="t-h">Inside the platform</h2>'
                f'<div class="grid">{tiles}</div></section>'
                '<section class="next"><div><h2>Start with the dashboard</h2><p>Every chart and test there runs on the '
                'same dataset, and every filter you set carries through.</p></div>'
                '<a class="go" href="dashboard" target="_self">Explore the data</a></section>', unsafe_allow_html=True)
    st.markdown(CSS, unsafe_allow_html=True)


CSS = f"""<style>
  .land {{ position: relative; display: grid; grid-template-columns: 7fr 5fr; gap: 40px; align-items: center;
           min-height: calc(100vh - 220px); max-height: 720px; padding: 8px 0 40px; border-bottom: 1px solid {ui.BORDER}; }}
  .land .kick, .q .k {{ font: 600 12px/1.5 {ui.FONT}; letter-spacing: .14em; text-transform: uppercase; color: {ui.ACCENT}; }}
  .land .h1 {{ font: 800 clamp(56px, 6.6vw, 100px)/.9 {ui.DISPLAY} !important; text-transform: uppercase; letter-spacing: -.005em;
              color: {ui.INK} !important; margin: 18px 0 0 !important; padding: 0 !important; max-width: 11.5ch;
              animation: punch .8s cubic-bezier(.2,.7,.2,1) both; animation-delay: var(--land-delay, 0s); }}
  .land p {{ color: {ui.INK_2} !important; font-size: 18px; line-height: 1.55; max-width: 50ch; margin: 26px 0 0; }}
  .cta {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 34px; }}
  .go, .alt {{ display: inline-flex; align-items: center; height: 48px; padding: 0 24px; text-decoration: none !important;
               font: 700 18px/1 {ui.DISPLAY}; letter-spacing: .06em; text-transform: uppercase; border-radius: 2px;
               transition: background-color .15s ease, border-color .15s ease, transform .1s ease; }}
  .go {{ background: {ui.ACCENT_FILL}; color: #fff !important; border: 1px solid {ui.ACCENT_FILL}; }}
  .go::after {{ content: ""; width: 9px; height: 9px; margin-left: 12px; border-top: 2px solid #fff; border-right: 2px solid #fff;
                transform: rotate(45deg); transition: transform .2s ease; }}
  .go:hover {{ background: #DA2532; }} .go:hover::after {{ transform: translateX(3px) rotate(45deg); }}
  .alt {{ color: {ui.INK} !important; border: 1px solid {ui.CONTROL}; }} .alt:hover {{ border-color: {ui.INK_2}; }}
  .go:active, .alt:active {{ transform: scale(.98); }}
  .pic {{ position: relative; margin: 0; aspect-ratio: 1; overflow: hidden; }}
  .octa {{ position: absolute; inset: 0; width: 100%; height: 100%; fill: none; stroke: {ui.CONTROL}; stroke-width: 1; }}
  .octa .i {{ stroke: rgba(229,56,59,.55); stroke-dasharray: 1100; stroke-dashoffset: 1100;
              animation: draw 2.2s cubic-bezier(.4,0,.2,1) forwards; animation-delay: calc(var(--land-delay, 0s) + .3s); }}
  .octa line, .octa circle {{ stroke: #1F1F25; }}
  .frame {{ position: absolute; inset: 15%; background: #131316 center 30% / cover no-repeat;
            clip-path: polygon(29% 0, 71% 0, 100% 29%, 100% 71%, 71% 100%, 29% 100%, 0 71%, 0 29%);
            filter: grayscale(.25) contrast(1.05); animation: settle 1.4s cubic-bezier(.2,.7,.2,1) both;
            animation-delay: var(--land-delay, 0s); }}
  .pic figcaption {{ position: absolute; right: 0; bottom: -4px; font-size: 11px; color: {ui.INK_MUTED}; }}
  @keyframes punch {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
  @keyframes settle {{ from {{ opacity: 0; transform: scale(1.04); }} to {{ opacity: 1; transform: none; }} }}

  .q {{ display: grid; grid-template-columns: 6fr 6fr; gap: 48px; padding: 64px 0; border-bottom: 1px solid {ui.BORDER}; }}
  .q h2, .f h2, .tiles h2, .next h2 {{ font: 800 44px/0.98 {ui.DISPLAY}; text-transform: uppercase; color: {ui.INK};
          margin: 14px 0 0; padding: 0; }}
  .q p {{ font-size: 16px; color: {ui.INK_2}; margin: 18px 0 0; max-width: 56ch; }}
  .qn {{ display: grid; grid-template-rows: repeat(3, auto); align-content: center; border-left: 1px solid {ui.BORDER}; }}
  .qn div {{ display: grid; grid-template-columns: 150px 1fr; gap: 20px; align-items: baseline; padding: 18px 0 18px 32px;
             border-bottom: 1px solid {ui.BORDER}; }}
  .qn div:last-child {{ border-bottom: none; }}
  .qn b {{ font: 800 52px/1 {ui.DISPLAY}; color: {ui.INK}; font-variant-numeric: tabular-nums; }}
  .qn div:first-child b {{ color: {ui.ACCENT}; }}
  .qn span {{ font-size: 14px; color: {ui.INK_2}; line-height: 1.5; }}

  .f {{ padding: 64px 0 40px; }}
  .fs {{ display: grid; grid-template-columns: repeat(3, 1fr); margin-top: 28px; border-top: 2px solid {ui.INK}; }}
  .fs article {{ padding: 20px 28px 8px 0; }}
  .fs article + article {{ padding-left: 28px; border-left: 1px solid {ui.BORDER}; }}
  .fs b {{ display: block; font: 700 24px/1.05 {ui.DISPLAY}; text-transform: uppercase; color: {ui.INK}; }}
  .fs p {{ font-size: 14px; margin: 10px 0 0; }}

  .tape {{ background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 4px; padding: 22px 32px 10px; margin-top: 8px; }}
  .tape .th, .tape .tr {{ display: grid; grid-template-columns: 1fr 1.3fr 1fr; align-items: center; text-align: center; }}
  .tape .th {{ padding-bottom: 14px; border-bottom: 1px solid {ui.CONTROL}; }}
  .tape .th em {{ font: 800 34px/1 {ui.DISPLAY}; font-style: normal; text-transform: uppercase; }}
  .tape .th span {{ font: 600 12px/1 {ui.FONT}; letter-spacing: .14em; text-transform: uppercase; color: {ui.INK_MUTED}; }}
  .tape .tr {{ padding: 11px 0; border-bottom: 1px solid {ui.BORDER}; }}
  .tape .tr:last-child {{ border-bottom: none; }}
  .tape .tr span {{ color: {ui.INK_2}; font-size: 13px; }}
  .tape .tr b {{ font: 700 26px/1 {ui.DISPLAY}; font-variant-numeric: tabular-nums; }}
  .tape .o {{ color: {ui.STEEL}; }} .tape .s {{ color: {ui.ACCENT}; }}

  .tiles {{ padding: 64px 0 0; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 28px; }}
  .tile {{ display: flex; flex-direction: column; background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 4px;
           text-decoration: none !important; overflow: hidden; transition: border-color .2s ease, transform .2s ease; }}
  .tile:hover {{ border-color: {ui.ACCENT}; transform: translateY(-2px); }}
  .tp {{ aspect-ratio: 16 / 8; background: #1A1A1F center 30% / cover no-repeat; filter: grayscale(.6) brightness(.8);
         transition: filter .3s ease; }}
  .tile:hover .tp {{ filter: grayscale(0) brightness(.95); }}
  .tb {{ padding: 16px 20px 18px; display: flex; flex-direction: column; flex: 1; }}
  .tb h3 {{ font: 700 24px/1.05 {ui.DISPLAY}; text-transform: uppercase; color: {ui.INK}; margin: 0; padding: 0; }}
  .tb p {{ font-size: 14px; color: {ui.INK_2} !important; margin: 8px 0 14px; flex: 1; }}
  .tb u {{ text-decoration: none; font: 600 12px/1 {ui.FONT}; letter-spacing: .14em; text-transform: uppercase; color: {ui.ACCENT}; }}
  .next {{ display: flex; justify-content: space-between; align-items: center; gap: 24px; margin-top: 64px; padding: 32px;
           background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-left: 2px solid {ui.ACCENT}; border-radius: 0 4px 4px 0; }}
  .next h2 {{ font-size: 34px; margin: 0; }}
  .next p {{ margin: 8px 0 0; font-size: 14px; }}
  @media (max-width: 1000px) {{ .land {{ grid-template-columns: 1fr; min-height: 0; max-height: none; }} .pic {{ max-width: 420px; }}
    .q {{ grid-template-columns: 1fr; gap: 28px; }} .qn {{ border-left: none; border-top: 1px solid {ui.BORDER}; }}
    .qn div {{ padding-left: 0; }} .grid {{ grid-template-columns: 1fr 1fr; }} }}
  @media (max-width: 640px) {{ .land .h1 {{ font-size: 54px !important; }} .land p {{ font-size: 16px; }}
    .fs {{ grid-template-columns: 1fr; }} .fs article + article {{ padding-left: 0; border-left: none; border-top: 1px solid {ui.BORDER}; }}
    .grid {{ grid-template-columns: 1fr; }} .qn div {{ grid-template-columns: 110px 1fr; }} .qn b {{ font-size: 40px; }}
    .q h2, .f h2, .tiles h2 {{ font-size: 34px; }} .next {{ flex-direction: column; align-items: flex-start; }}
    .tape {{ padding: 16px; }} .tape .th em {{ font-size: 24px; }} .tape .tr b {{ font-size: 20px; }} }}
</style>"""
