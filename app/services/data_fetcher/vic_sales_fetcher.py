import io
import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# Victorian Land and Property — median house prices by suburb
# Primary: land.vic.gov.au XLSX (Cloudflare-protected, returns 403 on direct download)
# Fallback: data.vic.gov.au CKAN datastore
_VIC_CKAN_SEARCH = "https://discover.data.vic.gov.au/api/3/action/package_show"
_VIC_DATASET_ID = "victorian-property-sales-report-median-house-by-suburb-time-series"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.land.vic.gov.au/",
    "Accept": "application/octet-stream,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class VICSalesFetcher(BaseFetcher):
    """Fetches Victoria median house prices by suburb from land.vic.gov.au."""

    SOURCE_KEY = "vic_sales"

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        # Step 1: discover current file URL via CKAN (URL changes with each release)
        xlsx_url = self._discover_url()
        if not xlsx_url:
            logger.warning("VIC sales: could not discover download URL from data portal")
            return pd.DataFrame()

        # Step 2: download XLSX
        try:
            resp = requests.get(xlsx_url, headers=_HEADERS, timeout=60, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 5000:
                logger.info(f"VIC sales: downloaded {len(resp.content)/1024:.0f} KB from {xlsx_url}")
                return pd.read_excel(io.BytesIO(resp.content), sheet_name=0, dtype=str)
            else:
                logger.warning(f"VIC sales: download returned {resp.status_code} from {xlsx_url}")
        except Exception as e:
            logger.warning(f"VIC sales: download failed — {e}")

        return pd.DataFrame()

    def _discover_url(self) -> str:
        """Query CKAN to get the current XLSX download URL (changes with each release)."""
        try:
            r = requests.get(
                _VIC_CKAN_SEARCH,
                params={"id": _VIC_DATASET_ID},
                timeout=15,
            )
            if r.status_code == 200 and r.json().get("success"):
                for res in r.json()["result"]["resources"]:
                    if res.get("format", "").upper() in ("XLSX", "XLS"):
                        return res["url"]
        except Exception as e:
            logger.warning(f"VIC sales CKAN discovery failed: {e}")
        return ""

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["suburb", "state", "vic_median_sale_price"])

        # The file is wide-format: rows = suburbs, columns = quarters
        # First column = suburb name, last non-empty column = most recent quarter price
        suburb_col = df.columns[0]
        # Find the last column with mostly numeric-ish data
        price_col = None
        for col in reversed(df.columns[1:]):
            vals = df[col].dropna()
            numeric = pd.to_numeric(
                vals.astype(str).str.replace(r"[$,]", "", regex=True).str.strip(),
                errors="coerce"
            ).dropna()
            if len(numeric) > len(df) * 0.3:  # at least 30% valid
                price_col = col
                break

        if not price_col:
            logger.warning("VIC sales: could not identify price column")
            return pd.DataFrame(columns=["suburb", "state", "vic_median_sale_price"])

        result = df[[suburb_col, price_col]].copy()
        result.columns = ["suburb", "vic_median_sale_price"]
        result["suburb"] = result["suburb"].astype(str).str.strip().str.title()
        result["vic_median_sale_price"] = (
            result["vic_median_sale_price"]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .str.strip()
        )
        result["vic_median_sale_price"] = pd.to_numeric(result["vic_median_sale_price"], errors="coerce")
        result = result.dropna(subset=["suburb", "vic_median_sale_price"])
        result = result[result["vic_median_sale_price"] > 50000]
        result["state"] = "VIC"

        result = (
            result.groupby(["suburb", "state"])
            .agg(vic_median_sale_price=("vic_median_sale_price", "last"))
            .reset_index()
        )
        logger.info(f"VIC sales: normalised to {len(result)} suburbs")
        return result
