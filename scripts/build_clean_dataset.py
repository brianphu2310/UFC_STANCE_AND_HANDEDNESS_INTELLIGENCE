"""
Build data/ufc_fighters_clean.csv — the single dataset the Streamlit app reads.

Inputs
  * UFC_FINAL_DATASET.xlsx (sheet "🥊 Fighters Database") – the project's 117 fighters,
    full pro record, stance and dominant hand (Tapology).
  * ufc_data.csv – weight class + learning tip for 103 of them.
  * UFCSTATS scrape (github.com/Greco1899/scrape_ufc_stats) – physical attributes, date of
    birth, official stance and round-by-round fight stats. Downloaded to data/raw/ufcstats/
    on first run (that folder is git-ignored).

Output columns (one row per fighter) — see DATA_DICTIONARY at the bottom.

Run:  python scripts/build_clean_dataset.py
"""
from __future__ import annotations

import re
import subprocess
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "UFC_FINAL_DATASET.xlsx"
CSV = ROOT / "ufc_data.csv"
RAW = ROOT / "data" / "raw" / "ufcstats"
OUT = ROOT / "data" / "ufc_fighters_clean.csv"
UFCSTATS_REPO = "https://github.com/Greco1899/scrape_ufc_stats.git"
TODAY = date.today()

# Primary division for fighters whose weight class was missing or a fill value in ufc_data.csv.
WEIGHT_CLASS_FIXES = {
    "Jon Jones": "Light Heavyweight",
    "Ronda Rousey": "Women's Bantamweight", "Rose Namajunas": "Women's Strawweight",
    "Holly Holm": "Women's Bantamweight", "Miesha Tate": "Women's Bantamweight",
    "Carla Esparza": "Women's Strawweight", "Tatiana Suarez": "Women's Strawweight",
    "Amanda Nunes": "Women's Bantamweight", "Cris Cyborg": "Women's Featherweight",
    "Alexa Grasso": "Women's Flyweight", "Joanna Jedrzejczyk": "Women's Strawweight",
    "Zhang Weili": "Women's Strawweight", "Yan Xiaonan": "Women's Strawweight",
    "Valentina Shevchenko": "Women's Flyweight",
    "Tyron Woodley": "Welterweight", "Randy Couture": "Heavyweight",
    "Urijah Faber": "Bantamweight", "Sergio Pettis": "Flyweight", "Uriah Hall": "Middleweight",
    "Anthony Smith": "Light Heavyweight", "Wanderlei Silva": "Light Heavyweight",
    "Lyoto Machida": "Light Heavyweight", "Fabricio Werdum": "Heavyweight",
    "Junior Dos Santos": "Heavyweight", "Demian Maia": "Welterweight",
    "Thiago Alves": "Welterweight", "Cain Velasquez": "Heavyweight",
    "Zabit Magomedsharipov": "Featherweight", "Fedor Emelianenko": "Heavyweight",
    "Alexei Oleinik": "Heavyweight", "Andre Arlovski": "Heavyweight",
    "Mirko Cro Cop": "Heavyweight", "Nikita Krylov": "Light Heavyweight",
    "Dan Hardy": "Welterweight", "Paul Craig": "Light Heavyweight",
    "Gegard Mousasi": "Middleweight", "Bas Rutten": "Heavyweight", "Stefan Struve": "Heavyweight",
    "Melvin Manhoef": "Middleweight", "Martin Kampmann": "Welterweight",
    "Merab Dvalishvili": "Bantamweight", "Mark Hunt": "Heavyweight", "Tai Tuivasa": "Heavyweight",
    "Rory MacDonald": "Welterweight", "Yushin Okami": "Middleweight",
    "Dong Hyun Kim": "Welterweight", "Tarec Saffiedine": "Welterweight",
    "Georges St-Pierre": "Welterweight",
}
# Project name -> UFCSTATS name, where they differ.
NAME_ALIASES = {
    "Cris Cyborg": "Cristiane Justino", "Alexei Oleinik": "Aleksei Oleinik",
    "Andre Arlovski": "Andrei Arlovski", "Mirko Cro Cop": "Mirko Filipovic",
}
GENERIC_TIP = "Study fundamentals and signature techniques"


# ----------------------------------------------------------------------------
def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def ensure_ufcstats() -> None:
    if (RAW / "ufc_fight_stats.csv").exists():
        return
    RAW.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", UFCSTATS_REPO, str(RAW)], check=True)


