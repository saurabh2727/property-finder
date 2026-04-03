"""
Amenities Fetcher
=================
Queries OpenStreetMap Overpass API to count lifestyle amenities per suburb:
cafes, restaurants, supermarkets, parks, gyms, shopping centres.

Free, no API key required. Results cached for 30 days.
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

# Amenity categories and their OSM tags
AMENITY_TAGS = {
    "cafe": '[amenity~"cafe|coffee_shop"]',
    "restaurant": '[amenity="restaurant"]',
    "supermarket": '[shop~"supermarket|grocery"]',
    "park": '[leisure~"park|garden|nature_reserve"]',
    "gym": '[leisure~"fitness_centre|gym|sports_centre"]',
    "shopping": '[shop~"mall|department_store|shopping_centre"]',
    "pub_bar": '[amenity~"pub|bar"]',
}

# Weights for composite amenity score
AMENITY_WEIGHTS = {
    "supermarket": 2.0,
    "park": 1.5,
    "cafe": 1.0,
    "restaurant": 0.8,
    "gym": 1.2,
    "shopping": 1.5,
    "pub_bar": 0.5,
}


def _overpass_count(suburb: str, state: str, tag: str) -> int:
    """Count OSM nodes matching tag within a named suburb area."""
    state_full = {
        "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
        "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
        "NT": "Northern Territory", "ACT": "Australian Capital Territory",
    }.get(state.upper(), state)

    query = f"""
[out:json][timeout:25];
area["name"="{suburb}"]["is_in:state"="{state_full}"]->.a;
(
  node{tag}(area.a);
  way{tag}(area.a);
);
out count;
"""
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("elements", [{}])[0].get("tags", {}).get("total", 0)
    except Exception:
        pass
    return 0


class AmenitiesFetcher(BaseFetcher):
    """
    Fetches amenity counts per suburb from OpenStreetMap.

    Outputs: cafe_count, restaurant_count, supermarket_count, park_count,
             gym_count, shopping_count, amenity_score (0-10)
    """

    SOURCE_KEY = "amenities"
    CACHE_TTL_HOURS = 720  # 30 days

    def __init__(self, cache: DataCache, suburbs: List[Dict] = None):
        """
        Args:
            suburbs: List of {"suburb": str, "state": str} dicts to query.
                     If None, fetch() returns empty — must provide at merge time.
        """
        super().__init__(cache)
        self._suburbs = suburbs or []

    def _fetch_raw(self) -> pd.DataFrame:
        if not self._suburbs:
            logger.warning("AmenitiesFetcher: no suburb list provided — skipping OSM queries")
            return pd.DataFrame()

        rows = []
        total = len(self._suburbs)
        for i, s in enumerate(self._suburbs):
            suburb, state = s.get("suburb", ""), s.get("state", "")
            if not suburb or not state:
                continue

            counts = {}
            for amenity, tag in AMENITY_TAGS.items():
                counts[f"{amenity}_count"] = _overpass_count(suburb, state, tag)
                time.sleep(0.5)  # respect Overpass rate limits

            counts["suburb"] = suburb
            counts["state"] = state
            rows.append(counts)

            if (i + 1) % 10 == 0:
                logger.info(f"AmenitiesFetcher: {i+1}/{total} suburbs queried")
            time.sleep(1)  # extra pause between suburbs

        return pd.DataFrame(rows)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Composite amenity score (0-10)
        weighted = pd.Series(0.0, index=df.index)
        total_weight = sum(AMENITY_WEIGHTS.values())
        for amenity, weight in AMENITY_WEIGHTS.items():
            col = f"{amenity}_count"
            if col in df.columns:
                # Cap each category contribution, scale to 0-10
                capped = df[col].clip(0, 20)
                weighted += (capped / 20) * weight

        df["amenity_score"] = (weighted / total_weight * 10).clip(0, 10).round(2)

        df["suburb"] = df["suburb"].str.strip().str.title()
        df["state"] = df["state"].str.strip().str.upper()

        return df
