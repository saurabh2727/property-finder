import io
import logging
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

_RAW_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw"

# Expected ZIP file placed by user in data/raw/
# Download from: https://www.abs.gov.au/census/find-census-data/datapacks
# Select: 2021, General Community Profile, SA2, All of Australia
_DATAPACK_ZIP = _RAW_DATA_DIR / "abs_census_2021_gcp_sa2.zip"

# Tables to extract and their key columns
_TABLE_CONFIG = {
    "G02": {
        "pattern": "2021Census_G02_AUST_SA2.csv",
        "columns": {
            "SA2_CODE_2021": "sa2_code",
            "Median_age_persons": "median_age",
            "Median_mortgage_repay_monthly": "median_mortgage_monthly",
            "Median_rent_weekly": "median_rent_weekly_census",
            "Median_tot_prsnl_inc_weekly": "median_personal_income_weekly",
            "Median_tot_hhd_inc_weekly": "median_household_income_weekly",
            "Average_household_size": "avg_household_size",
        }
    },
    "G37": {
        "pattern": "2021Census_G37_AUST_SA2.csv",
        "columns": {
            "SA2_CODE_2021": "sa2_code",
            "O_OR_OS_Tot": "owner_occupied_dwellings",
            "Rented_Tot": "rented_dwellings",
            "Tot_dwell": "total_dwellings_g37",
        }
    },
    "G56": {
        "pattern": "2021Census_G56_AUST_SA2.csv",
        "columns": {
            "SA2_CODE_2021": "sa2_code",
            "Sep_house_Tot": "separate_houses",
            "Semi_det_Tot": "semi_detached_dwellings",
            "Flat_apt_Tot": "flat_apartment_dwellings",
            "Total_Tot": "total_dwellings_g56",
        }
    },
}


class ABSCensusFetcher(BaseFetcher):
    """
    Reads ABS Census 2021 General Community Profile DataPack.

    Requires the user to download the DataPack ZIP and place it at:
        data/raw/abs_census_2021_gcp_sa2.zip

    Download from:
        https://www.abs.gov.au/census/find-census-data/datapacks
        → 2021 → General Community Profile → SA2 → All of Australia
    """

    SOURCE_KEY = "abs_census_2021"

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    @property
    def datapack_available(self) -> bool:
        return _DATAPACK_ZIP.exists()

    def _fetch_raw(self) -> pd.DataFrame:
        if not _DATAPACK_ZIP.exists():
            raise FileNotFoundError(
                f"ABS Census 2021 DataPack not found at {_DATAPACK_ZIP}.\n"
                "Download from https://www.abs.gov.au/census/find-census-data/datapacks\n"
                "Select: 2021 → General Community Profile → SA2 → All of Australia\n"
                f"Save the ZIP file as: {_DATAPACK_ZIP}"
            )

        frames = {}
        with zipfile.ZipFile(_DATAPACK_ZIP) as zf:
            namelist = zf.namelist()
            for table_id, config in _TABLE_CONFIG.items():
                matched = [n for n in namelist if config["pattern"] in n]
                if not matched:
                    logger.warning(f"Census table {table_id} not found in ZIP (pattern: {config['pattern']})")
                    continue
                with zf.open(matched[0]) as f:
                    df = pd.read_csv(f, dtype={"SA2_CODE_2021": str})
                    frames[table_id] = df
                    logger.info(f"Loaded census table {table_id}: {len(df)} rows")

        if not frames:
            return pd.DataFrame()

        # Start merge from G02
        base_table = list(frames.keys())[0]
        result = frames[base_table]
        for table_id, df in list(frames.items())[1:]:
            if "SA2_CODE_2021" in df.columns:
                result = result.merge(df, on="SA2_CODE_2021", how="left", suffixes=("", f"_{table_id}"))

        return result

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Collect all column renames across tables
        rename_map = {}
        for config in _TABLE_CONFIG.values():
            rename_map.update(config["columns"])

        # Only rename columns that exist
        actual_rename = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(columns=actual_rename)

        df["sa2_code"] = df["sa2_code"].astype(str).str.zfill(9)

        # Numeric conversion
        numeric_cols = [c for c in df.columns if c != "sa2_code"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        # Derived ratios
        if "owner_occupied_dwellings" in df.columns and "total_dwellings_g37" in df.columns:
            df["owner_occupied_pct"] = (
                df["owner_occupied_dwellings"] / df["total_dwellings_g37"].replace(0, pd.NA) * 100
            ).round(1)

        if "rented_dwellings" in df.columns and "total_dwellings_g37" in df.columns:
            df["rented_pct"] = (
                df["rented_dwellings"] / df["total_dwellings_g37"].replace(0, pd.NA) * 100
            ).round(1)

        keep_cols = ["sa2_code"] + [v for config in _TABLE_CONFIG.values() for v in config["columns"].values() if v != "sa2_code"]
        keep_cols += ["owner_occupied_pct", "rented_pct"]
        keep_cols = [c for c in keep_cols if c in df.columns]

        return df[keep_cols].drop_duplicates(subset=["sa2_code"])
