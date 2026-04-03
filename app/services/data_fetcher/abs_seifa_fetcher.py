import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

_FEATURE_SERVER_URL = (
    "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services"
    "/ABS_Socio_Economic_Indexes_for_Areas_SEIFA_by_2021_SA2/FeatureServer/0/query"
)

# Actual field names from the ArcGIS service (verified)
_OUT_FIELDS = ",".join([
    "sa2_code_2021", "sa2_name_2021",
    "irsd_score", "irsd_aus_decile",
    "irsad_score", "irsad_aus_decile",
    "ieo_score", "ieo_aus_decile",
    "ier_score", "ier_aus_decile",
])


class ABSSEIFAFetcher(BaseFetcher):
    """Fetches SEIFA 2021 socio-economic indexes per SA2 from ABS ArcGIS REST API."""

    SOURCE_KEY = "abs_seifa_2021"
    PAGE_SIZE = 2000

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        records = []
        offset = 0

        while True:
            params = {
                "where": "1=1",
                "outFields": _OUT_FIELDS,
                "f": "json",
                "resultRecordCount": self.PAGE_SIZE,
                "resultOffset": offset,
            }
            resp = requests.get(_FEATURE_SERVER_URL, params=params, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            features = data.get("features", [])
            if not features:
                break

            records.extend(f["attributes"] for f in features)
            offset += self.PAGE_SIZE

            # ArcGIS returns exceededTransferLimit when there are more pages
            if not data.get("exceededTransferLimit", False) and len(features) < self.PAGE_SIZE:
                break

        logger.info(f"SEIFA: fetched {len(records)} SA2 records")
        return pd.DataFrame(records)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns={
            "sa2_code_2021": "sa2_code",
            "sa2_name_2021": "sa2_name",
            "irsd_score": "seifa_irsd_score",
            "irsd_aus_decile": "seifa_irsd_decile",
            "irsad_score": "seifa_irsad_score",
            "irsad_aus_decile": "seifa_irsad_decile",
            "ieo_score": "seifa_ieo_score",
            "ieo_aus_decile": "seifa_ieo_decile",
            "ier_score": "seifa_ier_score",
            "ier_aus_decile": "seifa_ier_decile",
        })
        df["sa2_code"] = df["sa2_code"].astype(str).str.zfill(9)

        numeric_cols = [c for c in df.columns if c.startswith("seifa_")]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        return df[["sa2_code", "sa2_name"] + numeric_cols].drop_duplicates(subset=["sa2_code"])
