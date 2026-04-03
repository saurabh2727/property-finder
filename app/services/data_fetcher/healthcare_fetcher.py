"""
Healthcare Fetcher
==================
Counts healthcare facilities per suburb using two sources:
1. data.gov.au — AIHW hospital locations (national, free download)
2. OpenStreetMap Overpass API — GPs, clinics, pharmacies

No API key required for either source. Cached for 30 days.
"""
import io
import logging
import time
from typing import Dict, List

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# AIHW hospital locations from data.gov.au
_AIHW_URL = (
    "https://data.gov.au/data/dataset/2b53da3a-4939-48b3-97e8-f1e4d05e2d80/"
    "resource/628a4bfb-8c10-47d0-aeb6-0e2e5a57dbb7/download/hospital-locations-2021.csv"
)

_STATE_FULL = {
    "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
    "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
    "NT": "Northern Territory", "ACT": "Australian Capital Territory",
}

HEALTHCARE_TAGS = {
    "hospital": '[amenity="hospital"]',
    "clinic": '[amenity~"clinic|doctors|health_centre"]',
    "pharmacy": '[amenity="pharmacy"]',
    "dentist": '[amenity="dentist"]',
}

HEALTHCARE_WEIGHTS = {
    "hospital": 5.0,
    "clinic": 2.0,
    "pharmacy": 1.5,
    "dentist": 1.0,
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


class HealthcareFetcher(BaseFetcher):
    """
    Fetches healthcare facility counts per suburb.

    Outputs: hospital_count, clinic_count, pharmacy_count, dentist_count,
             healthcare_score (0-10)
    """

    SOURCE_KEY = "healthcare"
    CACHE_TTL_HOURS = 720  # 30 days

    def __init__(self, cache: DataCache, suburbs: List[Dict] = None):
        super().__init__(cache)
        self._suburbs = suburbs or []

    def _fetch_raw(self) -> pd.DataFrame:
        # Try AIHW national hospital file first to get suburb-level hospital counts
        aihw_df = self._fetch_aihw_hospitals()

        # Then enrich with OSM for clinics/GPs/pharmacies
        osm_df = self._fetch_osm()

        if not aihw_df.empty and not osm_df.empty:
            merged = osm_df.merge(
                aihw_df[["suburb", "state", "hospital_count"]],
                on=["suburb", "state"], how="left", suffixes=("", "_aihw")
            )
            # Use AIHW hospital count if available (more accurate than OSM)
            if "hospital_count_aihw" in merged.columns:
                merged["hospital_count"] = merged["hospital_count_aihw"].fillna(
                    merged["hospital_count"]
                )
                merged = merged.drop(columns=["hospital_count_aihw"])
            return merged

        if not osm_df.empty:
            return osm_df
        return aihw_df

    def _fetch_aihw_hospitals(self) -> pd.DataFrame:
        try:
            resp = requests.get(_AIHW_URL, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                df = pd.read_csv(io.BytesIO(resp.content), dtype=str)
                # Detect suburb/state columns
                suburb_col = next((c for c in df.columns if "suburb" in c.lower() or "town" in c.lower()), None)
                state_col = next((c for c in df.columns if c.lower() in ("state", "st")), None)
                if suburb_col and state_col:
                    df["suburb"] = df[suburb_col].str.strip().str.title()
                    df["state"] = df[state_col].str.strip().str.upper()
                    agg = df.groupby(["suburb", "state"]).size().reset_index(name="hospital_count")
                    logger.info(f"HealthcareFetcher: AIHW loaded {len(agg)} suburb hospital counts")
                    return agg
        except Exception as e:
            logger.warning(f"HealthcareFetcher: AIHW download failed: {e}")
        return pd.DataFrame()

    def _fetch_osm(self) -> pd.DataFrame:
        if not self._suburbs:
            return pd.DataFrame()

        rows = []
        total = len(self._suburbs)
        for i, s in enumerate(self._suburbs):
            suburb, state = s.get("suburb", ""), s.get("state", "")
            if not suburb or not state:
                continue
            state_full = _STATE_FULL.get(state.upper(), state)

            counts = {"suburb": suburb, "state": state}
            for facility, tag in HEALTHCARE_TAGS.items():
                counts[f"{facility}_count"] = _overpass_count(suburb, state_full, tag)
                time.sleep(0.5)

            rows.append(counts)
            if (i + 1) % 10 == 0:
                logger.info(f"HealthcareFetcher: {i+1}/{total} OSM suburbs done")
            time.sleep(1)

        return pd.DataFrame(rows)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        weighted = pd.Series(0.0, index=df.index)
        for facility, weight in HEALTHCARE_WEIGHTS.items():
            col = f"{facility}_count"
            if col in df.columns:
                weighted += df[col].clip(0, 5) * weight

        # Max: 1 hospital (5) + 3 clinics (6) + 3 pharmacies (4.5) + 2 dentists (2) = 17.5
        df["healthcare_score"] = (weighted / 17.5 * 10).clip(0, 10).round(2)

        df["suburb"] = df["suburb"].str.strip().str.title()
        df["state"] = df["state"].str.strip().str.upper()

        return df
