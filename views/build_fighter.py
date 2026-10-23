"""Build your fighter: body → 3D model → stance, then tabs for fighters, roadmap, gear, classes."""
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui
from body3d import body3d

PHASE_COLORS = dict(zip([p for p, _ in core.PHASES], ui.PALETTE))


def _inputs():
    gender = st.segmented_control("Division", ["Men", "Women"], default="Men", key="bf_g") or "Men"
    h = st.slider("Height (cm)", 150, 210, 179, key="bf_h")
    w = st.slider("Weight (kg)", 45, 130, 69, key="bf_w")
    r = st.slider("Reach / arm span (cm)", 145, 225, 181, key="bf_r",
                  help="Fingertip to fingertip with your arms straight out. For most people it is close to their height.")
    c1, c2 = st.columns(2)
    hand = c1.radio("Dominant hand", ["Right", "Left"], key="bf_hand")
    foot = c2.radio("Dominant foot", ["Right", "Left"], key="bf_foot",
                    help="The foot you'd kick a ball with.")
    style = st.selectbox("Fighting style", core.STYLES, key="bf_style")
    freq = st.slider("Training sessions per week", 1, 7, 4, key="bf_freq")
    level = st.select_slider("Experience", core.LEVELS, value="Beginner", key="bf_lvl")
    goal = st.selectbox("Goal", list(core.GOALS), index=2, key="bf_goal")
    return dict(gender=gender, height_cm=h, weight_kg=w, reach_cm=r, hand=hand, foot=foot,
                style=style, sessions=freq, level=level, goal=goal)


def _body_card(p, df, stance_choice):
    bmi = p["weight_kg"] / (p["height_cm"] / 100) ** 2
    ape = p["reach_cm"] - p["height_cm"]
    div = core.division_for_weight(p["weight_kg"], p["gender"])
    peers = df[df["weight_class"] == div]
    peer_reach = peers["reach_cm"].median()
    peer_h = peers["height_cm"].median()
    ape_txt = ("long arms for your height" if ape >= 4 else "short arms for your height"
               if ape <= -4 else "arms about your height")
    st.markdown(f"""
    <div class="card">
      <div class="t">Your frame</div>
      <div class="kv">
        <div>Division<b>{escape(div)}</b></div>
        <div>BMI<b>{bmi:.1f}</b></div>
        <div>Ape index<b>{ape:+d} cm</b></div>
        <div>Stance<b>{escape(stance_choice)}</b></div>
        <div>vs {escape(div)} height<b>{p['height_cm'] - peer_h:+.0f} cm</b></div>
        <div>vs {escape(div)} reach<b>{p['reach_cm'] - peer_reach:+.0f} cm</b></div>
      </div>
      <div class="b">You have {ape_txt}. Medians are from the {len(peers)} {escape(div)} fighters
      in the dataset.</div>
    </div>""", unsafe_allow_html=True)


def _stance_card(adv, stance_choice, df, hand):
    same = df[(df["stance"] == stance_choice) & (df["hand"] == hand)]
    reasons = "".join(f"<li>{escape(x)}</li>" for x in adv["reasons"])
    tail = (f"{len(same)} fighters in the dataset fight {escape(stance_choice)} with a "
            f"{hand.lower()} dominant hand (mean win rate {same['win_rate'].mean():.0f}%)."
            if len(same) else f"No fighter in the dataset is {escape(stance_choice)} and "
                              f"{hand.lower()}-handed — a genuinely rare look.")
    st.markdown(f"""
    <div class="card" style="margin-top:10px">
      <div class="t">Suggested stance: {escape(adv['recommended'])}</div>
      <div class="s">Alternative: {escape(adv['alternative'])}{'. You are cross-dominant.' if adv['cross_dominant'] else ''}</div>
      <div class="b"><ul>{reasons}</ul><div style="margin-top:6px">{tail}</div></div>
    </div>""", unsafe_allow_html=True)


