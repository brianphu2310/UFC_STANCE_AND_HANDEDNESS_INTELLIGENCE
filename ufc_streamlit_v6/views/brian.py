"""Spar vs Brian: physical comparison + open/closed-stance game plan."""
from html import escape

import pandas as pd
import streamlit as st

import ufc_core as core
import ui
from body3d import body3d


def render(df: pd.DataFrame):
    B = core.BRIAN
    st.markdown('<div class="eyebrow">Spar vs Brian</div>'
                '<div class="title">Planning a round against a right-handed southpaw</div>'
                '<div class="sub">Coaching heuristics, not a win prediction — the data has no '
                'head-to-head outcomes to predict from.</div>', unsafe_allow_html=True)
    st.write("")
    left, mid, right = st.columns([1, 1.8, 1.3], gap="medium")
    with left:
        stance = st.segmented_control("Your stance", ["Orthodox", "Southpaw", "Switch"],
                                      default="Orthodox", key="br_st") or "Orthodox"
        hand = st.radio("Dominant hand", ["Right", "Left"], horizontal=True, key="br_hand")
        foot = st.radio("Dominant foot", ["Right", "Left"], horizontal=True, key="br_foot")
        h = st.slider("Height (cm)", 150, 210, 175, key="br_h")
        r = st.slider("Reach (cm)", 145, 225, 180, key="br_r")
        w = st.slider("Weight (kg)", 45, 130, 72, key="br_w")
    with mid:
        body3d([dict(label="You", height_cm=h, weight_kg=w, reach_cm=r,
                     stance="Orthodox" if stance == "Switch" else stance, hand=hand, foot=foot),
                dict(label="Brian", height_cm=B["height_cm"], weight_kg=B["weight_kg"],
                     reach_cm=B["reach_cm"], stance=B["stance"], hand=B["hand"], foot=B["foot"],
                     ghost=True)], height=500, key="brian_body")
    with right:
        m1, m2, m3 = st.columns(3)
        m1.metric("Height", f"{h}", f"{h - B['height_cm']:+d} cm", delta_color="off")
        m2.metric("Reach", f"{r}", f"{r - B['reach_cm']:+d} cm", delta_color="off")
        m3.metric("Weight", f"{w}", f"{w - B['weight_kg']:+d} kg", delta_color="off")
        notes = core.matchup_notes(stance, hand)
        keys = "".join(f"<li>{escape(k)}</li>" for k in notes["keys"])
        gap = r - B["reach_cm"]
        rng = ("You have the longer reach — keep it long, jab and teep, make him come to you."
               if gap >= 5 else "Brian out-reaches you — close distance behind feints and work "
               "inside his jab." if gap <= -5 else
               "Reach is roughly even — the jab battle and footwork decide range.")
        st.markdown(f"""
        <div class="card" style="margin-top:10px">
          <div class="t">{escape(notes['geometry'])}</div>
          <div class="b">{escape(notes['summary'])}<ul>{keys}</ul>
          <div style="margin-top:6px"><b>Range:</b> {escape(rng)}</div></div>
        </div>""", unsafe_allow_html=True)

    ui.section("Fighters closest to Brian's style",
               "Southpaw, right-handed, near 69 kg — study how they use the lead hand.")
    study = core.model_fighters(df, height_cm=B["height_cm"], reach_cm=B["reach_cm"],
                                weight_kg=B["weight_kg"], stance="Southpaw", hand="Right",
                                foot="Right", style="Striker", gender="Men",
                                goal="Amateur competition", n=6)
    study["What they do best"] = study["fighter"].map(lambda n: "; ".join(core.strengths(df, n, 2)))
    st.dataframe(study[["fighter", "weight_class", "stance", "wins", "losses", "What they do best"]]
                 .rename(columns={"fighter": "Fighter", "weight_class": "Division",
                                  "stance": "Stance", "wins": "W", "losses": "L"}),
                 hide_index=True, width="stretch")
