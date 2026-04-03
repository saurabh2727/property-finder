"""
QLD Property Sales Fetcher
==========================
Downloads Queensland property sales data from the QLD Government open data portal.

Source: Queensland Spatial Catalogue / QLD Titles Registry
  - Property sales transactions (suburb-level aggregated)
  - https://www.data.qld.gov.au

Free public data, no API key required.
Cached for 7 days (weekly updates).
"""
import io
import logging
import zipfile

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# QLD Government open data — property sales
_QLD_SALES_URLS = [
    # QLD Spatial Catalogue — property transactions (free download)
    "https://data.qld.gov.au/dataset/property-sales-data/resource/"
    "1fd527f5-d66d-4cd4-81fd-7085de681ef5/download/property-sales-transactions.csv",
    # Fallback: QLD Titles Registry bulk data
    "https://www.titlesqld.com.au/property-data-services/property-data-download/"
    "property-sales-summary.csv",
    # DNRME open data portal
    "https://geoserver.information.qld.gov.au/geoserver/ows?service=WFS&version=1.0.0"
    "&request=GetFeature&typeName=state_prop_sales_qld&outputFormat=csv&maxFeatures=50000",
]

_QLD_SALES_CKAN = {
    "base": "https://data.qld.gov.au/api/3/action/datastore_search",
    "resource_id": "1fd527f5-d66d-4cd4-81fd-7085de681ef5",
    "limit": 50000,
}


class QLDSalesFetcher(BaseFetcher):
    """
    Fetches QLD residential property sales data, aggregated to suburb level.

    Outputs:
      - suburb, state="QLD"
      - qld_median_sale_price: median residential sale price ($)
      - qld_sale_count: number of sales in dataset period
      - qld_median_land_size: median land size (m²) where available
    """

    SOURCE_KEY = "qld_sales"
    CACHE_TTL_HOURS = 168  # 7 days

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        # Try direct CSV downloads first
        for url in _QLD_SALES_URLS:
            try:
                logger.info(f"QLDSalesFetcher: trying {url[:80]}...")
                resp = requests.get(url, timeout=60, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    # Try CSV
                    try:
                        df = pd.read_csv(io.BytesIO(resp.content), dtype=str,
                                        encoding="utf-8", low_memory=False)
                        if len(df) > 100:
                            logger.info(f"QLDSalesFetcher: loaded {len(df)} rows")
                            return df
                    except Exception:
                        pass
                    # Try ZIP
                    try:
                        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                            csvs = [f for f in zf.namelist() if f.endswith(".csv")]
                            if csvs:
                                with zf.open(csvs[0]) as f:
                                    df = pd.read_csv(f, dtype=str, low_memory=False)
                                logger.info(f"QLDSalesFetcher: ZIP loaded {len(df)} rows")
                                return df
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"QLDSalesFetcher: {e}")

        # Try CKAN API
        return self._fetch_ckan()

    def _fetch_ckan(self) -> pd.DataFrame:
        try:
            logger.info("QLDSalesFetcher: trying CKAN API")
            resp = requests.get(
                _QLD_SALES_CKAN["base"],
                params={
                    "resource_id": _QLD_SALES_CKAN["resource_id"],
                    "limit": _QLD_SALES_CKAN["limit"],
                },
                timeout=30,
            )
            resp.raise_for_status()
            records = resp.json().get("result", {}).get("records", [])
            if records:
                df = pd.DataFrame(records)
                logger.info(f"QLDSalesFetcher: CKAN returned {len(df)} records")
                return df
        except Exception as e:
            logger.error(f"QLDSalesFetcher: CKAN failed: {e}")
        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Detect suburb column
        suburb_col = next((c for c in df.columns if any(x in c.lower() for x in
                           ["suburb", "locality", "town"])), None)
        price_col = next((c for c in df.columns if any(x in c.lower() for x in
                          ["price", "sale_price", "contract_price", "amount"])), None)
        land_col = next((c for c in df.columns if any(x in c.lower() for x in
                         ["land", "area", "lot_size"])), None)
        type_col = next((c for c in df.columns if any(x in c.lower() for x in
                         ["type", "property_type", "dwelling"])), None)

        if not suburb_col:
            logger.warning(f"QLDSalesFetcher: no suburb column found. Columns: {list(df.columns)[:15]}")
            return pd.DataFrame()

        df["suburb"] = df[suburb_col].astype(str).str.strip().str.title()
        df["state"] = "QLD"

        # Filter to residential only
        if type_col:
            residential_keywords = ["residential", "house", "unit", "townhouse",
                                     "villa", "flat", "apartment"]
            mask = df[type_col].astype(str).str.lower().str.contains(
                "|".join(residential_keywords), na=False
            )
            df = df[mask | df[type_col].isna()]

        # Parse price
        if price_col:
            df["_price"] = pd.to_numeric(
                df[price_col].astype(str).str.replace(r"[$,]", "", regex=True),
                errors="coerce"
            )
            # Filter out non-arm's-length sales (< $50k or > $50M)
            df = df[(df["_price"] >= 50000) & (df["_price"] <= 50_000_000)]

        # Parse land size
        if land_col:
            df["_land"] = pd.to_numeric(df[land_col], errors="coerce")

        # Aggregate to suburb level
        agg_dict = {"_price": ["median", "count"]}
        if land_col:
            agg_dict["_land"] = "median"

        agg = df.groupby(["suburb", "state"]).agg(agg_dict).reset_index()
        agg.columns = ["suburb", "state"] + [
            "qld_median_sale_price", "qld_sale_count"
        ] + (["qld_median_land_size"] if land_col else [])

        agg["qld_median_sale_price"] = agg["qld_median_sale_price"].round(0)

        # Filter suburbs with at least 3 sales for statistical reliability
        agg = agg[agg["qld_sale_count"] >= 3]

        logger.info(f"QLDSalesFetcher: {len(agg)} QLD suburbs with sales data")
        return agg
