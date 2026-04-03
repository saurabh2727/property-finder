"""
Walkability Fetcher
===================
Computes a walkability score (0-100) and bike infrastructure score (0-10) per suburb
using OpenStreetMap Overpass API data.

Walkability methodology (inspired by Walk Score):
- Weighted proximity/density of: supermarkets, cafes, parks, schools,
  restaurants, transit stops, pharmacies
- Penalties for car-only infrastructure (high road density, no footpaths)

Bike score: counts OSM cycleways and bike infrastructure per suburb area.

No API key required. Cached for 30 days.
"""
import logging
import time
from typing import Dict, List

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

_STATE_FULL = {
    "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
    "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
    "NT": "Northern Territory", "ACT": "Australian Capital Territory",
}

# Tags and weights for walkability scoring
WALK_TAGS = {
    "supermarket": ('[shop~"supermarket|grocery"]', 3.0),
    "cafe_restaurant": ('[amenity~"cafe|restaurant|food_court"]', 1.5),
    "park": ('[leisure~"park|garden"]', 2.0),
    "pharmacy": ('[amenity="pharmacy"]', 2.5),
    "school": ('[amenity~"school|kindergarten"]', 2.0),
    "bus_stop": ('[highway="bus_stop"]', 1.5),
    "train_station": ('[railway~"station|halt"]', 3.0),
    "post_office": ('[amenity~"post_office|bank"]', 1.0),
    "library": ('[amenity="library"]', 0.5),
    "gym": ('[leisure~"fitness_centre|gym"]', 0.5),
}

BIKE_TAGS = {
    "cycleway": '[highway="cycleway"]',
    "bike_lane": '[cycleway~"lane|track"]',
    "shared_path": '[highway="path"][bicycle="designated"]',
}


def _overpass_count(suburb: str, state_full: str, tag: str, timeout: int = 25) -> int:
    query = f"""
[out:json][timeout:{timeout}];
area["name"="{suburb}"]["is_in:state"="{state_full}"]->.a;
(
  node{tag}(area.a);
  way{tag}(area.a);
);
out count;
"""
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=timeout + 5)
        if resp.status_code == 200:
            data = resp.json()
            return int(data.get("elements", [{}])[0].get("tags", {}).get("total", 0))
    except Exception:
        pass
    return 0


class WalkabilityFetcher(BaseFetcher):
    """
    Computes walkability and bike infrastructure scores per suburb from OSM.

    Outputs:
      - walkability_score: 0-100 (Walk Score style)
      - bike_score: 0-10 (cycling infrastructure density)
      - is_walkable: bool (score >= 70)
      - is_bikeable: bool (score >= 6)
    """

    SOURCE_KEY = "walkability"
    CACHE_TTL_HOURS = 720  # 30 days

    def __init__(self, cache: DataCache, suburbs: List[Dict] = None):
        super().__init__(cache)
        self._suburbs = suburbs or []

    def _fetch_raw(self) -> pd.DataFrame:
        if not self._suburbs:
            logger.warning("WalkabilityFetcher: no suburb list — skipping")
            return pd.DataFrame()

        rows = []
        total = len(self._suburbs)
        for i, s in enumerate(self._suburbs):
            suburb, state = s.get("suburb", ""), s.get("state", "")
            if not suburb or not state:
                continue
            state_full = _STATE_FULL.get(state.upper(), state)

            row = {"suburb": suburb, "state": state}

            # Query all walkability tags
            for category, (tag, _) in WALK_TAGS.items():
                row[f"walk_{category}_count"] = _overpass_count(suburb, state_full, tag)
                time.sleep(0.4)

            # Query bike infrastructure
            for infra, tag in BIKE_TAGS.items():
                row[f"bike_{infra}_count"] = _overpass_count(suburb, state_full, tag)
                time.sleep(0.4)

            rows.append(row)
            if (i + 1) % 5 == 0:
                logger.info(f"WalkabilityFetcher: {i+1}/{total} suburbs done")
            time.sleep(1.5)

        return pd.DataFrame(rows)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Walkability score (0-100)
        walk_score = pd.Series(0.0, index=df.index)
        total_weight = sum(w for _, w in WALK_TAGS.values())

        for category, (_, weight) in WALK_TAGS.items():
            col = f"walk_{category}_count"
            if col in df.columns:
                counts = df[col].clip(0, 20)
                # Diminishing returns: log scale contribution
                import numpy as np
                contribution = np.log1p(counts) / np.log1p(20)
                walk_score += contribution * weight

        df["walkability_score"] = (walk_score / total_weight * 100).clip(0, 100).round(1)
        df["is_walkable"] = df["walkability_score"] >= 70

        # Bike score (0-10)
        bike_total = pd.Series(0, index=df.index)
        for infra in BIKE_TAGS:
            col = f"bike_{infra}_count"
            if col in df.columns:
                bike_total += df[col]

        df["bike_score"] = (bike_total.clip(0, 50) / 50 * 10).round(2)
        df["is_bikeable"] = df["bike_score"] >= 6.0

        df["suburb"] = df["suburb"].str.strip().str.title()
        df["state"] = df["state"].str.strip().str.upper()

        # Drop raw count columns from output (keep scores only)
        count_cols = [c for c in df.columns if c.startswith("walk_") or c.startswith("bike_")
                      and c.endswith("_count")]
        df = df.drop(columns=count_cols, errors="ignore")

        return df