def _models(df, p, stance):
    top = core.model_fighters(df, height_cm=p["height_cm"], reach_cm=p["reach_cm"],
                              weight_kg=p["weight_kg"], stance=stance, hand=p["hand"],
                              foot=p["foot"], style=p["style"], gender=p["gender"],
                              goal=p["goal"], n=5)
    cols = st.columns(len(top))
    for c, (_, f) in zip(cols, top.iterrows()):
        learn = core.strengths(df, f["fighter"], top=3)
        note = f.get("study")
        items = ([f"<li><b>Signature:</b> {escape(note)}</li>"] if isinstance(note, str) else []) \
            + [f"<li>{escape(x)}</li>" for x in learn]
        c.markdown(f"""
        <div class="card" style="height:100%">
          <div class="score">{f['match_score']:.0f}<small> / 100 match</small></div>
          <div class="t" style="margin-top:8px">{escape(f['fighter'])}</div>
          <div class="s">{escape(f['weight_class'])}, {f['wins']}–{f['losses']}</div>
          <div style="margin-top:6px"><span class="pill">{escape(f['stance'])}</span><span class="pill">{escape(f['hand'])}-handed</span><span class="pill">{escape(f['fighting_style'])}</span></div>
          <div class="s" style="margin-top:6px">{f['height_cm']:.0f} cm tall, reach {f'{f["reach_cm"]:.0f} cm' if pd.notna(f['reach_cm']) else 'n/a'}</div>
          <div class="b"><b>What to learn</b><ul>{''.join(items)}</ul></div>
        </div>""", unsafe_allow_html=True)

    parts = [("s_body", "Body match"), ("s_stance", "Stance"), ("s_hand", "Hand"),
             ("s_style", "Style"), ("s_quality", "Proven quality"), ("s_foot", "Foot (estimated)")]
    order = top.iloc[::-1]
    fig = go.Figure()
    for i, (col, label) in enumerate(parts):
        fig.add_bar(y=order["fighter"], x=order[col], name=label, orientation="h",
                    marker=dict(color=ui.PALETTE[i], line=dict(color=ui.SURFACE, width=2)),
                    hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x:.1f}} pts<extra></extra>")
    fig.update_layout(barmode="stack", xaxis=dict(range=[0, 100], title="match points"))
    st.write("")
    ui.chart(ui.layout(fig, height=120 + 38 * len(top), title="Why these fighters",
                       margin=dict(l=10, r=14, t=74, b=10)))
    return top


def _roadmap(p, stance):
    rm = core.roadmap(style=p["style"], stance=stance, hand=p["hand"], foot=p["foot"],
                      sessions=p["sessions"], goal=p["goal"], level=p["level"])
    total = rm["end_month"].max()
    fig = go.Figure()
    for _, r in rm.iterrows():
        fig.add_bar(y=[r["phase"]], x=[r["end_month"] - r["start_month"]], base=[r["start_month"]],
                    orientation="h", name=r["phase"],
                    marker=dict(color=PHASE_COLORS[r["phase"]], line=dict(color=ui.SURFACE, width=2)),
                    text=f"{r['start_month']:.0f}–{r['end_month']:.0f} mo", textposition="inside",
                    insidetextanchor="middle", textfont=dict(color=ui.on_color(PHASE_COLORS[r["phase"]])),
                    hovertemplate=f"<b>{r['phase']}</b><br>month {r['start_month']:.1f} → "
                                  f"{r['end_month']:.1f}<extra></extra>")
    fig.update_layout(showlegend=False, xaxis=dict(title="months from today", range=[0, total * 1.02]),
                      yaxis=dict(autorange="reversed"))
    ui.chart(ui.layout(fig, height=230, title=f"≈ {total:.0f} months to “{p['goal']}” "
                                              f"at {p['sessions']} sessions a week"))
    cols = st.columns(4)
    for c, (_, r) in zip(cols, rm.iterrows()):
        focus = "".join(f"<li>{escape(x)}</li>" for x in r["focus"])
        week = "".join(f'<span class="pill">{escape(x)}</span>' for x in r["week"])
        c.markdown(f"""
        <div class="card" style="height:100%;border-top:3px solid {PHASE_COLORS[r['phase']]}">
          <div class="t">{escape(r['phase'])}</div>
          <div class="s">Months {r['start_month']:.0f}–{r['end_month']:.0f}</div>
          <div class="b"><ul>{focus}</ul></div>
          <div class="s" style="margin-top:8px">Weekly classes</div><div>{week}</div>
        </div>""", unsafe_allow_html=True)
    return rm


GEAR_DIR = Path(__file__).resolve().parents[1] / "static" / "gear"


@st.cache_data
def _gear_photos() -> dict:
    """key -> (static URL, credit line) for every photo in static/gear (see its README)."""
    credits = {}
    f = GEAR_DIR / "credits.csv"
    if f.exists():
        c = pd.read_csv(f)
        credits = {r.key: f"{r.author}, {r.license}" for r in c.itertuples()}
    out = {}
    for img in sorted(GEAR_DIR.glob("*")):
        if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            out[img.stem] = (f"app/static/gear/{img.name}", credits.get(img.stem, ""))
    return out


