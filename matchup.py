"""Matchup card: the stance geometry seen from above, plus the tale of the tape. Plain HTML and SVG
(no 3D), drawn from the same figure dicts the pages already build.

Top-down view: fighter A on the left facing right, fighter B on the right facing left. Orthodox leads
with the left foot, southpaw with the right. When both lead feet sit on the same line the stance is
open (orthodox vs southpaw); on opposite lines it is closed. The dominant hand's glove is gold.
"""
from html import escape

import streamlit as st

import ui


def _lead_left(stance: str) -> bool:
    return stance != "Southpaw"          # orthodox and switch (drawn orthodox) lead with the left foot


def _fighter_svg(f: dict, x: float, facing: int, color: str, scale: float) -> str:
    """Feet, hips and gloves for one fighter seen from above. facing +1 = looks right, -1 = left.
    Screen y grows downwards; a fighter facing right has their left side at the top."""
    s = scale * f["height_cm"] / 180
    left_y = -1 if facing > 0 else 1                     # screen side (−1 top, +1 bottom) of the left hand
    lead_left = _lead_left(f["stance"])
    lead_y = left_y if lead_left else -left_y
    w, d = 30 * s, 46 * s                                # half stance width, front-to-back foot gap
    lead = (x + facing * d / 2, 150 + lead_y * w)
    rear = (x - facing * d / 2, 150 - lead_y * w)
    dom_foot_y = left_y if f.get("foot") == "Left" else -left_y
    dom_hand_y = left_y if f.get("hand") == "Left" else -left_y

    def foot(cx, cy, dominant):
        ang = 0 if facing > 0 else 180
        ring = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{17 * s:.1f}" fill="none" stroke="{ui.RULE}" '
                f'stroke-width="2" stroke-dasharray="3 3"/>') if dominant else ""
        return (ring + f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang + (20 if cy < 150 else -20) * facing})">'
                f'<ellipse rx="{13 * s:.1f}" ry="{6 * s:.1f}" fill="{color}"/>'
                f'<circle cx="{11 * s:.1f}" cy="0" r="{4.2 * s:.1f}" fill="{color}"/></g>')

    hip = (x, 150)
    # gloves: lead hand forward of the lead foot's side, rear hand at the chin
    lead_hand = (x + facing * 44 * s, 150 + lead_y * 13 * s)
    rear_hand = (x + facing * 18 * s, 150 - lead_y * 15 * s)
    gl = lambda p, y: (f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{8.5 * s:.1f}" '
                       f'fill="{ui.RULE if y == dom_hand_y else "#E9E9E9"}" stroke="#111" stroke-width="1.5"/>')
    return (f'<line x1="{lead[0]:.1f}" y1="{lead[1]:.1f}" x2="{rear[0]:.1f}" y2="{rear[1]:.1f}" '
            f'stroke="{color}" stroke-opacity=".35" stroke-width="{10 * s:.1f}" stroke-linecap="round"/>'
            + foot(*lead, lead_y == dom_foot_y) + foot(*rear, -lead_y == dom_foot_y)
            + f'<ellipse cx="{hip[0]:.1f}" cy="{hip[1]:.1f}" rx="{11 * s:.1f}" ry="{24 * s:.1f}" fill="#1b1b1d" '
              f'stroke="{color}" stroke-width="2"/>'
            + gl(lead_hand, lead_y) + gl(rear_hand, -lead_y)), lead


def _bars(figs, colors) -> str:
    rows = [("Height", "height_cm", "cm"), ("Reach", "reach_cm", "cm"), ("Weight", "weight_kg", "kg")]
    out = []
    for label, k, unit in rows:
        vals = [float(f[k]) for f in figs]
        lo, hi = min(vals) * .85, max(vals) * 1.02
        bars = "".join(
            f'<div class="mbar"><i style="width:{(v - lo) / (hi - lo) * 100:.0f}%;background:{c}"></i>'
            f'<b>{v:.0f} {unit}</b></div>' for v, c in zip(vals, colors))
        diff = f'<em>{vals[0] - vals[1]:+.0f} {unit}</em>' if len(vals) == 2 else ""
        out.append(f'<div class="mrow"><span>{label}</span><div class="mstack">{bars}</div>{diff}</div>')
    return "".join(out)


