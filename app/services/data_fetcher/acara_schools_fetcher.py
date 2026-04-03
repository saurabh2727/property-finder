import io
import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# ACARA My School — bulk school profile download (free, no API key)
# Published under Creative Commons Attribution 4.0
# Updated annually after NAPLAN cycle
_DOWNLOAD_URLS = [
    # Primary: ACARA direct download (year may vary — try recent years)
    "https://www.acara.edu.au/docs/default-source/research-and-statistics/my-school-dataset.xlsx",
    # Fallback: data.gov.au CKAN resource
    "https://data.gov.au/data/dataset/australian-curriculum-assessment-and-reporting-authority-school-profiles/resource/school-profile",
    # Fallback 2: ACARA school locations CSV (more stable URL)
    "https://acara.edu.au/docs/default-source/research-and-statistics/school-profile.xlsx",
]

_STATE_ABBREV = {
    "New South Wales": "NSW", "Victoria": "VIC", "Queensland": "QLD",
    "South Australia": "SA", "Western Australia": "WA", "Tasmania": "TAS",
    "Northern Territory": "NT", "Australian Capital Territory": "ACT",
    "NSW": "NSW", "VIC": "VIC", "QLD": "QLD", "SA": "SA",
    "WA": "WA", "TAS": "TAS", "NT": "NT", "ACT": "ACT",
}


class ACARASchoolsFetcher(BaseFetcher):
    """
    Fetches ACARA My School dataset to derive suburb-level school quality scores.

    The ICSEA (Index of Community Socio-Educational Advantage) score is used
    as the school quality proxy. Range ~500–1300, national mean ~1000.
    Higher = more advantaged school community.

    Aggregation: median ICSEA score across all schools in a suburb.
    Also provides: count of schools, % of independent/catholic schools.
    """

    SOURCE_KEY = "acara_schools"
    CACHE_TTL_HOURS = 720  # 30 days — annual release

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        for url in _DOWNLOAD_URLS:
            try:
                logger.info(f"Trying ACARA download from: {url}")
                resp = requests.get(url, timeout=60, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    # Try Excel first, then CSV
                    try:
                        df = pd.read_excel(io.BytesIO(resp.content), dtype=str)
                    except Exception:
                        df = pd.read_csv(io.BytesIO(resp.content), dtype=str, encoding="latin-1")
                    logger.info(f"ACARA: downloaded {len(df)} schools from {url}")
                    return df
            except Exception as e:
                logger.warning(f"ACARA download failed ({url}): {e}")

        # Final fallback: data.gov.au CKAN API
        return self._fetch_from_ckan()

    def _fetch_from_ckan(self) -> pd.DataFrame:
        """Try data.gov.au CKAN API for ACARA school data."""
        try:
            url = "https://data.gov.au/api/3/action/datastore_search"
            # Search for ACARA school profile dataset
            params = {
                "resource_id": "a92a6cf2-1adb-4a3f-8b42-ee9a0e2babb3",  # ACARA school profiles
                "limit": 10000,
            }
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            records = resp.json().get("result", {}).get("records", [])
            if records:
                df = pd.DataFrame(records)
                logger.info(f"ACARA: downloaded {len(df)} schools from data.gov.au CKAN")
                return df
        except Exception as e:
            logger.error(f"ACARA CKAN fallback failed: {e}")

        logger.error("ACARA: all download attempts failed")
        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Detect key columns (names vary across ACARA releases)
        col_map = {}
        for col in df.columns:
            lc = col.lower().strip()
            if any(x in lc for x in ["suburb", "town", "locality"]):
                col_map.setdefault("suburb", col)
            elif any(x in lc for x in ["state", "territory"]) and "postcode" not in lc:
                col_map.setdefault("state", col)
            elif "icsea" in lc:
                col_map.setdefault("icsea", col)
            elif "school_type" in lc or "school type" in lc:
                col_map.setdefault("school_type", col)
            elif "school_sector" in lc or "school sector" in lc or "sector" in lc:
                col_map.setdefault("school_sector", col)
            elif "postcode" in lc or "post_code" in lc:
                col_map.setdefault("postcode", col)

        if "suburb" not in col_map or "icsea" not in col_map:
            logger.warning(f"ACARA: could not identify suburb/ICSEA columns. Available: {list(df.columns)[:20]}")
            return pd.DataFrame()

        df = df.copy()

        # Rename to standard names
        df["suburb"] = df[col_map["suburb"]].astype(str).str.strip().str.title()
        df["icsea_score"] = pd.to_numeric(df[col_map["icsea"]], errors="coerce")

        if "state" in col_map:
            df["state"] = df[col_map["state"]].astype(str).str.strip().map(
                lambda x: _STATE_ABBREV.get(x, x)
            )
        else:
            df["state"] = "UNKNOWN"

        if "school_sector" in col_map:
            df["school_sector"] = df[col_map["school_sector"]].astype(str).str.strip()
        else:
            df["school_sector"] = "Unknown"

        df = df.dropna(subset=["suburb", "icsea_score"])
        df = df[df["icsea_score"].between(500, 1300)]  # valid ICSEA range

        # Aggregate to suburb level
        agg = df.groupby(["suburb", "state"]).agg(
            school_icsea_median=("icsea_score", "median"),
            school_icsea_max=("icsea_score", "max"),
            school_count=("icsea_score", "count"),
        ).reset_index()

        # Normalise ICSEA to 0–10 score for use in ML model
        # ICSEA ranges ~500–1300, practical range ~800–1200
        agg["school_quality_score"] = (
            (agg["school_icsea_median"] - 800) / 400 * 10
        ).clip(0, 10).round(2)

        logger.info(f"ACARA: aggregated to {len(agg)} suburbs, ICSEA range "
                    f"{agg['school_icsea_median'].min():.0f}–{agg['school_icsea_median'].max():.0f}")
        return agg
