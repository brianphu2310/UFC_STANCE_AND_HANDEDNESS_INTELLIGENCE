"""
Core logic for the UFC Stance & Handedness Intelligence app.

Streamlit-free so it can be unit-tested (tests/test_core.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path(__file__).parent / "data"
DATA_PATH = DATA_DIR / "ufc_fighters_enriched.csv"

# ============================================================================
# Reference data
# ============================================================================
DIVISIONS_MEN = {
    "Flyweight": 56.7, "Bantamweight": 61.2, "Featherweight": 65.8, "Lightweight": 70.3,
    "Welterweight": 77.1, "Middleweight": 83.9, "Light Heavyweight": 93.0, "Heavyweight": 120.2,
}
DIVISIONS_WOMEN = {
    "Women's Strawweight": 52.2, "Women's Flyweight": 56.7, "Women's Bantamweight": 61.2,
    "Women's Featherweight": 65.8,
}
DIVISION_LIMIT_KG = {**DIVISIONS_MEN, **DIVISIONS_WOMEN}
DIVISION_ORDER = list(DIVISIONS_WOMEN) + list(DIVISIONS_MEN)
HW_TYPICAL_KG = 110.0

# Dimensions everything on the dashboard can be grouped by, with a fixed category order.
GROUP_DIMS = {
    "Stance": ("stance", ["Orthodox", "Southpaw", "Switch"]),
    "Dominant hand": ("hand", ["Right", "Left"]),
    "Dominant foot": ("foot", ["Right", "Left"]),
    "Stance × hand": ("stance_hand", ["Orthodox · Right-handed", "Southpaw · Right-handed",
                                      "Southpaw · Left-handed", "Orthodox · Left-handed",
                                      "Switch · Right-handed", "Switch · Left-handed"]),
    "Foot × hand": ("foot_hand", ["Right foot · Right hand", "Left foot · Right hand",
                                  "Left foot · Left hand", "Right foot · Left hand"]),
}
STYLES = ["Striker", "Grappler", "All-rounder"]
STANCE_HAND_ORDER = GROUP_DIMS["Stance × hand"][1]

BRIAN = dict(name="Brian Phu", height_cm=179, reach_cm=181, weight_kg=69,
             stance="Southpaw", hand="Right", foot="Right")

STUDY_NOTES = {
    "Conor McGregor": "Left straight timing, lead-foot positioning, distance management",
    "Israel Adesanya": "Feints, calf kicks, counter-striking off the back foot",
    "Dustin Poirier": "Boxing combinations, body punching, pressure",
    "Georges St-Pierre": "Jab-to-takedown entries, fight IQ, round-winning game plans",
    "Jon Jones": "Creativity, oblique kicks, using length at range",
    "Khabib Nurmagomedov": "Cage wrestling, chain takedowns, top pressure",
    "Islam Makhachev": "Southpaw-killing kicks, clinch wrestling, back takes",
    "Anderson Silva": "Head movement, counter timing, relaxed rhythm",
    "Alex Pereira": "Left hook counter, kickboxing precision, calf kicks",
    "Sean O'Malley": "Lead-hand precision, distance control, stance switching",
    "Petr Yan": "Boxing in the pocket, pressure, late-round cardio",
    "Cory Sandhagen": "Stance switching, creative kicks, movement",
    "TJ Dillashaw": "Footwork, angle exits, switch-stance combinations",
    "Henry Cejudo": "Olympic-level wrestling entries, fight IQ",
    "Yair Rodriguez": "Kicking variety, spinning attacks, unpredictability",
    "Charles Oliveira": "Submission chains, Muay Thai clinch, relentless pace",
    "Alexander Volkanovski": "Footwork, feints, adaptable game plans, cardio",
    "Max Holloway": "Volume boxing, shot selection, durability",
    "Ilia Topuria": "Pocket boxing, body hooks, composure",
    "Robert Whittaker": "Blitz entries, in-and-out movement",
    "Kamaru Usman": "Jab, cage pressure, wrestling control",
    "Leon Edwards": "Southpaw kicking, clinch elbows, patience",
    "Valentina Shevchenko": "Counter-striking, clinch trips, precision",
    "Zhang Weili": "Power combinations, pressure, clinch knees",
    "Amanda Nunes": "Power right hand, top control",
    "Lyoto Machida": "Karate distance, blitz counters, southpaw straight left",
    "Nate Diaz": "Southpaw volume boxing, cardio, jiu-jitsu",
    "Nick Diaz": "Southpaw volume boxing, pressure, jiu-jitsu",
    "BJ Penn": "Boxing, flexible guard, takedown defence",
    "Francis Ngannou": "Power punching, counter uppercut",
    "Tom Aspinall": "Hand speed for a heavyweight, fast finishes",
    "Merab Dvalishvili": "Chain wrestling, pace, cardio",
    "Robbie Lawler": "Power boxing, toughness, late-round finishes",
    "Demian Maia": "Takedown-to-back-take system, positional jiu-jitsu",
    "Daniel Cormier": "Olympic wrestling, dirty boxing in the clinch",
    "Cain Velasquez": "Relentless pace, wrestling-to-ground-and-pound",
}

# Readable labels for data-driven strengths: column -> (label, unit, higher_is_better)
SKILLS = {
    "slpm": ("Striking volume", "sig. strikes / min", True),
    "str_acc": ("Striking accuracy", "% landed", True),
    "str_def": ("Striking defence", "% avoided", True),
    "kd_avg": ("Knockdown power", "knockdowns / 15 min", True),
    "td_avg": ("Takedowns", "per 15 min", True),
    "td_def": ("Takedown defence", "% stuffed", True),
    "sub_avg": ("Submission threat", "attempts / 15 min", True),
    "ctrl_pct": ("Top control", "% of fight time", True),
    "sapm": ("Damage avoidance", "sig. strikes absorbed / min", False),
}


# ============================================================================
# Data
# ============================================================================
def load_fighters(path: Path | str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"fighter", "country", "stance", "hand", "foot", "win_rate", "weight_class",
                "gender", "stance_hand", "foot_hand", "fighting_style", "height_cm"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    df["weight_kg"] = df["weight_class"].map(DIVISION_LIMIT_KG).where(
        df["weight_class"] != "Heavyweight", HW_TYPICAL_KG)
    df["study"] = df["fighter"].map(STUDY_NOTES)
    return df


def load_catalogue(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}_sample.csv")


def division_for_weight(weight_kg: float, gender: str = "Men") -> str:
    table = DIVISIONS_WOMEN if gender == "Women" else DIVISIONS_MEN
    for name, limit in table.items():
        if weight_kg <= limit:
            return name
    return list(table)[-1]


def present_order(df: pd.DataFrame, dim_label: str) -> tuple[str, list[str]]:
    col, order = GROUP_DIMS[dim_label]
    seen = set(df[col].dropna())
    return col, [c for c in order if c in seen]


# ============================================================================
# Statistics
# ============================================================================
def cohens_d(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0


def bootstrap_diff_ci(a, b, n_boot: int = 5000, seed: int = 7, level: float = 0.95):
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    diffs = rng.choice(a, (n_boot, len(a))).mean(1) - rng.choice(b, (n_boot, len(b))).mean(1)
    lo, hi = np.percentile(diffs, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return float(lo), float(hi)


def bootstrap_mean_ci(a, n_boot: int = 4000, seed: int = 7, level: float = 0.95):
    rng = np.random.default_rng(seed)
    a = np.asarray(a, float)
    means = rng.choice(a, (n_boot, len(a))).mean(1)
    lo, hi = np.percentile(means, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return float(lo), float(hi)


def effect_label(d: float) -> str:
    d = abs(d)
    return "negligible" if d < 0.2 else "small" if d < 0.5 else "medium" if d < 0.8 else "large"


def required_n_per_group(d: float, alpha: float = 0.05, power: float = 0.8) -> int:
    d = abs(d)
    if d < 1e-6:
        return 10**6
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return int(np.ceil(2 * (z / d) ** 2))


@dataclass
class Comparison:
    label_a: str
    label_b: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    diff: float
    ci_low: float
    ci_high: float
    welch_t: float
    welch_p: float
    mwu_p: float
    d: float
    power_n_per_group: int

    @property
    def significant(self) -> bool:
        return self.welch_p < 0.05


def compare_groups(df, mask_a, mask_b, label_a, label_b, metric="win_rate") -> Comparison:
    a = df.loc[mask_a, metric].dropna().to_numpy(float)
    b = df.loc[mask_b, metric].dropna().to_numpy(float)
    if len(a) < 2 or len(b) < 2:
        raise ValueError("Each group needs at least 2 fighters")
    t, p = stats.ttest_ind(a, b, equal_var=False)
    mwu_p = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
    d = cohens_d(a, b)
    lo, hi = bootstrap_diff_ci(a, b)
    return Comparison(label_a, label_b, len(a), len(b), a.mean(), b.mean(), a.mean() - b.mean(),
                      lo, hi, float(t), float(p), float(mwu_p), d, required_n_per_group(d))


def holm_adjust(pvalues: list[float]) -> list[float]:
    """Holm–Bonferroni step-down adjusted p-values (controls family-wise error)."""
    p = np.asarray(pvalues, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[idx]))
        adj[idx] = running
    return adj.tolist()


def group_summary(df: pd.DataFrame, col: str, order: list[str], metric="win_rate") -> pd.DataFrame:
    g = df.groupby(col)[metric]
    out = pd.DataFrame({"fighters": g.size(), "share_pct": g.size() / len(df) * 100,
                        "mean": g.mean(), "median": g.median(), "sd": g.std()})
    return out.reindex([o for o in order if o in out.index])


def anova(df: pd.DataFrame, col: str, metric="win_rate"):
    groups = [g[metric].dropna().to_numpy() for _, g in df.groupby(col)
              if g[metric].notna().sum() >= 2]
    if len(groups) < 2:
        raise ValueError("Need two groups")
    f, p = stats.f_oneway(*groups)
    _, kp = stats.kruskal(*groups)
    return dict(f=float(f), p=float(p), kruskal_p=float(kp))


# ============================================================================
# Fighter strengths (data-driven, from real UFC stats)
# ============================================================================
def skill_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for col, (_, _, higher) in SKILLS.items():
        r = df[col].rank(pct=True)
        out[col] = r if higher else 1 - r + 1 / len(df)
    return (out * 100).round(0)


def strengths(df: pd.DataFrame, fighter: str, top: int = 3) -> list[str]:
    pct = skill_percentiles(df)
    i = df.index[df["fighter"] == fighter][0]
    row = pct.loc[i].dropna().sort_values(ascending=False).head(top)
    lines = []
    for col, p in row.items():
        label, unit, _ = SKILLS[col]
        val = df.at[i, col]
        lines.append(f"{label}: {val:.1f} {unit} (top {max(100 - int(p), 1)}%)")
    return lines


def similar_fighters(df: pd.DataFrame, fighter: str, n: int = 5) -> pd.DataFrame:
    """Nearest fighters on UFC skill percentiles + frame (height, reach). Returns distance 0–1."""
    pct = skill_percentiles(df) / 100
    frame = df[["height_cm", "reach_cm"]].apply(lambda c: (c - c.mean()) / c.std()) / 3
    feats = pd.concat([pct, frame], axis=1)
    feats = feats.fillna(feats.mean())
    i = df.index[df["fighter"] == fighter][0]
    dist = np.sqrt(((feats - feats.loc[i]) ** 2).mean(axis=1))
    out = df.assign(distance=dist).drop(index=i).nsmallest(n, "distance")
    out["similarity"] = (100 * (1 - out["distance"] / dist.max())).round(0)
    return out


def head_to_head(df: pd.DataFrame, a: str, b: str) -> dict:
    """Skill-by-skill edges between two fighters (percentiles vs the whole dataset)."""
    pct = skill_percentiles(df)
    ia = df.index[df["fighter"] == a][0]
    ib = df.index[df["fighter"] == b][0]
    rows = []
    for col, (label, _, _) in SKILLS.items():
        pa, pb = pct.at[ia, col], pct.at[ib, col]
        rows.append(dict(skill=label, a=pa, b=pb,
                         edge=a if pa > pb + 5 else b if pb > pa + 5 else "Even"))
    tab = pd.DataFrame(rows)
    ra, rb = df.at[ia, "stance"], df.at[ib, "stance"]
    geometry = ("Closed stance" if ra == rb and "Switch" not in (ra, rb)
                else "Mixed — switch-hitter can choose" if "Switch" in (ra, rb) else "Open stance")
    return dict(table=tab, wins_a=int((tab["edge"] == a).sum()), wins_b=int((tab["edge"] == b).sum()),
                reach_gap=float(df.at[ia, "reach_cm"] - df.at[ib, "reach_cm"])
                if pd.notna(df.at[ia, "reach_cm"]) and pd.notna(df.at[ib, "reach_cm"]) else None,
                height_gap=float(df.at[ia, "height_cm"] - df.at[ib, "height_cm"]),
                geometry=geometry)


def plan_markdown(profile: dict, stance: str, advice: dict, models: pd.DataFrame,
                  rm: pd.DataFrame, classes: pd.DataFrame, coaches: pd.DataFrame,
                  learn: dict[str, list[str]], gear: pd.DataFrame | None = None) -> str:
    """A shareable training plan as Markdown."""
    L = [f"# Training plan — {profile['goal']}", "",
         f"- Frame: {profile['height_cm']} cm, {profile['weight_kg']} kg, reach {profile['reach_cm']} cm",
         f"- Dominant hand / foot: {profile['hand']} / {profile['foot']}",
         f"- Style: {profile['style']} · {profile['sessions']} sessions a week · {profile['level']}",
         f"- Stance: **{stance}** (suggested {advice['recommended']}, alternative {advice['alternative']})",
         "", "## Why this stance"] + [f"- {r}" for r in advice["reasons"]]
    L += ["", "## Fighters to study"]
    for _, f in models.iterrows():
        L.append(f"### {f['fighter']} — {f['match_score']:.0f}/100 match")
        L.append(f"{f['weight_class']} · {f['stance']} · {f['hand']}-handed · {f['wins']}-{f['losses']}")
        L += [f"- {x}" for x in learn.get(f["fighter"], [])]
    L += ["", f"## Roadmap (≈ {rm['end_month'].max():.0f} months)"]
    for _, r in rm.iterrows():
        L.append(f"### {r['phase']} — months {r['start_month']:.0f}–{r['end_month']:.0f}")
        L += [f"- {x}" for x in r["focus"]]
        L.append(f"- Weekly classes: {', '.join(r['week'])}")
    L += ["", "## Classes"] + [f"- {r['class']} ({r['discipline']}, {r['level']}) — {r['focus']}"
                              for _, r in classes.iterrows()]
    if gear is not None and len(gear):
        need = gear[~gear["optional"]]
        L += ["", f"## Gear (≈ A${need['price_aud'].sum():,} in total, typical prices)"]
        for _, g in gear.groupby("priority", sort=False):
            L.append(f"### {g['priority'].iloc[0]}")
            L += [f"- {r['item']} — {r['size']} (≈ A${r['price_aud']}). {r['why']}" for _, r in g.iterrows()]
    L += ["", "## Coaches (sample roster)"] + [f"- {r['coach']} — {r['discipline']}, {r['specialty']}"
                                               for _, r in coaches.iterrows()]
    L += ["", "_Generated by UFC Stance & Handedness Intelligence. Fighter stats: UFCSTATS._"]
    return "\n".join(L)


# ============================================================================
# Build-your-fighter: stance advice, model fighters, roadmap, classes, coaches
# ============================================================================
def recommend_stance(hand: str, foot: str, style: str) -> dict:
    other = {"Right": "Left", "Left": "Right"}
    back_hand_stance = "Orthodox" if hand == "Right" else "Southpaw"  # power hand at the back
    power_forward = "Southpaw" if hand == "Right" else "Orthodox"     # power hand in front
    if hand == foot:
        rec, alt = back_hand_stance, power_forward
        reasons = [
            f"Your {hand.lower()} hand and {foot.lower()} foot are both at the back in {rec}: "
            "power rear straight and a strong rear round kick.",
            f"{alt} ('power side forward', Brian's setup) trades rear power for a faster, "
            "heavier jab and lead hook — worth drilling as a second look.",
        ]
    else:
        foot_back_stance = "Orthodox" if foot == "Right" else "Southpaw"
        if style == "Grappler":
            rec = "Orthodox" if foot == "Left" else "Southpaw"  # dominant leg leads the shot
            reasons = [f"You're cross-dominant. {rec} puts your dominant {foot.lower()} leg "
                       "in front, where it drives the penetration step for takedowns."]
        elif style == "Striker":
            rec = back_hand_stance
            reasons = [f"You're cross-dominant. {rec} keeps your dominant {hand.lower()} hand "
                       f"at the back for power; your {foot.lower()} leg leads — use it for teeps, "
                       "switch kicks and lead-leg calf kicks."]
        else:
            rec = foot_back_stance
            reasons = [f"You're cross-dominant. {rec} puts your dominant {foot.lower()} leg "
                       "at the back for kick power while your dominant hand leads the jab."]
        alt = "Southpaw" if rec == "Orthodox" else "Orthodox"
        reasons.append("Cross-dominant fighters often switch stance comfortably — "
                       "add switch-stance drills once the basics are solid.")
    return dict(recommended=rec, alternative=alt, reasons=reasons,
                cross_dominant=hand != foot, other_hand=other[hand])


GOALS = {  # goal -> (base months at 4 sessions/week, competitive?)
    "Fitness & self-defence": (6, False),
    "Interclub / smoker bout": (9, True),
    "Amateur competition": (15, True),
    "Pro debut": (30, True),
    "Pro career (UFC path)": (60, True),
}
LEVELS = ["Beginner", "Some experience", "Experienced"]


def model_fighters(df: pd.DataFrame, *, height_cm: float, reach_cm: float, weight_kg: float,
                   stance: str, hand: str, foot: str, style: str, gender: str, goal: str,
                   n: int = 5) -> pd.DataFrame:
    """Rank fighters as study models. Returns top n with score components (sum = score)."""
    pool = df[(df["gender"] == gender) & df["height_cm"].notna()].copy()
    reach_f = pool["reach_cm"].fillna(pool["height_cm"])
    body_gap = np.sqrt(((pool["height_cm"] - height_cm) / 6) ** 2
                       + ((reach_f - reach_cm) / 7) ** 2
                       + ((pool["weight_kg"] - weight_kg) / 9) ** 2)
    pro_goal = goal in ("Pro debut", "Pro career (UFC path)")
    w = dict(body=30, stance=22, hand=13, foot=5, style=20, quality=10)
    stance_score = np.where(pool["stance"] == stance, 1.0,
                            np.where((pool["stance"] == "Switch") | (stance == "Switch"), 0.5, 0.0))
    quality = (0.5 * pool["win_rate"].rank(pct=True) + 0.5 * pool["popularity_index"] / 100)
    if pro_goal:
        quality = 0.6 * quality + 0.4 * pool["champion"].astype(float)
    pool["s_body"] = np.exp(-body_gap / 1.5) * w["body"]
    pool["s_stance"] = stance_score * w["stance"]
    pool["s_hand"] = (pool["hand"] == hand) * w["hand"]
    pool["s_foot"] = (pool["foot"] == foot) * w["foot"]
    pool["s_style"] = np.where(pool["fighting_style"] == style, 1.0,
                               np.where(pool["fighting_style"] == "All-rounder", 0.5, 0.0)) * w["style"]
    pool["s_quality"] = quality * w["quality"]
    parts = ["s_body", "s_stance", "s_hand", "s_foot", "s_style", "s_quality"]
    pool["match_score"] = pool[parts].sum(axis=1)
    return pool.sort_values("match_score", ascending=False).head(n).reset_index(drop=True)


DISCIPLINES = {
    "Striker": ["Boxing", "Muay Thai", "Kickboxing"],
    "Grappler": ["BJJ", "Wrestling", "No-Gi"],
    "All-rounder": ["MMA", "Boxing", "Muay Thai", "Wrestling", "BJJ", "No-Gi", "Kickboxing"],
}


def weekly_mix(style: str, sessions: int, phase: int, goal: str, stance: str) -> list[str]:
    """Class names for one training week. phase: 0 foundation … 3 competition."""
    competitive = GOALS[goal][1]
    core = {
        "Striker": ["Boxing Fundamentals", "Muay Thai Technique", "Kickboxing Conditioning"],
        "Grappler": ["BJJ Fundamentals (Gi)", "Wrestling for MMA", "No-Gi Grappling"],
        "All-rounder": ["Boxing Fundamentals", "Wrestling for MMA", "Muay Thai Technique",
                        "BJJ Fundamentals (Gi)", "MMA Integration"],
    }[style][:]
    if phase >= 1 and stance == "Southpaw" and style != "Grappler":
        core.insert(1, "Southpaw & Open-Stance Lab")
    if phase >= 1 and style == "Grappler":
        core.append("MMA Integration")
    extras = []
    if phase >= 1:
        extras.append("Controlled Sparring")
    if sessions >= 4:
        extras.append("Strength & Conditioning")
    if phase >= 3 and competitive:
        extras.insert(0, "Competition Team")
    if sessions >= 6:
        extras.append("Mobility & Recovery")
    week: list[str] = []
    n_extra = min(len(extras), max(sessions - 2, 0))
    n_core = sessions - n_extra
    for i in range(n_core):
        week.append(core[i % len(core)])
    week.extend(extras[:n_extra])
    return week[:sessions]


PHASES = [
    ("Foundation", 0.25),
    ("Development", 0.35),
    ("Specialisation", 0.25),
    ("Competition-ready", 0.15),
]


def roadmap(*, style: str, stance: str, hand: str, foot: str, sessions: int, goal: str,
            level: str) -> pd.DataFrame:
    base, competitive = GOALS[goal]
    months = base * float(np.clip(4 / max(sessions, 1), 0.6, 2.5))
    months *= {"Beginner": 1.0, "Some experience": 0.75, "Experienced": 0.5}[level]
    months = max(round(months), 3)
    lead_hand = "left" if stance == "Orthodox" else "right"
    focus = {
        "Foundation": [
            f"{stance} stance, guard and footwork — {lead_hand} side leads",
            {"Striker": "Jab–cross, round kick, teep, basic defence",
             "Grappler": "Stance, level change, sprawl, guard retention",
             "All-rounder": "Jab–cross, round kick, sprawl, escapes from bottom"}[style],
            "Conditioning base: 3 × 3-min rounds without gassing",
        ],
        "Development": [
            {"Striker": "Combinations off the jab, checking kicks, counters",
             "Grappler": "Single & double leg chains, passing, top control",
             "All-rounder": "Strike-to-takedown entries, get-ups, clinch"}[style],
            "Open-stance vs closed-stance game plans (lead-foot battle)",
            "Controlled sparring 1× per week",
        ],
        "Specialisation": [
            f"Build your A-game around the dominant {hand.lower()} hand and {foot.lower()} foot",
            "Study your model fighters' tape: 2 rounds per week of mimic drilling",
            "Switch-stance drills" if hand != foot else "Southpaw looks to surprise orthodox partners"
            if stance == "Orthodox" else "Orthodox looks to surprise southpaw partners",
        ],
        "Competition-ready": [
            "Fight-pace rounds and weight management" if competitive
            else "Test yourself: technical sparring with new partners",
            "Game plans vs orthodox and vs southpaw opponents",
            "Recovery, mobility and injury prevention",
        ],
    }
    rows, start = [], 0.0
    for i, (name, frac) in enumerate(PHASES):
        dur = months * frac
        rows.append(dict(phase=name, start_month=round(start, 1), end_month=round(start + dur, 1),
                         focus=focus[name],
                         week=weekly_mix(style, sessions, i, goal, stance)))
        start += dur
    return pd.DataFrame(rows)


def schedule(week: list[str]) -> pd.DataFrame:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    n = len(week)
    slots = np.linspace(0, 6, n).round().astype(int) if n < 7 else list(range(7))
    grid = {d: "Rest" for d in days}
    for cls, d in zip(week, slots):
        grid[days[int(d)]] = cls if grid[days[int(d)]] == "Rest" else grid[days[int(d)]] + " + " + cls
    return pd.DataFrame({"Day": days, "Session": [grid[d] for d in days]})


def pick_classes(classes: pd.DataFrame, style: str, weeks: list[list[str]]) -> pd.DataFrame:
    cat_order = {c: i for i, c in enumerate(classes["class"])}
    first = {c: next(i for i, w in enumerate(weeks) if c in w) for w in weeks for c in w}
    used = sorted(first, key=lambda c: (first[c], cat_order.get(c, 99)))
    out = classes.set_index("class").loc[[c for c in used if c in cat_order]].reset_index()
    out["starts_in"] = out["class"].map(lambda c: PHASES[first[c]][0])
    return out


def pick_coaches(coaches: pd.DataFrame, *, style: str, stance: str, hand: str, goal: str,
                 n: int = 3) -> pd.DataFrame:
    c = coaches.copy()
    competitive = GOALS[goal][1]
    c["score"] = (
        c["discipline"].map(lambda d: any(k in d for k in DISCIPLINES[style])) * 40
        + (c["best_for"] == style) * 15
        + (c["stance"] == stance) * 20 + (c["stance"] == "Switch") * 10
        + (c["hand"] == hand) * 5
        + np.where(competitive, (c["level"] == "Competition") * 10, (c["level"] != "Competition") * 10)
        + c["years_coaching"].clip(upper=20) / 2
    )
    sc = c[c["discipline"].str.contains("Strength")]
    top = c[~c["discipline"].str.contains("Strength")].sort_values("score", ascending=False).head(n)
    return pd.concat([top, sc]).reset_index(drop=True)


# ============================================================================
# Gear: what to buy, in what size, and when — driven by the classes in the roadmap
# ============================================================================
# Every item names the classes that need it, so a recommendation can always say why.
# `styles` limits an item to some fighting styles; `optional` items are nice to have and are left
# out of the totals. Prices are typical Australian retail ranges
# in AUD (low, high), not quotes; no brands.
GEAR = {
    "hand_wraps": dict(item="Hand wraps", cat="Hands", price=(12, 30),
                       needs={"Boxing Fundamentals", "Southpaw & Open-Stance Lab", "Muay Thai Technique",
                              "Kickboxing Conditioning", "Controlled Sparring", "MMA Integration",
                              "Competition Team"},
                       why="Protect the small bones of the hand and the wrist under every glove."),
    "boxing_gloves": dict(item="Boxing gloves", cat="Hands", price=(60, 220),
                       needs={"Boxing Fundamentals", "Southpaw & Open-Stance Lab", "Muay Thai Technique",
                              "Kickboxing Conditioning", "Controlled Sparring", "Competition Team"},
                       why="For pads, bag work and striking sparring."),
    "bag_mitts": dict(item="Bag mitts", cat="Hands", price=(40, 120), optional=True,
                      needs={"Boxing Fundamentals", "Kickboxing Conditioning", "Muay Thai Technique"},
                      why="Light gloves for heavy-bag rounds that spare your sparring gloves; never spar in them."),
    "mouthguard": dict(item="Mouthguard", cat="Protection", price=(15, 60),
                       needs={"Controlled Sparring", "Competition Team", "MMA Integration",
                              "Wrestling for MMA", "No-Gi Grappling", "BJJ Fundamentals (Gi)"},
                       why="Required for any live rounds, striking or grappling."),
    "groin": dict(item="Groin guard", cat="Protection", price=(30, 90),
                  needs={"Controlled Sparring", "Competition Team", "MMA Integration",
                         "Muay Thai Technique", "Kickboxing Conditioning"},
                  why="Kicks and knees land low by accident; most gyms require one for sparring."),
    "shins": dict(item="Shin guards", cat="Protection", price=(60, 200),
                  needs={"Muay Thai Technique", "Kickboxing Conditioning", "Controlled Sparring",
                         "MMA Integration", "Competition Team"},
                  why="Protect you and your partner when checking and throwing kicks."),
    "headgear": dict(item="Headgear", cat="Protection", price=(70, 220),
                     needs={"Controlled Sparring", "Competition Team"},
                     why="Cuts the risk of cuts and bruising in sparring; required for most amateur bouts."),
    "mma_spar": dict(item="MMA sparring gloves (7 oz)", cat="Hands", price=(70, 160),
                     needs={"MMA Integration"},
                     why="Padded enough for striking, open enough to grab and grapple."),
    "mma_fight": dict(item="MMA fight gloves (4 oz)", cat="Hands", price=(60, 150),
                      needs={"Competition Team"}, styles={"All-rounder"},
                      why="The glove you compete in; train with it in the weeks before a bout."),
    "gi": dict(item="BJJ gi", cat="Grappling", price=(100, 260),
               needs={"BJJ Fundamentals (Gi)"}, why="Required for gi classes."),
    "rash": dict(item="Rash guard", cat="Grappling", price=(40, 110),
                 needs={"No-Gi Grappling", "Wrestling for MMA", "MMA Integration", "Competition Team"},
                 styles={"Grappler", "All-rounder"},
                 why="Tight top that won't catch fingers or toes; keeps mats hygienic."),
    "fight_shorts": dict(item="MMA shorts", cat="Grappling", price=(40, 110),
                         needs={"No-Gi Grappling", "Wrestling for MMA", "MMA Integration"},
                         why="Split-leg shorts with no pockets or zips: free to kick, nothing to catch on."),
    "wrestling_shoes": dict(item="Wrestling shoes", cat="Grappling", price=(80, 180),
                            needs={"Wrestling for MMA"},
                            why="Grip for shots and sprawls if your gym wrestles in shoes (some go barefoot)."),
    "ear_guards": dict(item="Ear guards", cat="Grappling", price=(30, 70), optional=True,
                       needs={"Wrestling for MMA", "No-Gi Grappling", "BJJ Fundamentals (Gi)"},
                       why="Wrestling headgear that prevents cauliflower ear from friction in the clinch and on the mat."),
    "boxing_shoes": dict(item="Boxing shoes", cat="Conditioning", price=(90, 280), optional=True,
                         needs={"Boxing Fundamentals", "Southpaw & Open-Stance Lab"},
                         why="Light, flat-soled and ankle-high for pivots on canvas; only for gyms that train in shoes."),
    "knee_pads": dict(item="Knee pads", cat="Grappling", price=(30, 80), optional=True,
                      needs={"Wrestling for MMA", "No-Gi Grappling", "MMA Integration"},
                      why="Padding for knees that hit the mat hundreds of times a session in shots and scrambles."),
    "ankle_supports": dict(item="Ankle supports", cat="Protection", price=(15, 40), optional=True,
                           needs={"Muay Thai Technique", "Kickboxing Conditioning"},
                           why="Light compression for ankles that pivot on every kick; not a fix for an injury."),
    "timer": dict(item="Round timer", cat="Conditioning", price=(40, 150), optional=True, needs=None,
                  why="Rounds and rest on the clock, so shadowboxing and home sessions run like a real class."),
    "gym_bag": dict(item="Gym backpack", cat="Conditioning", price=(50, 180), optional=True, needs=None,
                    why="Separate pockets keep wet gloves and wraps away from clean clothes so they dry and don't smell."),
    "rope": dict(item="Skipping rope", cat="Conditioning", price=(15, 45),
                 needs=None, why="Cheapest conditioning there is: footwork rhythm and a warm-up anywhere."),
}
BUDGETS = {"Tight": 0.0, "Balanced": 0.5, "Best kit": 1.0}   # where in the price range to aim


def glove_oz(weight_kg: float) -> int:
    """Sparring glove weight most gyms ask for at this bodyweight (bag work can go 2 oz lighter)."""
    return 12 if weight_kg < 57 else 14 if weight_kg < 75 else 16


def shin_size(height_cm: float) -> str:
    return "S" if height_cm < 165 else "M" if height_cm < 178 else "L" if height_cm < 188 else "XL"


def gi_size(height_cm: float, weight_kg: float, gender: str) -> str:
    """Common IBJJF-style sizing: the larger of the height and weight sizes."""
    if gender == "Women":
        by_h = 1 if height_cm < 160 else 2 if height_cm < 170 else 3 if height_cm < 178 else 4
        by_w = 1 if weight_kg < 55 else 2 if weight_kg < 65 else 3 if weight_kg < 75 else 4
        return f"F{max(by_h, by_w)}"
    by_h = 0 if height_cm < 163 else 1 if height_cm < 173 else 2 if height_cm < 183 else 3 if height_cm < 191 else 4
    by_w = 0 if weight_kg < 60 else 1 if weight_kg < 75 else 2 if weight_kg < 90 else 3 if weight_kg < 105 else 4
    return f"A{max(by_h, by_w)}"


# For a grappler, sparring and the fight team mean live rolls, not striking rounds.
GRAPPLER_ROLLS = {"Controlled Sparring", "Competition Team"}
STRIKING_KIT = {"hand_wraps", "boxing_gloves", "bag_mitts", "groin", "shins", "headgear",
                "boxing_shoes"}


def recommend_gear(*, height_cm: float, weight_kg: float, gender: str, goal: str, style: str,
                   rm: pd.DataFrame, budget: str = "Balanced") -> pd.DataFrame:
    """
    Gear for this person's roadmap. One row per item with its size, the month to buy it by (the start
    of the phase where a class first needs it), the classes that need it, and a price for the budget.
    `priority` is "Before day one" for anything the first phase needs, else "Before month N";
    optional items come last as "Optional extras" and are not part of any total.
    """
    competitive = GOALS[goal][1]
    first_need = {}                                     # class -> (phase index, start month)
    for i, r in rm.reset_index(drop=True).iterrows():
        for c in r["week"]:
            first_need.setdefault(c, (i, float(r["start_month"])))
    oz = glove_oz(weight_kg)
    size = {
        "hand_wraps": "4.5 m (180 in)" if weight_kg >= 55 else "3 m (120 in)",
        "boxing_gloves": f"{oz} oz", "bag_mitts": "Your glove size (S/M/L)",
        "mouthguard": "Boil-and-bite" + ("; a dentist-made one before you compete" if competitive else ""),
        "groin": "Chest and groin protector" if gender == "Women" else "Cup with jock or compression short",
        "shins": shin_size(height_cm),
        "headgear": "Open-face" if not competitive else "Open-face, competition approved",
        "mma_spar": "7 oz", "mma_fight": "4 oz", "gi": gi_size(height_cm, weight_kg, gender),
        "rash": "Fitted", "fight_shorts": "Your waist size; split leg",
        "wrestling_shoes": "Your shoe size, snug", "ear_guards": "One size, adjustable",
        "boxing_shoes": "Your shoe size, snug", "rope": "Speed rope, cut to your height",
        "knee_pads": "S/M/L by knee circumference", "ankle_supports": "Your shoe size range",
        "timer": "Wall or bag-mounted", "gym_bag": "35 L or more fits gloves and shins",
    }
    k = BUDGETS.get(budget, 0.5)
    rows = []
    for key, g in GEAR.items():
        if "styles" in g and style not in g["styles"]:
            continue
        needs = g["needs"]
        if needs is not None and style == "Grappler" and key in STRIKING_KIT:
            needs = needs - GRAPPLER_ROLLS
        if needs is None:
            phase, month, by = 0, 0.0, []
        else:
            hits = [(first_need[c], c) for c in needs if c in first_need]
            if not hits:
                continue
            (phase, month), _ = min(hits)
            by = sorted(c for _, c in hits)
        lo, hi = g["price"]
        rows.append(dict(key=key, item=g["item"], category=g["cat"], size=size[key], why=g["why"],
                         needed_for=by, phase=PHASES[phase][0], buy_by_month=round(month),
                         optional=bool(g.get("optional")),
                         priority="Optional extras" if g.get("optional")
                         else "Before day one" if phase == 0 else f"Before month {round(month)}",
                         price_aud=int(round((lo + k * (hi - lo)) / 5) * 5)))
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["optional", "buy_by_month", "category", "item"]).reset_index(drop=True)


# ============================================================================
# Sparring matchup vs Brian (rule-based, not a prediction)
# ============================================================================
def matchup_notes(stance: str, hand: str) -> dict:
    if stance == "Switch":
        stance = "Orthodox"
    if stance != BRIAN["stance"]:
        return dict(
            geometry="Open stance (mirror image)",
            summary="Your lead foot and Brian's lead foot sit on the same line — the "
                    "foot-stepping collision that started this project.",
            keys=["Win the outside-foot battle: whoever gets their lead foot outside owns the "
                  "straight rear-hand line.",
                  "The rear straight and rear body/liver kick are open on both sides.",
                  "Brian's lead hand is his dominant (right) hand, so expect a heavier jab and "
                  "lead hook than a typical southpaw's."])
    return dict(
        geometry="Closed stance (same stance)",
        summary="Lead sides line up against each other, so the jab and lead hook become the main "
                "weapons for both of you.",
        keys=["The jab battle decides range — Brian's right-handed jab is his best weapon.",
              "Lead-leg kicks and outside angles work better than rear-hand power.",
              "Step off to the outside of his lead foot before throwing the rear hand."])