def inches(v) -> float:
    """'5\\' 11"' -> 71 ; '74"' -> 74 ; '--' -> nan"""
    s = str(v)
    m = re.match(r"(\d+)' ?(\d+)", s)
    if m:
        return int(m[1]) * 12 + int(m[2])
    m = re.match(r"(\d+(?:\.\d+)?)\"", s)
    return float(m[1]) if m else np.nan


def of_pair(v):
    """'13 of 27' -> (13, 27)"""
    m = re.match(r"(\d+) of (\d+)", str(v))
    return (int(m[1]), int(m[2])) if m else (0, 0)


def mmss(v) -> int:
    m = re.match(r"(\d+):(\d+)", str(v))
    return int(m[1]) * 60 + int(m[2]) if m else 0


def fight_seconds(round_: int, time_: str, fmt: str) -> int:
    lengths = [int(x) * 60 for x in re.findall(r"\d+", fmt.split("(")[-1])] if "(" in fmt else []
    done = sum(lengths[: max(int(round_) - 1, 0)]) if lengths else 0
    return done + mmss(time_)


# ----------------------------------------------------------------------------
def load_base() -> pd.DataFrame:
    raw = pd.read_excel(XLSX, sheet_name="🥊 Fighters Database", header=None, skiprows=2)
    raw.columns = ["row", "fighter", "country", "continent", "stance_project", "hand",
                   "wins", "losses", "total_fights", "win_rate"]
    df = raw.drop(columns="row").dropna(subset=["fighter"])
    df = df[df["fighter"] != "Fighter Name"].copy()
    for c in ["wins", "losses"]:
        df[c] = pd.to_numeric(df[c], errors="raise").astype(int)
    df["total_fights"] = df["wins"] + df["losses"]
    df["win_rate"] = (df["wins"] / df["total_fights"] * 100).round(2)

    extra = pd.read_csv(CSV).set_index("fighter_name")
    df["weight_class"] = df["fighter"].map(extra["weight_class"])
    df["learning_tip"] = df["fighter"].map(extra["learning_tip"]).fillna(GENERIC_TIP)
    df["weight_class_source"] = "original"
    fix = df["fighter"].map(WEIGHT_CLASS_FIXES)
    changed = fix.notna() & (fix != df["weight_class"])
    df.loc[changed, "weight_class"] = fix[changed]
    df.loc[changed, "weight_class_source"] = "corrected"
    df["gender"] = np.where(df["weight_class"].str.startswith("Women's"), "Women", "Men")
    df["key"] = df["fighter"].map(lambda n: norm(NAME_ALIASES.get(n, n)))
    return df


def load_tott() -> pd.DataFrame:
    t = pd.read_csv(RAW / "ufc_fighter_tott.csv")
    t["key"] = t["FIGHTER"].map(norm)
    t = t.drop_duplicates("key", keep=False)  # ambiguous names are dropped, never guessed
    t["height_cm"] = (t["HEIGHT"].map(inches) * 2.54).round(1)
    t["reach_cm"] = (t["REACH"].map(inches) * 2.54).round(1)
    t["stance_ufcstats"] = t["STANCE"].where(t["STANCE"].isin(["Orthodox", "Southpaw", "Switch"]))
    t["dob"] = pd.to_datetime(t["DOB"], format="%b %d, %Y", errors="coerce")
    t["ufcstats_url"] = t["URL"]
    return t[["key", "FIGHTER", "height_cm", "reach_cm", "stance_ufcstats", "dob", "ufcstats_url"]]


