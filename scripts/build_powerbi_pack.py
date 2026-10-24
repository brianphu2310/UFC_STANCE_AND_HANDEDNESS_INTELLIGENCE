"""Build the Power BI pack in powerbi/: tidy CSV tables for the model and 1280x720 page backgrounds.

    python scripts/build_powerbi_pack.py

Tables (powerbi/data/):
  fighters.csv        one row per fighter: identity, stance, hand, foot, record, frame, style, flags
  skills.csv          one row per fighter and skill: raw value and percentile vs all fighters (long format)
  stance_tests.csv    the Stance lab comparisons on career win rate (gap, 95% CI, p values, Cohen's d)
  gear.csv            the gear catalogue with sizes left blank and AUD price ranges

Backgrounds (powerbi/backgrounds/*.jpg): a fight photo under an 82% dark veil, the page title set in
Big Shoulders Display and a white-framed banner area, to use as Format page > Canvas background.
"""
import sys
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ufc_core as core  # noqa: E402

OUT = ROOT / "powerbi"
W, H = 1280, 720
PAGES = [  # file, title, photo in static/hero, banner photo
    ("01_home", "WHICH SIDE DO YOU LEAD WITH?", "explorer", "build-a-fighter"),
    ("02_overview", "29% LEAD WITH THE OTHER SIDE", "data", None),
    ("03_explorer", "TWO FIGHTERS, SIDE BY SIDE", "stance-lab", "explorer"),
    ("04_stance_lab", "DOES STANCE DECIDE FIGHTS?", "explorer", "stance-lab"),
    ("05_build_a_fighter", "BUILD YOUR FIGHTER", "build-a-fighter", "build-a-fighter"),
]


def tables(df: pd.DataFrame):
    d = OUT / "data"
    d.mkdir(parents=True, exist_ok=True)
    cols = ["fighter", "gender", "country", "continent", "weight_class", "stance", "hand", "foot",
            "stance_hand", "fighting_style", "champion", "wins", "losses", "win_rate", "age",
            "height_cm", "reach_cm", "weight_kg", "ape_index_cm", "ufc_fights", "title_fights",
            "first_ufc_fight", "popularity_index"]
    f = df[cols].copy()
    f["debut_year"] = pd.to_datetime(f["first_ufc_fight"], errors="coerce").dt.year.astype("Int64")
    f.to_csv(d / "fighters.csv", index=False)

    rows = []
    for col, (label, unit, higher) in core.SKILLS.items():
        pct = df[col].rank(pct=True, ascending=higher) * 100
        for name, v, p in zip(df["fighter"], df[col], pct):
            rows.append(dict(fighter=name, skill=label, unit=unit, value=v,
                             percentile=round(p, 1) if pd.notna(p) else None))
    pd.DataFrame(rows).to_csv(d / "skills.csv", index=False)

    tests = [("Southpaw vs Orthodox", df.stance == "Southpaw", df.stance == "Orthodox"),
             ("Right-handed southpaw vs orthodox right-hander",
              (df.stance == "Southpaw") & (df.hand == "Right"), (df.stance == "Orthodox") & (df.hand == "Right")),
             ("Switch vs single stance", df.stance == "Switch", df.stance != "Switch"),
             ("Left-handed vs right-handed", df.hand == "Left", df.hand == "Right"),
             ("Left-footed vs right-footed (estimated)", df.foot == "Left", df.foot == "Right")]
    out = []
    for label, a, b in tests:
        c = core.compare_groups(df, a, b, *label.split(" vs "))
        out.append({k: getattr(c, k) for k in vars(c)} | {"comparison": label})
    pd.DataFrame(out).to_csv(d / "stance_tests.csv", index=False)

    pd.DataFrame([dict(key=k, item=g["item"], category=g["cat"], price_low_aud=g["price"][0],
                       price_high_aud=g["price"][1], optional=bool(g.get("optional")), why=g["why"])
                  for k, g in core.GEAR.items()]).to_csv(d / "gear.csv", index=False)


def _cover(img: Image.Image, w: int, h: int, fy: float = .3) -> Image.Image:
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = int((img.height - h) * fy)
    return img.crop((x, y, x + w, y + h))


def backgrounds(font_path: Path):
    d = OUT / "backgrounds"
    d.mkdir(parents=True, exist_ok=True)
    hero = ROOT / "static" / "hero"
    title_font = ImageFont.truetype(str(font_path), 54)
    for name, title, photo, banner in PAGES:
        bg = _cover(Image.open(hero / f"{photo}.webp").convert("RGB"), W, H)
        bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 10, 10)), .82)
        draw = ImageDraw.Draw(bg)
        # banner strip under the nav bar (y 68-160), photo on the right fading into dark
        if banner:
            strip = _cover(Image.open(hero / f"{banner}.webp").convert("RGB"), W - 48, 92, .25)
            mask = Image.linear_gradient("L").rotate(90).resize(strip.size)      # 0 left -> 255 right
            dark = Image.new("RGB", strip.size, (11, 11, 11))
            strip = Image.composite(strip, dark, mask.point(lambda v: min(255, max(0, (v - 40) * 1.5))))
            bg.paste(strip, (24, 68))
            draw.rectangle([24, 68, W - 25, 159], outline=(233, 233, 233), width=2)
        # title in the banner, italic by a shear
        t = Image.new("RGBA", (900, 70), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((10, 2), title, font=title_font, fill=(255, 255, 255))
        t = t.transform(t.size, Image.AFFINE, (1, .18, -6, 0, 1, 0), Image.BICUBIC)
        bg.paste(t, (40, 80), t)
        bg.save(d / f"{name}.jpg", quality=86)


if __name__ == "__main__":
    df = core.load_fighters()
    tables(df)
    font = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if font:
        backgrounds(font)
    print("wrote", OUT)
