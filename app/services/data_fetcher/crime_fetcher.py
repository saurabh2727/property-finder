"""
Crime Fetcher
=============
Downloads LGA-level crime data for NSW and VIC from open government sources.

Sources:
- NSW: Bureau of Crime Statistics and Research (BOCSAR) — LGA Annual data
- VIC: Crime Statistics Agency — LGA data
- Other states: placeholder (data not freely available in bulk)

No API key required. Cached for 30 days.
"""
import io
import logging

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# NSW BOCSAR — New South Wales state-wide LGA annual crime data
# All LGAs in one file. URL confirmed working April 2026.
_NSW_BOCSAR_URLS = [
    "https://bocsar.nsw.gov.au/content/dam/dcj/bocsar/documents/publications/lga/NewSouthWales.xlsx",
    "https://bocsar.nsw.gov.au/content/dam/dcj/bocsar/documents/publications/lga/GreaterSydney.xlsx",
]

# VIC Crime Statistics Agency — LGA recorded offences (annual)
# https://www.crimestatistics.vic.gov.au/crime-statistics/downloads
_VIC_CRIME_URLS = [
    "https://files.crimestatistics.vic.gov.au/2024-06/Data_Tables_LGA_Recorded_Offences_Year_Ending_March_2024.xlsx",
    "https://files.crimestatistics.vic.gov.au/2024-03/Data_Tables_LGA_Recorded_Offences_Year_Ending_December_2023.xlsx",
]

# ABS Population estimates for normalisation (ERP LGA-level)
_ABS_LGA_POP_URL = (
    "https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/"
    "latest-release"  # Not a direct download; will use a fallback
)


class CrimeFetcher(BaseFetcher):
    """
    Fetches LGA-level crime statistics for NSW and VIC.

    Outputs (per suburb/LGA):
      - crime_incidents_per_1000: total recorded offences per 1,000 population
      - crime_risk_score: 0-10 (lower = safer), normalised nationally
      - property_crime_rate: property-specific offences per 1,000
    """

    SOURCE_KEY = "crime"
    CACHE_TTL_HOURS = 720  # 30 days

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        frames = []

        nsw = self._fetch_nsw()
        if not nsw.empty:
            frames.append(nsw)

        vic = self._fetch_vic()
        if not vic.empty:
            frames.append(vic)

        if not frames:
            logger.error("CrimeFetcher: all sources failed")
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def _fetch_nsw(self) -> pd.DataFrame:
        for url in _NSW_BOCSAR_URLS:
            try:
                logger.info(f"CrimeFetcher: downloading NSW BOCSAR from {url}")
                resp = requests.get(url, timeout=60, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    xl = pd.ExcelFile(io.BytesIO(resp.content))
                    # BOCSAR files: find the sheet with "LGA" or "Offence" data
                    sheet = next(
                        (s for s in xl.sheet_names if any(x in s.lower() for x in ["lga", "offence", "total"])),
                        xl.sheet_names[0]
                    )
                    df = xl.parse(sheet, dtype=str, header=None)
                    # Find the actual header row (first row where first cell looks like "LGA")
                    header_row = 0
                    for i, row in df.iterrows():
                        if any(str(v).lower() in ("lga", "local government area", "area") for v in row.values):
                            header_row = i
                            break
                    df.columns = df.iloc[header_row]
                    df = df.iloc[header_row + 1:].reset_index(drop=True)
                    df["state"] = "NSW"
                    logger.info(f"CrimeFetcher: NSW BOCSAR loaded {len(df)} rows from '{sheet}'")
                    return df
            except Exception as e:
                logger.warning(f"CrimeFetcher: NSW {url} failed: {e}")
        return pd.DataFrame()

    def _fetch_vic(self) -> pd.DataFrame:
        for url in _VIC_CRIME_URLS:
            try:
                logger.info(f"CrimeFetcher: downloading VIC Crime Stats from {url}")
                resp = requests.get(url, timeout=60, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    xl = pd.ExcelFile(io.BytesIO(resp.content))
                    sheet = next(
                        (s for s in xl.sheet_names if any(x in s.lower() for x in ["lga", "offence", "table"])),
                        xl.sheet_names[0]
                    )
                    df = xl.parse(sheet, dtype=str)
                    df["state"] = "VIC"
                    logger.info(f"CrimeFetcher: VIC loaded {len(df)} rows from '{sheet}'")
                    return df
            except Exception as e:
                logger.warning(f"CrimeFetcher: VIC {url} failed: {e}")
        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Detect LGA/suburb column
        lga_col = next((c for c in df.columns if any(x in c.lower() for x in
                        ["lga", "local government", "suburb", "area"])), None)
        if not lga_col:
            logger.warning(f"CrimeFetcher: cannot find LGA column. Columns: {list(df.columns)[:15]}")
            return pd.DataFrame()

        df["suburb"] = df[lga_col].astype(str).str.strip().str.title()

        # Detect total offences column
        offence_col = next((c for c in df.columns if any(x in c.lower() for x in
                            ["total", "offence", "incident", "count"])), None)
        population_col = next((c for c in df.columns if "population" in c.lower()), None)

        if offence_col:
            df["total_offences"] = pd.to_numeric(df[offence_col], errors="coerce")
        else:
            # Sum numeric columns as total offences
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                df["total_offences"] = df[numeric_cols].sum(axis=1)
            else:
                df["total_offences"] = 0

        if population_col:
            df["lga_population"] = pd.to_numeric(df[population_col], errors="coerce")
            df["crime_incidents_per_1000"] = (
                df["total_offences"] / df["lga_population"].replace(0, pd.NA) * 1000
            ).round(1)
        else:
            # Can't normalise by population without population data
            df["crime_incidents_per_1000"] = pd.NA

        # Property crime: look for property-related offence columns
        property_cols = [c for c in df.columns if any(x in c.lower() for x in
                         ["theft", "break", "property", "burglary", "robbery"])]
        if property_cols:
            df["property_offences"] = df[property_cols].apply(
                pd.to_numeric, errors="coerce"
            ).sum(axis=1)
        else:
            df["property_offences"] = pd.NA

        result = df[["suburb", "state", "total_offences",
                     "crime_incidents_per_1000"]].copy()
        if "property_offences" in df.columns:
            result["property_offences"] = df["property_offences"]

        result = result.dropna(subset=["suburb"])
        result = result[result["suburb"].str.len() > 1]

        # Normalise crime risk score (0-10, lower = safer)
        if result["crime_incidents_per_1000"].notna().any():
            max_rate = result["crime_incidents_per_1000"].quantile(0.95)
            result["crime_risk_score"] = (
                result["crime_incidents_per_1000"] / max_rate * 10
            ).clip(0, 10).round(2)
        else:
            result["crime_risk_score"] = pd.NA

        logger.info(f"CrimeFetcher: normalised {len(result)} LGA records")
        return result
