"""Build your fighter: body → 3D model → model fighters → roadmap, classes, coaches."""
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui
from body3d import body3d

PHASE_COLORS = dict(zip([p for p, _ in core.PHASES], ui.PALETTE))


def _inputs():
    st.markdown('<div class="eyebrow">Your profile</div>', unsafe_allow_html=True)
    gender = st.segmented_control("Divisions", ["Men", "Women"], default="Men", key="bf_g") or "Men"
    h = st.slider("Height (cm)", 150, 210, 179, key="bf_h")
    w = st.slider("Weight (kg)", 45, 130, 69, key="bf_w")
    r = st.slider("Reach / arm span (cm)", 145, 225, 181, key="bf_r",
                  help="Fingertip to fingertip with arms straight out. Most people ≈ their height.")
    c1, c2 = st.columns(2)
    hand = c1.radio("Dominant hand", ["Right", "Left"], key="bf_hand")
    foot = c2.radio("Dominant foot", ["Right", "Left"], key="bf_foot",
                    help="The foot you'd kick a ball with.")
    style = st.selectbox("How you want to fight", core.STYLES, key="bf_style")
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
      <div class="s">Alternative: {escape(adv['alternative'])}{' · cross-dominant' if adv['cross_dominant'] else ''}</div>
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
          <div class="s">{escape(f['weight_class'])} · {f['wins']}–{f['losses']}</div>
          <div style="margin-top:6px"><span class="pill">{escape(f['stance'])}</span><span class="pill">{escape(f['hand'])}-handed</span><span class="pill">{escape(f['fighting_style'])}</span></div>
          <div class="s" style="margin-top:6px">{f['height_cm']:.0f} cm · reach {f'{f["reach_cm"]:.0f} cm' if pd.notna(f['reach_cm']) else 'n/a'}</div>
          <div class="b"><b>What to learn</b><ul>{''.join(items)}</ul></div>
        </div>""", unsafe_allow_html=True)

    parts = [("s_body", "Body match"), ("s_stance", "Stance"), ("s_hand", "Hand"),
             ("s_style", "Style"), ("s_quality", "Proven quality"), ("s_foot", "Foot ≈")]
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
                    insidetextanchor="middle", textfont=dict(color="#fff"),
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


def render(df: pd.DataFrame):
    st.markdown('<div class="eyebrow">Build your fighter</div>'
                '<div class="title">Your body, your stance, your fighters to study, your plan</div>'
                '<div class="sub">Set your frame and goals on the left — the model, matches and '
                'roadmap update live.</div>', unsafe_allow_html=True)
    st.write("")
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

    ui.section("Fighters to model yourself on",
               "Ranked on body match (height, reach, weight), stance, dominant hand, style and "
               "proven quality. 'What to learn' comes from their real UFC stats.")
    _models(df, p, stance)

    ui.section("Your roadmap", "Length scales with your goal, sessions per week and experience.")
    rm = _roadmap(p, stance)

    a, b = st.columns([1, 1.3], gap="medium")
    with a:
        ui.section("First week", "Foundation phase — spread across the week with rest days.")
        st.dataframe(core.schedule(rm.iloc[0]["week"]), hide_index=True, width="stretch", height=290)
    with b:
        ui.section("Classes to join", "Sample class catalogue — swap in your gym's timetable "
                   "(data/classes_sample.csv).")
        classes = core.pick_classes(core.load_catalogue("classes"), p["style"], list(rm["week"]))
        st.dataframe(classes[["class", "discipline", "level", "focus", "starts_in"]]
                     .rename(columns=str.capitalize).rename(columns={"Starts_in": "Starts in"}),
                     hide_index=True, width="stretch", height=290)

    ui.section("Coaches to ask for", "Fictional sample roster — replace data/coaches_sample.csv "
               "with your gym's coaches. Matched on discipline, stance, hand and goal.")
    coaches = core.pick_coaches(core.load_catalogue("coaches"), style=p["style"], stance=stance,
                                hand=p["hand"], goal=p["goal"])
    cols = st.columns(len(coaches))
    for c, (_, r) in zip(cols, coaches.iterrows()):
        why = []
        if r["stance"] == stance:
            why.append(f"also fights {stance.lower()}")
        if r["best_for"] in (p["style"], "Any"):
            why.append(f"specialises in {p['style'].lower()}s" if r["best_for"] != "Any"
                       else "supports every style")
        c.markdown(f"""
        <div class="card" style="height:100%">
          <div class="t">{escape(r['coach'])}</div>
          <div class="s">{escape(r['discipline'])} · {r['years_coaching']} yrs · {escape(r['level'])}</div>
          <div style="margin-top:6px">{'' if r['stance'] == '—' else f'<span class="pill">{escape(r["stance"])}</span><span class="pill">{escape(r["hand"])}-handed</span>'}</div>
          <div class="b">{escape(r['specialty'])}{'<br><span style="color:' + ui.ACCENT + '">✓ ' + escape(', '.join(why)) + '</span>' if why else ''}</div>
        </div>""", unsafe_allow_html=True)
