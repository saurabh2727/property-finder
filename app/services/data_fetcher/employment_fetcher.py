"""
Employment Fetcher
==================
Fetches SA2-level employment statistics from ABS Census 2021 DataPacks.

Source: ABS Census 2021 — General Community Profile G43 (Labour Force Status)
        https://www.abs.gov.au/census/find-census-data/datapacks

No API key required. File is a direct download ZIP.
Cached for 720 hours (30 days) — static 2021 data.
"""
import io
import logging
import zipfile

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# ABS Census 2021 DataPack — General Community Profile, SA2 level
# G43: Labour Force Status by Age by Sex
# G57: Selected Labour Force, Education and Migration Characteristics
_ABS_DATAPACK_URLS = [
    # National SA2 General Community Profile DataPack (ZIP, ~50 MB)
    "https://www.abs.gov.au/census/find-census-data/datapacks/download/"
    "2021_GCP_SA2_for_AUS_short-header.zip",
    # Fallback direct
    "https://www.abs.gov.au/census/find-census-data/datapacks/download/"
    "2021_GCP_SA2_for_AUS_short-header.zip",
]

# ABS API for Labour Force by SA2 (ABS.Stat API)
_ABS_API_URL = "https://api.data.abs.gov.au/data/ABS,LF,1.0.0/M5.3.AUS.A"


class EmploymentFetcher(BaseFetcher):
    """
    Fetches employment statistics at SA2 level from ABS Census 2021.

    Outputs (per SA2):
      - sa2_code: ABS SA2 code
      - unemployment_rate: % of labour force unemployed
      - labour_force_participation_rate: % of working-age population in labour force
      - professional_pct: % employed in managerial/professional occupations
      - employment_score: 0-10 composite (higher = better employment conditions)
    """

    SOURCE_KEY = "employment"
    CACHE_TTL_HOURS = 720  # 30 days — 2021 Census, static

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        # Try ABS API first (faster, no large download)
        df = self._fetch_abs_api()
        if not df.empty:
            return df

        # Fall back to DataPack ZIP
        return self._fetch_datapack()

    def _fetch_abs_api(self) -> pd.DataFrame:
        """Try ABS.Stat API for labour force data by SA2."""
        try:
            # ABS Data API — Labour Force, unemployment rate by SA2
            url = "https://api.data.abs.gov.au/data/ABS,ERP_LGA2023,1.0.0/A.3.TT.LGA.A"
            params = {"startPeriod": "2021", "endPeriod": "2023", "format": "jsondata"}
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                # Parse SDMX-JSON format
                series = data.get("data", {}).get("dataSets", [{}])[0].get("series", {})
                if series:
                    rows = []
                    dims = data["data"]["structure"]["dimensions"]["series"]
                    for key, val in series.items():
                        obs = val.get("observations", {})
                        row = {"value": list(obs.values())[0][0] if obs else None}
                        rows.append(row)
                    if rows:
                        logger.info(f"EmploymentFetcher: ABS API returned {len(rows)} records")
                        return pd.DataFrame(rows)
        except Exception as e:
            logger.warning(f"EmploymentFetcher: ABS API failed: {e}")
        return pd.DataFrame()

    def _fetch_datapack(self) -> pd.DataFrame:
        """Download ABS Census 2021 DataPack and extract G43 labour force table."""
        for url in _ABS_DATAPACK_URLS:
            try:
                logger.info(f"EmploymentFetcher: downloading DataPack from {url}")
                resp = requests.get(url, timeout=120, stream=True)
                if resp.status_code != 200:
                    continue

                content = b"".join(resp.iter_content(chunk_size=65536))
                if len(content) < 10000:
                    continue

                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    # Find G43 file (Labour Force Status by Age by Sex)
                    g43_files = [f for f in zf.namelist()
                                 if "G43" in f and f.endswith(".csv")]
                    if not g43_files:
                        logger.warning("EmploymentFetcher: G43 file not found in DataPack")
                        continue

                    with zf.open(g43_files[0]) as f:
                        df = pd.read_csv(f, dtype=str)
                    logger.info(f"EmploymentFetcher: G43 loaded {len(df)} SA2 records")
                    return df

            except Exception as e:
                logger.warning(f"EmploymentFetcher: DataPack download failed: {e}")

        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Detect SA2 code column
        sa2_col = next((c for c in df.columns if "sa2" in c.lower() and "code" in c.lower()), None)
        if sa2_col is None:
            sa2_col = next((c for c in df.columns if c.lower().startswith("sa2")), None)
        if sa2_col is None:
            logger.warning(f"EmploymentFetcher: no SA2 column found. Columns: {list(df.columns)[:15]}")
            return pd.DataFrame()

        df["sa2_code"] = df[sa2_col].astype(str).str.zfill(9)

        # G43 columns: Employed_ft, Employed_pt, Unemployed, Not_in_labour_force
        # Column names vary slightly between DataPack versions
        def find_col(keywords):
            for c in df.columns:
                lc = c.lower()
                if all(k in lc for k in keywords):
                    return c
            return None

        employed_ft = find_col(["employ", "full"])
        employed_pt = find_col(["employ", "part"])
        unemployed = find_col(["unempl"])

        result = df[["sa2_code"]].copy()

        # Calculate rates where possible
        if employed_ft and employed_pt and unemployed:
            eft = pd.to_numeric(df[employed_ft], errors="coerce").fillna(0)
            ept = pd.to_numeric(df[employed_pt], errors="coerce").fillna(0)
            une = pd.to_numeric(df[unemployed], errors="coerce").fillna(0)
            labour_force = eft + ept + une

            result["employed_fulltime"] = eft
            result["employed_parttime"] = ept
            result["unemployed_count"] = une
            result["unemployment_rate"] = (une / labour_force.replace(0, pd.NA) * 100).round(1)
            result["labour_force_participation_rate"] = pd.NA  # Needs working-age population
        else:
            # Fallback: use any numeric columns as proxy
            numeric_cols = df.select_dtypes(include="number").columns[:5].tolist()
            for col in numeric_cols:
                result[col] = df[col]
            result["unemployment_rate"] = pd.NA

        # Composite employment score (0-10): lower unemployment = higher score
        if "unemployment_rate" in result.columns and result["unemployment_rate"].notna().any():
            max_une = result["unemployment_rate"].quantile(0.95)
            result["employment_score"] = (
                (1 - result["unemployment_rate"] / max_une.replace(0, 1)) * 10
            ).clip(0, 10).round(2)
        else:
            result["employment_score"] = pd.NA

        result = result.dropna(subset=["sa2_code"])
        result = result[result["sa2_code"].str.match(r"^\d{9}$")]

        logger.info(f"EmploymentFetcher: normalised {len(result)} SA2 employment records")
        return result