def career_stats(names: dict[str, str]) -> pd.DataFrame:
    """names: key -> UFCSTATS full name. Returns one row per key with UFC career stats."""
    res = pd.read_csv(RAW / "ufc_fight_results.csv")
    stats = pd.read_csv(RAW / "ufc_fight_stats.csv").dropna(subset=["FIGHTER"])
    events = pd.read_csv(RAW / "ufc_event_details.csv")
    for d in (res, stats, events):
        for c in ("EVENT", "BOUT", "FIGHTER"):
            if c in d:
                d[c] = d[c].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    events["date"] = pd.to_datetime(events["DATE"], format="%B %d, %Y", errors="coerce")
    res = res.merge(events[["EVENT", "date"]], on="EVENT", how="left")
    res["main_event"] = ~res.duplicated("EVENT")  # first bout listed = main event
    res["title"] = res["WEIGHTCLASS"].str.contains("Title", na=False)
    res["secs"] = [fight_seconds(r, t, f) for r, t, f in
                   zip(res["ROUND"], res["TIME"], res["TIME FORMAT"].astype(str))]
    res["method"] = res["METHOD"].str.strip()

    # per fighter per bout totals
    for col in ["SIG.STR.", "TD", "TOTAL STR."]:
        pairs = stats[col].map(of_pair)
        stats[col + "_l"] = [p[0] for p in pairs]
        stats[col + "_a"] = [p[1] for p in pairs]
    for col in ["HEAD", "BODY", "LEG", "DISTANCE", "CLINCH", "GROUND"]:
        stats[col + "_l"] = stats[col].map(lambda v: of_pair(v)[0])
    stats["ctrl_s"] = stats["CTRL"].map(mmss)
    stats["kd"] = pd.to_numeric(stats["KD"], errors="coerce").fillna(0)
    stats["sub_att"] = pd.to_numeric(stats["SUB.ATT"], errors="coerce").fillna(0)
    num = [c for c in stats.columns if c.endswith(("_l", "_a"))] + ["ctrl_s", "kd", "sub_att"]
    per_bout = stats.groupby(["EVENT", "BOUT", "FIGHTER"], as_index=False)[num].sum()

    rows = []
    wanted = {v: k for k, v in names.items()}
    res["f1"] = res["BOUT"].str.split(" vs. ").str[0].str.strip()
    res["f2"] = res["BOUT"].str.split(" vs. ").str[-1].str.strip()
    for full, key in wanted.items():
        mine = res[(res["f1"] == full) | (res["f2"] == full)]
        if mine.empty:
            continue
        me_first = mine["f1"] == full
        outcome = np.where(me_first, mine["OUTCOME"].str.split("/").str[0],
                           mine["OUTCOME"].str.split("/").str[1])
        opp = np.where(me_first, mine["f2"], mine["f1"])
        won = outcome == "W"
        b = mine[["EVENT", "BOUT"]].assign(me=full, opp=opp)
        mine_s = b.merge(per_bout, left_on=["EVENT", "BOUT", "me"],
                         right_on=["EVENT", "BOUT", "FIGHTER"], how="left")
        opp_s = b.merge(per_bout, left_on=["EVENT", "BOUT", "opp"],
                        right_on=["EVENT", "BOUT", "FIGHTER"], how="left")
        has = mine_s["SIG.STR._a"].notna().to_numpy()
        secs = mine["secs"].to_numpy()[has].sum()
        mins = secs / 60 if secs else np.nan
        S, O = mine_s[has], opp_s[has]
        sig_l, sig_a = S["SIG.STR._l"].sum(), S["SIG.STR._a"].sum()
        osig_l, osig_a = O["SIG.STR._l"].sum(), O["SIG.STR._a"].sum()
        td_l, td_a = S["TD_l"].sum(), S["TD_a"].sum()
        otd_l, otd_a = O["TD_l"].sum(), O["TD_a"].sum()
        pos = S[["DISTANCE_l", "CLINCH_l", "GROUND_l"]].sum()
        tgt = S[["HEAD_l", "BODY_l", "LEG_l"]].sum()
        meth = mine["method"].to_numpy()
        rows.append(dict(
            key=key,
            ufc_fights=len(mine), ufc_wins=int(won.sum()),
            ufc_losses=int((outcome == "L").sum()),
            ufc_ko_wins=int((won & pd.Series(meth).str.contains("KO").to_numpy()).sum()),
            ufc_sub_wins=int((won & (meth == "Submission")).sum()),
            ufc_dec_wins=int((won & pd.Series(meth).str.startswith("Decision").to_numpy()).sum()),
            title_fights=int(mine["title"].sum()),
            main_events=int(mine["main_event"].sum()),
            first_ufc_fight=mine["date"].min(), last_ufc_fight=mine["date"].max(),
            stats_fights=int(has.sum()), ufc_minutes=round(mins, 1) if mins == mins else np.nan,
            slpm=sig_l / mins if mins else np.nan,
            str_acc=sig_l / sig_a * 100 if sig_a else np.nan,
            sapm=osig_l / mins if mins else np.nan,
            str_def=(1 - osig_l / osig_a) * 100 if osig_a else np.nan,
            td_avg=td_l / mins * 15 if mins else np.nan,
            td_acc=td_l / td_a * 100 if td_a else np.nan,
            td_def=(1 - otd_l / otd_a) * 100 if otd_a else np.nan,
            sub_avg=S["sub_att"].sum() / mins * 15 if mins else np.nan,
            kd_avg=S["kd"].sum() / mins * 15 if mins else np.nan,
            ctrl_pct=S["ctrl_s"].sum() / secs * 100 if secs else np.nan,
            pct_distance=pos["DISTANCE_l"] / sig_l * 100 if sig_l else np.nan,
            pct_clinch=pos["CLINCH_l"] / sig_l * 100 if sig_l else np.nan,
            pct_ground=pos["GROUND_l"] / sig_l * 100 if sig_l else np.nan,
            pct_head=tgt["HEAD_l"] / sig_l * 100 if sig_l else np.nan,
            pct_body=tgt["BODY_l"] / sig_l * 100 if sig_l else np.nan,
            pct_leg=tgt["LEG_l"] / sig_l * 100 if sig_l else np.nan,
        ))
    return pd.DataFrame(rows)


