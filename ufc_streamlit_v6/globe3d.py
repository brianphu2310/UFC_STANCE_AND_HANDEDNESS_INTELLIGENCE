"""Rotatable 3D globe with fighter names per country (three.js, served locally — no CDN)."""
import json
from pathlib import Path

import pandas as pd
import streamlit.components.v1 as components

_DIR = Path(__file__).parent / "components" / "globe3d"
_component = components.declare_component("globe3d", path=str(_DIR))

ISO3 = {"USA": "USA", "Brazil": "BRA", "Russia": "RUS", "UK": "GBR", "Netherlands": "NLD",
        "Mexico": "MEX", "Poland": "POL", "France": "FRA", "Australia": "AUS", "Japan": "JPN",
        "Jamaica": "JAM", "Georgia": "GEO", "Canada": "CAN", "China": "CHN",
        "South Korea": "KOR", "Ecuador": "ECU", "Czech Rep.": "CZE", "Belarus": "BLR",
        "Croatia": "HRV", "Ukraine": "UKR", "Ireland": "IRL", "Denmark": "DNK",
        "Germany": "DEU", "Nigeria": "NGA", "Cameroon": "CMR", "New Zealand": "NZL",
        "Kyrgyzstan": "KGZ", "Belgium": "BEL"}


def _centroids() -> dict:
    topo = json.loads((_DIR / "world_110m.json").read_text())
    out = {g["id"]: g["properties"]["ct"] for g in topo["objects"]["countries"]["geometries"]
           if "id" in g and "ct" in g.get("properties", {})}
    out["USA"] = [-98.5, 39.5]   # contiguous US, not pulled north by Alaska
    out["CAN"] = [-100.0, 56.0]
    out["RUS"] = [60.0, 58.0]    # label nearer the populated west
    out["FRA"] = [2.3, 46.6]     # metropolitan France
    return out


CENTROIDS = _centroids()


def country_payload(df: pd.DataFrame, rank_col: str = "popularity_index") -> list[dict]:
    rows = []
    for country, g in df.sort_values(rank_col, ascending=False).groupby("country", sort=False):
        iso = ISO3.get(country)
        if not iso or iso not in CENTROIDS:
            continue
        lon, lat = CENTROIDS[iso]
        rows.append(dict(iso3=iso, name=country, lat=lat, lon=lon, count=int(len(g)),
                         fighters=g["fighter"].tolist()))
    return rows


def globe3d(countries: list[dict], height: int = 560, max_names: int = 3,
            selected: str | None = None, key: str | None = None):
    """Returns the ISO3 code of the country the user clicked (or None)."""
    return _component(countries=countries, height=height, max_names=max_names,
                      selected=selected, key=key, default=None)
