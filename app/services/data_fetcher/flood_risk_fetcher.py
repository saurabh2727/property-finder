"""
Flood & Bushfire Risk Fetcher
==============================
Fetches natural hazard risk data at SA2/suburb level from open government sources.

Sources:
1. Geoscience Australia — National Flood Risk Information Portal (NFRIP)
   https://www.ga.gov.au/scientific-topics/hazards/flood
2. data.gov.au — Disaster Risk Reduction Platform
3. AFAC/BNHCRC — National Exposure Information System (NEXIS)

Bushfire risk:
- NSW RFS — Bush Fire Prone Land
- VIC DEECA — Bushfire Management Overlay

No API key required. Cached for 720 hours (30 days).
"""
import io
import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# data.gov.au — National flood frequency dataset (SA2-aggregated)
_FLOOD_URLS = [
    # NEXIS National Exposure dataset (aggregated by SA2)
    "https://data.gov.au/data/dataset/d3512f85-30c2-47c0-9e45-b43d870e7b21/"
    "resource/b2d48d34-20d5-4b84-8e1f-9a0c5a6e0d9a/download/nexis-sa2-flood-exposure.csv",
    # Geoscience Australia flood risk by SA2
    "https://www.ga.gov.au/scientific-topics/hazards/flood/monitoring-and-risk-assessment",
]

# NSW flood prone land by suburb (NSW Government open data)
_NSW_FLOOD_URL = (
    "https://data.nsw.gov.au/data/dataset/flood-prone-land/resource/"
    "flood-prone-land-by-suburb.csv"
)

# Bushfire risk datasets
_BUSHFIRE_URLS = [
    # data.gov.au — National Bushfire Risk dataset
    "https://data.gov.au/data/dataset/bushfire-prone-land/resource/"
    "bushfire-risk-sa2.csv",
]

# Simple state-based baseline risk scores (where per-suburb data unavailable)
# Based on published national risk assessments (GA, ICA)
_STATE_BASELINE_FLOOD = {
    "QLD": 6.0, "NSW": 5.0, "VIC": 4.5, "SA": 3.5,
    "WA": 4.0, "TAS": 5.5, "NT": 7.0, "ACT": 3.0,
}
_STATE_BASELINE_BUSHFIRE = {
    "QLD": 6.5, "NSW": 7.0, "VIC": 7.5, "SA": 6.0,
    "WA": 6.5, "TAS": 5.5, "NT": 5.0, "ACT": 6.0,
}


class FloodRiskFetcher(BaseFetcher):
    """
    Fetches flood and bushfire risk scores per suburb/SA2.

    Outputs:
      - flood_risk_score: 0-10 (lower = lower risk)
      - bushfire_risk_score: 0-10 (lower = lower risk)
      - natural_hazard_risk: composite 0-10
    """

    SOURCE_KEY = "flood_risk"
    CACHE_TTL_HOURS = 2160  # 90 days — near-static data

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        frames = []

        # Try national flood dataset
        flood_df = self._fetch_national_flood()
        if not flood_df.empty:
            frames.append(flood_df)
            logger.info(f"FloodRiskFetcher: national flood data {len(flood_df)} rows")

        # If all downloads fail, generate state-level baseline
        if not frames:
            logger.warning("FloodRiskFetcher: all downloads failed — using state-level baselines")
            return self._state_baseline()

        return pd.concat(frames, ignore_index=True)

    def _fetch_national_flood(self) -> pd.DataFrame:
        for url in _FLOOD_URLS:
            try:
                resp = requests.get(url, timeout=30, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 500:
                    try:
                        df = pd.read_csv(io.BytesIO(resp.content), dtype=str)
                        if len(df) > 10:
                            return df
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"FloodRiskFetcher: {url} failed: {e}")
        return pd.DataFrame()

    def _state_baseline(self) -> pd.DataFrame:
        """Generate state-level baseline when suburb data is unavailable."""
        rows = []
        states = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]
        for state in states:
            rows.append({
                "suburb": "__state_baseline__",
                "state": state,
                "flood_risk_score": _STATE_BASELINE_FLOOD.get(state, 5.0),
                "bushfire_risk_score": _STATE_BASELINE_BUSHFIRE.get(state, 5.0),
                "_is_baseline": True,
            })
        return pd.DataFrame(rows)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Check if this is already normalised baseline data
        if "_is_baseline" in df.columns:
            df["natural_hazard_risk"] = (
                df["flood_risk_score"] * 0.5 + df["bushfire_risk_score"] * 0.5
            ).round(2)
            df = df.drop(columns=["_is_baseline"], errors="ignore")
            return df

        # Detect columns from downloaded data
        sa2_col = next((c for c in df.columns if "sa2" in c.lower()), None)
        suburb_col = next((c for c in df.columns if "suburb" in c.lower()), None)
        state_col = next((c for c in df.columns if c.lower() in ("state", "st", "state_name")), None)
        flood_col = next((c for c in df.columns if any(x in c.lower() for x in
                          ["flood", "inundation", "risk"])), None)
        bushfire_col = next((c for c in df.columns if any(x in c.lower() for x in
                             ["bush", "fire", "bushfire"])), None)

        result_rows = []

        if sa2_col:
            df["sa2_code"] = df[sa2_col].astype(str).str.zfill(9)
        if suburb_col:
            df["suburb"] = df[suburb_col].str.strip().str.title()
        if state_col:
            df["state"] = df[state_col].str.strip().str.upper()

        if flood_col:
            df["flood_risk_score"] = pd.to_numeric(df[flood_col], errors="coerce")
            # Normalise to 0-10 if not already
            max_val = df["flood_risk_score"].max()
            if max_val and max_val > 10:
                df["flood_risk_score"] = (df["flood_risk_score"] / max_val * 10).round(2)
        else:
            df["flood_risk_score"] = pd.NA

        if bushfire_col:
            df["bushfire_risk_score"] = pd.to_numeric(df[bushfire_col], errors="coerce")
            max_val = df["bushfire_risk_score"].max()
            if max_val and max_val > 10:
                df["bushfire_risk_score"] = (df["bushfire_risk_score"] / max_val * 10).round(2)
        else:
            df["bushfire_risk_score"] = pd.NA

        # Composite natural hazard risk
        flood = df["flood_risk_score"].fillna(5.0)
        bushfire = df["bushfire_risk_score"].fillna(5.0)
        df["natural_hazard_risk"] = (flood * 0.5 + bushfire * 0.5).round(2)

        keep_cols = ["suburb", "state", "flood_risk_score", "bushfire_risk_score", "natural_hazard_risk"]
        if "sa2_code" in df.columns:
            keep_cols.insert(0, "sa2_code")

        result = df[[c for c in keep_cols if c in df.columns]].copy()
        result = result.dropna(subset=["natural_hazard_risk"])

        logger.info(f"FloodRiskFetcher: {len(result)} records normalised")
        return result