def _gear(p, rm):
    """Gear tab: what to buy, in what size, by when, and why, for this person's roadmap."""
    budget = st.segmented_control("Budget", list(core.BUDGETS), default="Balanced", key="bf_budget",
                                  help="Where in the usual price range to aim. Sizes don't change.") \
        or "Balanced"
    gear = core.recommend_gear(height_cm=p["height_cm"], weight_kg=p["weight_kg"], gender=p["gender"],
                               goal=p["goal"], style=p["style"], rm=rm, budget=budget)
    if gear.empty:
        st.info("Your plan needs no special kit yet.")
        return gear
    need = gear[~gear["optional"]]
    first = need[need["buy_by_month"] == 0]
    st.markdown(f'''<div class="gearsum"><div><b>A${first["price_aud"].sum():,}</b><span>before day one,
      {len(first)} items</span></div><div><b>A${need["price_aud"].sum():,}</b><span>for the whole plan,
      {len(need)} items</span></div><div class="gearnote">Sizes come from your height and weight; each item is
      listed because a class in your roadmap needs it. Prices are typical Australian ranges, not quotes.
      Try gloves and shin guards on in a shop before buying.</div></div>''', unsafe_allow_html=True)
    for label, g in gear.groupby("priority", sort=False):
        sub = ("not in the totals" if g["optional"].iloc[0]
               else f'{g["phase"].iloc[0]} phase, A${g["price_aud"].sum():,}')
        st.markdown(f'<div class="gearwhen">{escape(label)}<span>{escape(sub)}</span></div>',
                    unsafe_allow_html=True)
        photos = _gear_photos()
        cols = st.columns(4)                      # fixed width, so a group of one stays card-sized
        for i, (_, r) in enumerate(g.iterrows()):
            n = r["needed_for"]
            need = (("Anyone who trains" if r["optional"] else "Everyone, from week one") if not n else ", ".join(n[:2])
                    + (f" and {len(n) - 2} more" if len(n) > 2 else ""))
            ph = photos.get(r["key"])
            img = (f'<img class="gimg" src="{ph[0]}" alt="{escape(r["item"])}">'
                   + (f'<div class="gcred">Photo: {escape(ph[1])}</div>' if ph[1] else "")) if ph else ""
            cols[i % len(cols)].markdown(f"""
            <div class="card gear">{img}
              <div class="gtop"><span class="t">{escape(r['item'])}</span><span class="gp">A${r['price_aud']}</span></div>
              <div class="gsize">{escape(r['size'])}</div>
              <div class="b">{escape(r['why'])}</div>
              <div class="s">For: {escape(need)}</div>
            </div>""", unsafe_allow_html=True)
    return gear


GEAR_CSS = f"""<style>
  .gearsum {{ display: grid; grid-template-columns: auto auto 1fr; gap: 6px 34px; align-items: end;
              margin: 6px 0 14px; }}
  .gearsum b {{ display: block; font-family: {ui.DISPLAY}; font-weight: 800; font-size: 2.1rem; line-height: 1;
                color: {ui.INK}; font-variant-numeric: tabular-nums; }}
  .gearsum span {{ font-size: .8rem; color: {ui.INK_MUTED}; }}
  .gearnote {{ font-size: .82rem; color: {ui.INK_2}; max-width: 62ch; line-height: 1.45; }}
  .gearwhen {{ font-family: {ui.DISPLAY}; font-weight: 700; font-size: 1.25rem; color: {ui.INK};
               border-top: 1px solid {ui.BORDER}; padding-top: 10px; margin: 10px 0 6px; }}
  .gearwhen span {{ font-family: {ui.BODY}; font-weight: 500; font-size: .8rem; color: {ui.INK_MUTED};
                    margin-left: 10px; }}
  .card.gear {{ margin-bottom: 12px; }}
  .gimg {{ display: block; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 3px;
           margin-bottom: 4px; background: {ui.SURFACE_2}; }}
  .gcred {{ font-size: .68rem; color: {ui.INK_MUTED}; margin-bottom: 8px; }}
  .gtop {{ display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }}
  .gp {{ font-family: {ui.DISPLAY}; font-weight: 700; font-size: 1.15rem; color: {ui.RULE};
         font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .gsize {{ display: inline-block; margin-top: 6px; padding: 2px 8px; border-radius: 3px; font-size: .82rem;
            font-weight: 600; color: {ui.ON_ACCENT}; background: {ui.ACCENT_FILL}; }}
  @media (max-width: 900px) {{ .gearsum {{ grid-template-columns: 1fr 1fr; }} .gearnote {{ grid-column: 1 / -1; }} }}
</style>"""


