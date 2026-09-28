"""Rotatable 3D body model (three.js, served from components/body3d — no CDN)."""
from pathlib import Path

import streamlit.components.v1 as components

_component = components.declare_component(
    "body3d", path=str(Path(__file__).parent / "components" / "body3d"))


def body3d(figures: list[dict], height: int = 520, pose: str = "guard",
           autorotate: bool = True, key: str | None = None):
    """
    figures: dicts with height_cm, weight_kg, reach_cm, stance, hand, foot and optional
             label, ghost (bool, drawn translucent), accent (hex colour for dominant side).
    """
    return _component(figures=figures, height=height, pose=pose, autorotate=autorotate,
                      key=key, default=None)
