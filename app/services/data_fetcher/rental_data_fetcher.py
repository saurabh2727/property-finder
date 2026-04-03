import io
import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# NSW Fair Trading — Rental Bond Data (quarterly XLSX)
# https://www.nsw.gov.au/housing-and-construction/rental-forms-surveys-and-data/rental-bond-data
_NSW_RENTAL_URL = (
    "https://www.fairtrading.nsw.gov.au/about-fair-trading/data-and-research"
    "/rental-bond-data/rental-bond-board-data-tables"
)

# Victoria DFFH — Moving Annual Rents by Suburb (quarterly CSV)
# https://discover.data.vic.gov.au/dataset/rental-report-quarterly-moving-annual-rents-by-suburb
_VIC_RENTAL_CKAN = "https://discover.data.vic.gov.au/api/3/action/datastore_search"
_VIC_RENTAL_RESOURCE = "e9e6fa72-3279-49a9-827d-34e7e3e21b91"  # verify on portal


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
        # NSW Fair Trading provides data as XLSX; the exact URL changes each quarter.
        # We attempt a predictable URL pattern and fall back gracefully.
        from datetime import datetime
        year = datetime.now().year
        quarter = (datetime.now().month - 1) // 3 + 1
        # Try current and previous quarter
        for q in [quarter, quarter - 1 if quarter > 1 else 4]:
            y = year if q == quarter else (year if quarter > 1 else year - 1)
            url = (
                f"https://www.fairtrading.nsw.gov.au/content/dam/public-service-corporate"
                f"/fair-trading/documents/data/rental-bond-board/rbb-data-{y}-q{q}.xlsx"
            )
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    df = pd.read_excel(io.BytesIO(resp.content), dtype=str)
                    df["state"] = "NSW"
                    logger.info(f"NSW rental: downloaded {len(df)} rows for {y} Q{q}")
                    return df
            except Exception:
                continue
        logger.warning("NSW rental data: could not download")
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