def render(df: pd.DataFrame):
    ui.page_header("Build your fighter",
                   "Enter your frame and goals on the left. You get a stance, fighters to study, a "
                   "training roadmap and the gear to buy for it, all in one plan you can download.")
    with st.container(key="oct_build"):
        left, mid, right = st.columns([1.05, 2.0, 1.2], gap="medium")
    with left:
        p = _inputs()
    adv = core.recommend_stance(p["hand"], p["foot"], p["style"])
    with right:
        choice = st.selectbox("Stance to plan for",
                              ["Suggested", "Orthodox", "Southpaw", "Switch"], key="bf_stance")
        stance = adv["recommended"] if choice == "Suggested" else choice
        _body_card(p, df, stance)
        _stance_card(adv, stance, df, p["hand"])

    top = core.model_fighters(df, height_cm=p["height_cm"], reach_cm=p["reach_cm"],
                              weight_kg=p["weight_kg"], stance=stance, hand=p["hand"],
                              foot=p["foot"], style=p["style"], gender=p["gender"],
                              goal=p["goal"], n=1)
    with mid:
        show_ghost = st.toggle(f"Compare with {top.iloc[0]['fighter']}", True, key="bf_ghost")
        figs = [dict(label="You", height_cm=p["height_cm"], weight_kg=p["weight_kg"],
                     reach_cm=p["reach_cm"], stance="Orthodox" if stance == "Switch" else stance,
                     hand=p["hand"], foot=p["foot"])]
        if show_ghost:
            f = top.iloc[0]
            figs.append(dict(label=f["fighter"], height_cm=float(f["height_cm"]),
                             weight_kg=float(f["weight_kg"]),
                             reach_cm=float(f["reach_cm"] if pd.notna(f["reach_cm"]) else f["height_cm"]),
                             stance="Orthodox" if f["stance"] == "Switch" else f["stance"],
                             hand=f["hand"], foot=f["foot"], ghost=True))
        body3d(figs, height=560, key="body")

    st.markdown(GEAR_CSS, unsafe_allow_html=True)
    t_models, t_road, t_gear, t_gym = st.tabs(["Fighters to study", "Training roadmap", "Gear to buy",
                                               "Classes and coaches"])
    with t_models:
        st.markdown('<div class="secsub">Ranked on body match (height, reach, weight), stance, dominant '
                    'hand, style and proven quality. "What to learn" comes from their real UFC stats.</div>',
                    unsafe_allow_html=True)
        models = _models(df, p, stance)
    with t_road:
        st.markdown('<div class="secsub">Length scales with your goal, sessions per week and experience. '
                    'Each phase lists what to work on and the classes to take each week.</div>',
                    unsafe_allow_html=True)
        rm = _roadmap(p, stance)
        ui.section("First week", "Foundation phase, spread across the week with rest days.")
        st.dataframe(core.schedule(rm.iloc[0]["week"]), hide_index=True, width="stretch", height=290)
    with t_gear:
        gear = _gear(p, rm)
    with t_gym:
        a, b = st.columns([1.3, 1], gap="medium")
        with a:
            ui.section("Classes to join", "Sample class catalogue; swap in your gym's timetable "
                       "(data/classes_sample.csv).")
            classes = core.pick_classes(core.load_catalogue("classes"), p["style"], list(rm["week"]))
            st.dataframe(classes[["class", "discipline", "level", "focus", "starts_in"]]
                         .rename(columns=str.capitalize).rename(columns={"Starts_in": "Starts in"}),
                         hide_index=True, width="stretch", height=290)
        with b:
            ui.section("Coaches to ask for", "Fictional sample roster, matched on discipline, stance, "
                       "hand and goal. Replace data/coaches_sample.csv with your gym's coaches.")
            coaches = core.pick_coaches(core.load_catalogue("coaches"), style=p["style"], stance=stance,
                                        hand=p["hand"], goal=p["goal"])
            for _, r in coaches.iterrows():
                why = []
                if r["stance"] == stance:
                    why.append(f"also fights {stance.lower()}")
                if r["best_for"] in (p["style"], "Any"):
                    why.append(f"specialises in {p['style'].lower()}s" if r["best_for"] != "Any"
                               else "supports every style")
                st.markdown(f"""
                <div class="card" style="margin-bottom:10px">
                  <div class="t">{escape(r['coach'])}</div>
                  <div class="s">{escape(r['discipline'])}, {r['years_coaching']} years coaching, {escape(r['level'].lower())}</div>
                  <div class="b">{escape(r['specialty'])}{'<br><span style="color:' + ui.ACCENT + '">Match: ' + escape(', '.join(why)) + '</span>' if why else ''}</div>
                </div>""", unsafe_allow_html=True)

    st.write("")
    learn = {f: ([df.loc[df["fighter"] == f, "study"].iloc[0]]
                 if isinstance(df.loc[df["fighter"] == f, "study"].iloc[0], str) else [])
             + core.strengths(df, f, top=3) for f in models["fighter"]}
    plan = core.plan_markdown(p, stance, adv, models, rm, classes, coaches, learn, gear)
    st.download_button("Download my plan: stance, fighters, roadmap and gear", plan.encode(),
                       "training_plan.md", "text/markdown", type="primary")
