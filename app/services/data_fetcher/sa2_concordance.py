import difflib
import io
import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import requests

from utils.data_cache import DataCache

_RAW_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw"

logger = logging.getLogger(__name__)

# ABS ASGS 2021 — SA2 to Suburb/Locality (SAL) correspondence file
# Published by ABS under CC BY 4.0
_CONCORDANCE_URL = (
    "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3"
    "/jul2021-jun2026/access-and-downloads/correspondences/CG_SAL_2021_SA2_2021.csv"
)

# State name → standard abbreviation
_STATE_ABBREV = {
    "new south wales": "NSW", "nsw": "NSW",
    "victoria": "VIC", "vic": "VIC",
    "queensland": "QLD", "qld": "QLD",
    "south australia": "SA", "sa": "SA",
    "western australia": "WA", "wa": "WA",
    "tasmania": "TAS", "tas": "TAS",
    "northern territory": "NT", "nt": "NT",
    "australian capital territory": "ACT", "act": "ACT",
}

# ABS state codes (STE_CODE21) to abbreviation
_STE_CODE_TO_ABBREV = {
    "1": "NSW", "2": "VIC", "3": "QLD", "4": "SA",
    "5": "WA", "6": "TAS", "7": "NT", "8": "ACT",
}


class SA2Concordance:
    """Maps suburb names ↔ SA2 codes using ABS ASGS concordance data."""

    def __init__(self, cache: DataCache):
        self.cache = cache
        self._df: Optional[pd.DataFrame] = None  # columns: sa2_code, sa2_name, suburb, state

    def load(self) -> None:
        if self._df is not None:
            return

        # Try disk cache first
        cached = self.cache.get("sa2_concordance")
        if cached is not None and self.cache.is_fresh("sa2_concordance"):
            self._df = cached
            logger.info(f"SA2 concordance loaded from cache ({len(self._df)} rows)")
            return

        # Try bundled file
        bundled = _RAW_DATA_DIR / "sa2_suburb_concordance.csv"
        if bundled.exists():
            self._df = pd.read_csv(bundled, dtype=str)
            self.cache.set("sa2_concordance", self._df)
            logger.info(f"SA2 concordance loaded from bundled file ({len(self._df)} rows)")
            return

        # Download from ABS
        logger.info("Downloading SA2 concordance from ABS...")
        try:
            resp = requests.get(_CONCORDANCE_URL, timeout=60)
            resp.raise_for_status()
            df = pd.read_csv(io.BytesIO(resp.content), dtype=str)
            self._df = self._process_concordance(df)
            self.cache.set("sa2_concordance", self._df)
            # Also save bundled copy for offline use
            _RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
            self._df.to_csv(bundled, index=False)
            logger.info(f"SA2 concordance downloaded and cached ({len(self._df)} rows)")
        except Exception as e:
            logger.error(f"Failed to load SA2 concordance: {e}")
            self._df = pd.DataFrame(columns=["sa2_code", "sa2_name", "suburb", "state"])

    def _process_concordance(self, df: pd.DataFrame) -> pd.DataFrame:
        # ABS concordance columns vary by file version; handle common patterns
        col_map = {}
        for col in df.columns:
            lc = col.lower()
            if "sa2_code" in lc or lc == "sa2_maincode_2021":
                col_map[col] = "sa2_code"
            elif "sa2_name" in lc:
                col_map[col] = "sa2_name"
            elif "sal_name" in lc or "suburb" in lc or "locality" in lc:
                col_map[col] = "suburb"
            elif "ste_code" in lc or "state_code" in lc:
                col_map[col] = "ste_code"

        df = df.rename(columns=col_map)

        if "ste_code" in df.columns:
            df["state"] = df["ste_code"].map(_STE_CODE_TO_ABBREV)
        elif "state" not in df.columns:
            df["state"] = None

        result = df[["sa2_code", "sa2_name", "suburb", "state"]].dropna(subset=["sa2_code", "suburb"])
        result = result.drop_duplicates(subset=["suburb", "state"])
        return result.reset_index(drop=True)

    def suburb_state_to_sa2(self, suburb: str, state: str) -> Optional[str]:
        if self._df is None or self._df.empty:
            return None

        state_norm = _STATE_ABBREV.get(state.lower().strip(), state.upper().strip())
        suburb_norm = suburb.strip().title()

        # Exact match first
        mask = (self._df["state"] == state_norm) & (self._df["suburb"].str.title() == suburb_norm)
        matches = self._df[mask]
        if not matches.empty:
            return matches.iloc[0]["sa2_code"]

        # Fuzzy match on same state
        state_df = self._df[self._df["state"] == state_norm]
        if state_df.empty:
            return None

        names = state_df["suburb"].str.title().tolist()
        close = difflib.get_close_matches(suburb_norm, names, n=1, cutoff=0.85)
        if close:
            row = state_df[state_df["suburb"].str.title() == close[0]].iloc[0]
            return row["sa2_code"]

        return None

    def enrich_dataframe(self, df: pd.DataFrame,
                         suburb_col: str = "Suburb",
                         state_col: str = "State") -> pd.DataFrame:
        """Add sa2_code column to a DataFrame via suburb+state lookup."""
        if self._df is None:
            self.load()

        df = df.copy()
        if suburb_col not in df.columns or state_col not in df.columns:
            df["sa2_code"] = None
            return df

        df["sa2_code"] = df.apply(
            lambda row: self.suburb_state_to_sa2(
                str(row.get(suburb_col, "")),
                str(row.get(state_col, ""))
            ),
            axis=1
        )

        matched = df["sa2_code"].notna().sum()
        logger.info(f"SA2 concordance: matched {matched}/{len(df)} suburbs")
        return df
