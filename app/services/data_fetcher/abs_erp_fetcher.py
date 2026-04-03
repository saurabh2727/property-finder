import logging
from typing import Dict, List

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# ABS Data API — Estimated Resident Population by SA2
# Dataflow: ABS_ANNUAL_ERP_ASGS2021
# Key structure: MEASURE.REGION_TYPE.ASGS_2021.FREQ
# ERP = population measure, SA2 = geography type, + = all SA2 codes, A = annual
_BASE_URL = "https://api.data.abs.gov.au/data/ABS_ANNUAL_ERP_ASGS2021"


class ABSERPFetcher(BaseFetcher):
    """Fetches Estimated Resident Population by SA2 from ABS Data API."""

    SOURCE_KEY = "abs_erp"

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        # Correct key: MEASURE=ERP, REGION_TYPE=SA2, ASGS_2021=all (+), FREQ=Annual
        url = f"{_BASE_URL}/ERP.SA2.+.A"
        headers = {"Accept": "application/vnd.sdmx.data+json;version=1.0"}
        # Fetch 6 years to compute 5yr growth rate
        params = {"startPeriod": "2018", "endPeriod": "2023"}

        resp = requests.get(url, headers=headers, params=params, timeout=120)
        resp.raise_for_status()

        return self._parse_sdmx_json(resp.json())

    def _parse_sdmx_json(self, data: dict) -> pd.DataFrame:
        structure = data["data"]["structure"]
        datasets = data["data"]["dataSets"]

        if not datasets:
            return pd.DataFrame()

        # Dimension order: MEASURE(0), REGION_TYPE(1), ASGS_2021(2), FREQ(3)
        series_dims = structure["dimensions"]["series"]
        obs_dims = structure["dimensions"]["observation"]

        # Build position-to-id lookup for each dimension
        series_id_map = [
            {i: v["id"] for i, v in enumerate(d["values"])}
            for d in series_dims
        ]
        obs_id_map = [
            {i: v["id"] for i, v in enumerate(d["values"])}
            for d in obs_dims
        ]

        records = []
        for series_key, series_data in datasets[0]["series"].items():
            parts = [int(p) for p in series_key.split(":")]
            # SA2 code is at dimension index 2 (ASGS_2021)
            sa2_code = series_id_map[2].get(parts[2], "") if len(series_id_map) > 2 else ""

            for obs_key, obs_value in series_data.get("observations", {}).items():
                year_id = int(obs_key)
                year = obs_id_map[0].get(year_id, "") if obs_id_map else ""
                value = obs_value[0] if obs_value else None
                records.append({
                    "sa2_code": sa2_code,
                    "year": year,
                    "population": value,
                })

        return pd.DataFrame(records)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df["sa2_code"] = df["sa2_code"].astype(str).str.zfill(9)
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df["population"] = pd.to_numeric(df["population"], errors="coerce")
        df = df.dropna(subset=["sa2_code", "year", "population"])

        # Latest year per SA2
        latest = df.sort_values("year").groupby("sa2_code").last().reset_index()
        latest = latest.rename(columns={"population": "erp_population", "year": "erp_year"})

        # 5-year CAGR per SA2
        growth_records = []
        for sa2, grp in df.groupby("sa2_code"):
            grp = grp.sort_values("year")
            if len(grp) >= 5:
                old_pop = grp.iloc[-5]["population"]
                new_pop = grp.iloc[-1]["population"]
                if old_pop and old_pop > 0:
                    cagr = ((new_pop / old_pop) ** (1 / 5) - 1) * 100
                    growth_records.append({"sa2_code": sa2, "pop_growth_rate_5yr": round(cagr, 2)})

        growth_df = (
            pd.DataFrame(growth_records)
            if growth_records
            else pd.DataFrame(columns=["sa2_code", "pop_growth_rate_5yr"])
        )

        result = latest[["sa2_code", "erp_population", "erp_year"]].merge(
            growth_df, on="sa2_code", how="left"
        )
        return result