def classify_style(df: pd.DataFrame) -> pd.Series:
    """Striker / Grappler / All-rounder from UFC stats, relative to this dataset.

    striking = mean percentile of sig. strikes landed per min and knockdowns per 15
    grappling = mean percentile of takedowns per 15, sub attempts per 15 and control-time %
    gap > 0.15 either way -> the stronger side; otherwise All-rounder.
    """
    ok = df["stats_fights"].fillna(0) >= 3
    pr = lambda c: df.loc[ok, c].rank(pct=True)
    strike = (pr("slpm") + pr("kd_avg")) / 2
    grapple = (pr("td_avg") + pr("sub_avg") + pr("ctrl_pct")) / 3
    out = pd.Series("Not enough UFC data", index=df.index)
    gap = grapple - strike
    out.loc[ok] = np.select([gap > 0.15, gap < -0.15], ["Grappler", "Striker"], "All-rounder")
    df.loc[ok, "striking_index"] = (strike * 100).round(0)
    df.loc[ok, "grappling_index"] = (grapple * 100).round(0)
    return out


def build() -> pd.DataFrame:
    ensure_ufcstats()
    df = load_base()
    tott = load_tott()
    df = df.merge(tott, on="key", how="left")
    missing = df.loc[df["FIGHTER"].isna(), "fighter"].tolist()
    assert not missing, f"no UFCSTATS match for {missing}"

    cs = career_stats(dict(zip(df["key"], df["FIGHTER"])))
    df = df.merge(cs, on="key", how="left")

    df["age"] = ((pd.Timestamp(TODAY) - df["dob"]).dt.days / 365.25).round(1)
    df["age_at_last_ufc_fight"] = ((df["last_ufc_fight"] - df["dob"]).dt.days / 365.25).round(1)
    df["active"] = df["last_ufc_fight"] >= pd.Timestamp(TODAY) - pd.Timedelta(days=730)
    df["ape_index_cm"] = (df["reach_cm"] - df["height_cm"]).round(1)
    df["headliner_index"] = df["main_events"].fillna(0) + df["title_fights"].fillna(0)
    df["fighting_style"] = classify_style(df)
    df["stance_ufcstats"] = df["stance_ufcstats"].fillna(df["stance_project"])

    rnd = ["slpm", "str_acc", "sapm", "str_def", "td_avg", "td_acc", "td_def", "sub_avg",
           "kd_avg", "ctrl_pct", "pct_distance", "pct_clinch", "pct_ground", "pct_head",
           "pct_body", "pct_leg"]
    df[rnd] = df[rnd].round(2)
    for c in ["dob", "first_ufc_fight", "last_ufc_fight"]:
        df[c] = df[c].dt.date
    df = df.drop(columns=["key", "FIGHTER"])
    assert df["fighter"].is_unique and len(df) == 117
    return df


DATA_DICTIONARY = """
fighter, country, continent, hand, wins, losses, total_fights, win_rate  – project dataset (full pro record)
stance_project        – stance in the project's Excel master
stance_ufcstats       – official UFCSTATS stance (Orthodox / Southpaw / Switch)
weight_class(_source) – primary division; 'corrected' where ufc_data.csv was missing/fill value
height_cm, reach_cm, ape_index_cm, dob, age, age_at_last_ufc_fight – UFCSTATS
ufc_*                 – UFC-only record and finishes (UFCSTATS results)
title_fights, main_events, headliner_index – popularity proxy
slpm/sapm             – sig. strikes landed / absorbed per minute
str_acc/str_def, td_acc/td_def – %  ;  td_avg, sub_avg, kd_avg – per 15 min ; ctrl_pct – % of fight time
pct_distance/clinch/ground, pct_head/body/leg – share of sig. strikes landed
fighting_style, striking_index, grappling_index – rule-based, see classify_style()
"""

if __name__ == "__main__":
    out = build()
    OUT.parent.mkdir(exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(out)} rows × {out.shape[1]} cols")
    print(out["fighting_style"].value_counts().to_string())
    print("no UFC stats:", out.loc[out["stats_fights"].isna(), "fighter"].tolist())
