"""
Public Transport Fetcher
========================
Counts public transport stops per suburb using OpenStreetMap Overpass API.
Covers bus stops, train stations, tram stops, and ferry terminals.

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

_STATE_FULL = {
    "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
    "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
    "NT": "Northern Territory", "ACT": "Australian Capital Territory",
}

# OSM tags for each transport mode
TRANSPORT_TAGS = {
    "train_station": '[railway~"station|halt"]',
    "bus_stop": '[highway="bus_stop"]',
    "tram_stop": '[railway="tram_stop"]',
    "ferry_terminal": '[amenity="ferry_terminal"]',
    "subway_station": '[station="subway"]',
}

# Score weights: rail > bus > others
TRANSPORT_WEIGHTS = {
    "train_station": 5.0,
    "subway_station": 5.0,
    "tram_stop": 3.0,
    "bus_stop": 1.0,
    "ferry_terminal": 2.0,
}


def _overpass_count(suburb: str, state_full: str, tag: str) -> int:
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


class TransportFetcher(BaseFetcher):
    """
    Fetches public transport stop counts per suburb from OpenStreetMap.

    Outputs: train_station_count, bus_stop_count, tram_stop_count,
             ferry_terminal_count, transit_score (0-10)
    """

    SOURCE_KEY = "transport"
    CACHE_TTL_HOURS = 720  # 30 days

    def __init__(self, cache: DataCache, suburbs: List[Dict] = None):
        super().__init__(cache)
        self._suburbs = suburbs or []

    def _fetch_raw(self) -> pd.DataFrame:
        if not self._suburbs:
            logger.warning("TransportFetcher: no suburb list provided — skipping")
            return pd.DataFrame()

        rows = []
        total = len(self._suburbs)
        for i, s in enumerate(self._suburbs):
            suburb, state = s.get("suburb", ""), s.get("state", "")
            if not suburb or not state:
                continue
            state_full = _STATE_FULL.get(state.upper(), state)

            counts = {"suburb": suburb, "state": state}
            for mode, tag in TRANSPORT_TAGS.items():
                counts[f"{mode}_count"] = _overpass_count(suburb, state_full, tag)
                time.sleep(0.5)

            rows.append(counts)
            if (i + 1) % 10 == 0:
                logger.info(f"TransportFetcher: {i+1}/{total} suburbs done")
            time.sleep(1)

        return pd.DataFrame(rows)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Weighted transit score: rail counts more
        weighted = pd.Series(0.0, index=df.index)
        for mode, weight in TRANSPORT_WEIGHTS.items():
            col = f"{mode}_count"
            if col in df.columns:
                weighted += df[col].clip(0, 10) * weight

        # Max practical score: 1 train station (5) + 10 bus stops (10) + 1 tram (3) = 18
        df["transit_score"] = (weighted / 18 * 10).clip(0, 10).round(2)

        # Flag: has heavy rail (train or subway)
        rail_cols = [c for c in ["train_station_count", "subway_station_count"] if c in df.columns]
        if rail_cols:
            df["has_train_station"] = df[rail_cols].sum(axis=1) > 0

        df["suburb"] = df["suburb"].str.strip().str.title()
        df["state"] = df["state"].str.strip().str.upper()

        return df