def matchup_card(figs: list[dict], title: str | None = None):
    """figs: one or two dicts with label, height_cm, weight_kg, reach_cm, stance, hand, foot."""
    figs = figs[:2]
    colors = [ui.PALETTE[0], ui.PALETTE[1]][:len(figs)]
    two = len(figs) == 2
    parts, leads = [], []
    xs = [128, 352] if two else [240]
    for f, x, face, c in zip(figs, xs, [1, -1], colors):
        svg, lead = _fighter_svg(f, x, face, c, 1.55)
        parts.append(svg)
        leads.append(lead)
    geom = ""
    if two:
        open_ = _lead_left(figs[0]["stance"]) != _lead_left(figs[1]["stance"])
        (x1, y1), (x2, y2) = leads
        geom = ("Open stance: the lead feet share a line, so the rear straight and the outside-foot "
                "battle decide it." if open_ else
                "Closed stance: lead feet on opposite lines, so the jab and the lead hook meet head on.")
        parts.insert(0, f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ui.RULE}" '
                        f'stroke-width="1.5" stroke-dasharray="6 5"/>')
    anchors = [(16, "start"), (464, "end")] if two else [(240, "middle")]
    names = "".join(
        f'<text x="{x}" y="34" text-anchor="{an}" class="mname" fill="{c}">{escape(f.get("label") or "Fighter")}</text>'
        f'<text x="{x}" y="52" text-anchor="{an}" class="msub">{escape(f["stance"])}, {escape(f["hand"]).lower()}-handed</text>'
        for f, (x, an), c in zip(figs, anchors, colors))
    mat = (f'<svg viewBox="0 0 480 270" class="msvg" role="img" aria-label="Stance from above">'
           f'<defs><pattern id="mesh" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           f'<path d="M0 0H14" stroke="#2a2a2d" stroke-width="1"/></pattern></defs>'
           f'<rect x="0" y="0" width="480" height="270" fill="#141416"/>'
           f'<rect x="0" y="0" width="480" height="270" fill="url(#mesh)" opacity=".6"/>'
           f'<circle cx="240" cy="150" r="112" fill="none" stroke="#2e2e31" stroke-width="2"/>'
           f'<line x1="240" y1="70" x2="240" y2="230" stroke="#2e2e31" stroke-width="1"/>'
           + names + "".join(parts)
           + f'<text x="12" y="258" class="msub">From above. Gold glove: dominant hand. Dashed ring: dominant foot.</text>'
           + '</svg>')
    head = f'<div class="mtitle">{escape(title)}</div>' if title else ""
    st.markdown(f"""<div class="mcard">{head}{mat}
      {f'<div class="mgeom">{escape(geom)}</div>' if geom else ""}
      <div class="mtape">{_bars(figs, colors)}</div></div>{CSS}""", unsafe_allow_html=True)


CSS = f"""<style>
  .mcard {{ background: linear-gradient(#1A1A1A, #121212 120px); border: 1px solid #2E2E30; padding: 14px 16px 12px; }}
  .mtitle {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; text-transform: uppercase;
             font-size: 1.4rem; color: #fff; margin-bottom: 8px; }}
  .msvg {{ display: block; width: 100%; max-width: 100%; height: auto; border: 1px solid #2E2E30; }}
  .msvg .mname {{ font-family: {ui.DISPLAY}; font-style: italic; font-weight: 800; font-size: 20px; text-transform: uppercase; }}
  .msvg .msub {{ font-family: {ui.BODY}; font-size: 11px; fill: {ui.INK_MUTED}; }}
  .mgeom {{ color: {ui.INK_2}; font-size: .92rem; margin: 10px 0 2px; border-left: 3px solid {ui.RULE}; padding-left: 10px; }}
  .mtape {{ margin-top: 10px; display: grid; gap: 8px; }}
  .mrow {{ display: grid; grid-template-columns: 64px 1fr 56px; gap: 10px; align-items: center; }}
  .mrow > span {{ color: {ui.INK_MUTED}; font-size: .8rem; text-transform: uppercase; letter-spacing: .06em; }}
  .mrow em {{ font-style: normal; font-family: {ui.DISPLAY}; font-weight: 800; color: #fff; text-align: right;
              font-variant-numeric: tabular-nums; }}
  .mstack {{ display: grid; gap: 3px; }}
  .mbar {{ position: relative; height: 18px; background: #1f1f21; }}
  .mbar i {{ position: absolute; inset: 0 auto 0 0; display: block; }}
  .mbar b {{ position: relative; font-size: .78rem; color: #fff; padding-left: 6px; line-height: 18px;
             font-variant-numeric: tabular-nums; text-shadow: 0 1px 2px #000; }}
</style>"""
