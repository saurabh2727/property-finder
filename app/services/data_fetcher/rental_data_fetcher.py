import io
import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# NSW Fair Trading — Rental Bond Lodgements (monthly XLSX, postcode-level)
# URL confirmed working April 2026. Contains: postcode, dwelling type, weekly rent, bedrooms.
_NSW_RENTAL_BASE = "https://www.nsw.gov.au/sites/default/files/noindex"
_NSW_RENTAL_URLS = [
    f"{_NSW_RENTAL_BASE}/2026-03/rentalbond_lodgements_february_2026.xlsx",
    f"{_NSW_RENTAL_BASE}/2026-02/rentalbond_lodgements_january_2026.xlsx",
    f"{_NSW_RENTAL_BASE}/2025-12/rentalbond_lodgements_november_2025.xlsx",
]

# NSW postcode → suburb mapping (ABS postcode correspondence file)
_NSW_POSTCODE_URL = (
    "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3"
    "/jul2021-jun2026/access-and-downloads/correspondences/CG_POA_2021_SAL_2021.csv"
)

# Victoria — Moving Annual Rents by LGA (quarterly, DFFH)
# Resource ID confirmed working April 2026
_VIC_RENTAL_CKAN = "https://discover.data.vic.gov.au/api/3/action/datastore_search"
_VIC_RENTAL_RESOURCE = "ca75f2c7-0c61-4189-bdf2-3e38fd8bd5b7"  # LGA-level, Sep 2025


class RentalDataFetcher(BaseFetcher):
    """Fetches rental price data from NSW and VIC government sources."""

    SOURCE_KEY = "rental_data"

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        frames = []

        nsw_df = self._fetch_nsw_rental()
        if nsw_df is not None and not nsw_df.empty:
            frames.append(nsw_df)

        vic_df = self._fetch_vic_rental()
        if vic_df is not None and not vic_df.empty:
            frames.append(vic_df)

        if not frames:
            logger.warning("Rental data: no data fetched from any source")
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def _fetch_nsw_rental(self) -> pd.DataFrame:
        for url in _NSW_RENTAL_URLS:
            try:
                logger.info(f"RentalDataFetcher: trying NSW {url}")
                resp = requests.get(url, timeout=30, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    df = pd.read_excel(io.BytesIO(resp.content), dtype=str)
                    df["state"] = "NSW"
                    logger.info(f"NSW rental: loaded {len(df)} rows from {url}")
                    return df
            except Exception as e:
                logger.warning(f"NSW rental {url}: {e}")
        logger.warning("RentalDataFetcher: all NSW URLs failed")
        return pd.DataFrame()

    def _fetch_vic_rental(self) -> pd.DataFrame:
        try:
            params = {"resource_id": _VIC_RENTAL_RESOURCE, "limit": 50000}
            resp = requests.get(_VIC_RENTAL_CKAN, params=params, timeout=30)
            resp.raise_for_status()
            records = resp.json().get("result", {}).get("records", [])
            if records:
                df = pd.DataFrame(records)
                df["state"] = "VIC"
                logger.info(f"VIC rental: downloaded {len(df)} rows")
                return df
        except Exception as e:
            logger.warning(f"VIC rental data: {e}")
        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Detect suburb and rent columns
        suburb_col = next((c for c in df.columns if "suburb" in c.lower() or "locality" in c.lower()), None)
        rent_col = next(
            (c for c in df.columns if "median" in c.lower() and "rent" in c.lower()),
            next((c for c in df.columns if "rent" in c.lower() and "week" in c.lower()), None)
        )
        state_col = "state" if "state" in df.columns else None

        if not suburb_col or not rent_col:
            logger.warning(f"Rental data: cannot identify suburb/rent columns. Available: {list(df.columns)}")
            return pd.DataFrame()

        keep = [suburb_col, rent_col]
        if state_col:
            keep.append(state_col)

        result = df[keep].copy()
        result.columns = ["suburb", "median_rent_weekly_actual"] + (["state"] if state_col else [])
        if "state" not in result.columns:
            result["state"] = "UNKNOWN"

        result["suburb"] = result["suburb"].astype(str).str.strip().str.title()
        result["median_rent_weekly_actual"] = (
            result["median_rent_weekly_actual"]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .str.strip()
        )
        result["median_rent_weekly_actual"] = pd.to_numeric(result["median_rent_weekly_actual"], errors="coerce")
        result = result.dropna(subset=["suburb", "median_rent_weekly_actual"])
        result = result[result["median_rent_weekly_actual"] > 50]

        # Latest value per suburb/state
        agg = result.groupby(["suburb", "state"]).agg(
            median_rent_weekly_actual=("median_rent_weekly_actual", "median")
        ).reset_index()

        logger.info(f"Rental data: normalised to {len(agg)} suburb records")
        return agg
