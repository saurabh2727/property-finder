"""
ACARA Schools Fetcher
=====================
Fetches two ACARA datasets and produces suburb-level school quality metrics:

1. School Profile 2025 — ICSEA scores, school sector, school type, enrolments
2. NAPLAN National Results 2025 — mean Reading + Numeracy scores per school

Both are free downloads from the ACARA Data Access Program under CC BY 4.0.

Output columns per suburb:
  school_quality_score   — 0–10 composite (ICSEA + NAPLAN, equally weighted)
  school_icsea_median    — median ICSEA across all schools in suburb
  naplan_mean_score      — mean NAPLAN score (Reading + Numeracy avg, all year levels)
  school_count           — total number of schools
  primary_count          — number of primary schools
  secondary_count        — number of secondary/combined schools
  pct_independent        — % of schools that are Independent/Private
  pct_catholic           — % of schools that are Catholic
  pct_government         — % of schools that are Government
  has_secondary          — True if suburb has at least one secondary/combined school
"""
import io
import logging

import numpy as np
import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# ── Download URLs ─────────────────────────────────────────────────────────────

_PROFILE_URLS = [
    "https://dataandreporting.blob.core.windows.net/anrdataportal/Data-Access-Program/School%20Profile%202025.xlsx",
    "https://dataandreporting.blob.core.windows.net/anrdataportal/Data-Access-Program/School%20Profile%202008-2025.xlsx",
]

_NAPLAN_URLS = [
    "https://dataandreporting.blob.core.windows.net/anrdataportal/ANR-ExcelDownloads/2025NAP_Draft/NAPLAN%20national%20results%20dataset.xlsx",
]

_STATE_ABBREV = {
    "New South Wales": "NSW", "Victoria": "VIC", "Queensland": "QLD",
    "South Australia": "SA", "Western Australia": "WA", "Tasmania": "TAS",
    "Northern Territory": "NT", "Australian Capital Territory": "ACT",
    "NSW": "NSW", "VIC": "VIC", "QLD": "QLD", "SA": "SA",
    "WA": "WA", "TAS": "TAS", "NT": "NT", "ACT": "ACT",
}

# Keywords used for flexible column detection
# Confirmed column names from School Profile 2025 (inspected April 2026)
# Flexible keywords kept as fallback for future releases
_SUBURB_KEYWORDS   = ["suburb", "town", "locality", "location"]
_STATE_KEYWORDS    = ["state", "territory"]
_ICSEA_KEYWORDS    = ["icsea"]
_SECTOR_KEYWORDS   = ["sector"]
_TYPE_KEYWORDS     = ["school type", "school_type", "type"]
_SCHOOL_KEYWORDS   = ["school name", "school_name", "schoolname"]
_READING_KEYWORDS  = ["reading", "read"]
_NUMERACY_KEYWORDS = ["numeracy", "numer"]
_YEAR_KEYWORDS     = ["year level", "year_level", "cohort", "grade"]

# Exact column names from School Profile 2025 — used as priority lookup before keyword search
_EXACT_COLS = {
    "suburb":  "Suburb",
    "state":   "State",
    "icsea":   "ICSEA",
    "sector":  "School Sector",
    "type":    "School Type",
    "school":  "School Name",
}


def _download_excel(urls: list, label: str) -> pd.DataFrame:
    """Download the first working Excel file from a list of URLs."""
    for url in urls:
        try:
            logger.info(f"{label}: trying {url}")
            resp = requests.get(url, timeout=90, allow_redirects=True)
            logger.info(f"{label}: HTTP {resp.status_code}, "
                        f"size={len(resp.content):,}, "
                        f"type={resp.headers.get('content-type', '?')[:60]}")
            if resp.status_code != 200:
                continue
            if len(resp.content) < 10_000:
                logger.warning(f"{label}: response too small — likely an error page")
                continue
            if "html" in resp.headers.get("content-type", "").lower():
                logger.warning(f"{label}: got HTML instead of Excel")
                continue
            xl = pd.ExcelFile(io.BytesIO(resp.content))
            logger.info(f"{label}: sheets = {xl.sheet_names}")
            # Skip cover/dictionary sheets — pick first sheet with actual school data
            data_sheet = next(
                (s for s in xl.sheet_names
                 if any(x in s.lower() for x in ["profile", "school", "naplan", "result"])
                 and not any(x in s.lower() for x in ["dictionary", "filter", "cover"])),
                xl.sheet_names[-1]
            )
            logger.info(f"{label}: reading sheet '{data_sheet}'")
            df = xl.parse(data_sheet, dtype=str)
            logger.info(f"{label}: loaded {len(df):,} rows — columns: {list(df.columns[:15])}")
            return df
        except Exception as e:
            logger.warning(f"{label}: failed ({url}): {e}")
    logger.error(f"{label}: all URLs failed")
    return pd.DataFrame()


def _find_col(df: pd.DataFrame, keywords: list) -> str | None:
    """Return the first column whose lowercase name contains any keyword."""
    for col in df.columns:
        lc = col.lower().strip()
        if any(k in lc for k in keywords):
            return col
    return None


def _find_col_exclude(df: pd.DataFrame, keywords: list, exclude: list) -> str | None:
    """Like _find_col but skip columns that also contain any exclude keyword."""
    for col in df.columns:
        lc = col.lower().strip()
        if any(k in lc for k in keywords) and not any(e in lc for e in exclude):
            return col
    return None


class ACARASchoolsFetcher(BaseFetcher):
    """
    Fetches ACARA School Profile + NAPLAN results and aggregates to suburb level.

    Final output columns — see module docstring for full descriptions.
    """

    SOURCE_KEY = "acara_schools"
    CACHE_TTL_HOURS = 720  # 30 days — annual release

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    # ── Public entry point ────────────────────────────────────────────────────

    def _fetch_raw(self) -> pd.DataFrame:
        profile_df = _download_excel(_PROFILE_URLS, "ACARA Profile")
        naplan_df  = _download_excel(_NAPLAN_URLS,  "ACARA NAPLAN")
        # Store both so _normalise can work with them together
        self._naplan_raw = naplan_df
        return profile_df

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        profile = self._parse_profile(df)
        naplan  = self._parse_naplan(getattr(self, "_naplan_raw", pd.DataFrame()))

        if profile.empty:
            logger.error("ACARA: school profile parse failed — no output")
            return pd.DataFrame()

        # Join NAPLAN onto profile at school level, then aggregate to suburb
        if not naplan.empty:
            profile = profile.merge(naplan, on="_school_key", how="left")
            logger.info(f"ACARA: joined NAPLAN to profile — "
                        f"{profile['naplan_mean_score'].notna().sum():,} schools matched")
        else:
            profile["naplan_mean_score"] = np.nan
            logger.warning("ACARA: NAPLAN data unavailable — naplan_mean_score will be NaN")

        return self._aggregate_to_suburb(profile)

    # ── Profile parser ────────────────────────────────────────────────────────

    def _parse_profile(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()

        # Try exact known column names first, fall back to keyword search
        def _col(exact_key, keywords, exclude=None):
            exact = _EXACT_COLS.get(exact_key)
            if exact and exact in df.columns:
                return exact
            return (_find_col_exclude(df, keywords, exclude or [])
                    if exclude else _find_col(df, keywords))

        suburb_col  = _col("suburb", _SUBURB_KEYWORDS)
        state_col   = _col("state",  _STATE_KEYWORDS, exclude=["postcode", "name"])
        icsea_col   = _col("icsea",  _ICSEA_KEYWORDS)
        sector_col  = _col("sector", _SECTOR_KEYWORDS)
        type_col    = _col("type",   _TYPE_KEYWORDS)
        school_col  = _col("school", _SCHOOL_KEYWORDS)

        logger.info(f"ACARA Profile cols → suburb={suburb_col}, state={state_col}, "
                    f"icsea={icsea_col}, sector={sector_col}, type={type_col}, "
                    f"school={school_col}")

        # ICSEA fallback: find by value range (500–1300)
        if not icsea_col:
            for col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(vals) > 100 and vals.between(500, 1300).mean() > 0.6:
                    icsea_col = col
                    logger.info(f"ACARA Profile: ICSEA detected by range in '{col}'")
                    break

        # Suburb fallback: title-case text column
        if not suburb_col:
            for col in df.columns:
                sample = df[col].dropna().astype(str).head(30)
                if sample.str.istitle().mean() > 0.5 and sample.str.len().mean() < 35:
                    suburb_col = col
                    logger.info(f"ACARA Profile: suburb detected by text pattern in '{col}'")
                    break

        if not suburb_col or not icsea_col:
            logger.warning(f"ACARA Profile: cannot identify key columns. "
                           f"Available: {list(df.columns[:30])}")
            return pd.DataFrame()

        result = pd.DataFrame()
        result["suburb"]       = df[suburb_col].astype(str).str.strip().str.title()
        result["icsea_score"]  = pd.to_numeric(df[icsea_col], errors="coerce")
        result["state"]        = (
            df[state_col].astype(str).str.strip().map(lambda x: _STATE_ABBREV.get(x, x))
            if state_col else "UNKNOWN"
        )
        result["school_sector"] = (
            df[sector_col].astype(str).str.strip().str.title()
            if sector_col else "Unknown"
        )
        result["school_type"] = (
            df[type_col].astype(str).str.strip().str.lower()
            if type_col else "unknown"
        )
        result["_school_key"] = (
            df[school_col].astype(str).str.strip().str.lower() + "|" + result["state"].str.lower()
            if school_col else result["suburb"].str.lower() + "|" + result["state"].str.lower()
        )

        result = result.dropna(subset=["suburb", "icsea_score"])
        result = result[result["icsea_score"].between(500, 1300)]
        logger.info(f"ACARA Profile: {len(result):,} valid school rows")
        return result

    # ── NAPLAN parser ─────────────────────────────────────────────────────────

    def _parse_naplan(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()

        df = df.copy()

        school_col   = _find_col(df, _SCHOOL_KEYWORDS)
        state_col    = _find_col_exclude(df, _STATE_KEYWORDS, ["postcode", "name"])
        reading_col  = _find_col(df, _READING_KEYWORDS)
        numeracy_col = _find_col(df, _NUMERACY_KEYWORDS)

        logger.info(f"ACARA NAPLAN cols → school={school_col}, state={state_col}, "
                    f"reading={reading_col}, numeracy={numeracy_col}")

        if not school_col:
            logger.warning("ACARA NAPLAN: no school name column found")
            return pd.DataFrame()

        scores = pd.DataFrame()
        scores["_school_key"] = (
            df[school_col].astype(str).str.strip().str.lower() + "|" +
            (df[state_col].astype(str).str.strip().str.lower() if state_col else "")
        )

        if reading_col:
            scores["reading"] = pd.to_numeric(df[reading_col], errors="coerce")
        if numeracy_col:
            scores["numeracy"] = pd.to_numeric(df[numeracy_col], errors="coerce")

        # Average Reading and Numeracy — these are the two most predictive signals
        score_cols = [c for c in ["reading", "numeracy"] if c in scores.columns]
        if not score_cols:
            logger.warning("ACARA NAPLAN: no Reading or Numeracy score columns found")
            return pd.DataFrame()

        scores["naplan_mean_score"] = scores[score_cols].mean(axis=1)

        # Aggregate to school level (file may have one row per year level)
        agg = (
            scores.groupby("_school_key")
            .agg(naplan_mean_score=("naplan_mean_score", "mean"))
            .reset_index()
        )
        agg["naplan_mean_score"] = agg["naplan_mean_score"].round(1)
        logger.info(f"ACARA NAPLAN: {len(agg):,} schools with NAPLAN scores")
        return agg

    # ── Suburb aggregation ────────────────────────────────────────────────────

    def _aggregate_to_suburb(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        result_rows = []

        for (suburb, state), grp in df.groupby(["suburb", "state"]):
            n = len(grp)
            sector = grp["school_sector"].str.lower()
            stype  = grp["school_type"].str.lower()

            # School type counts
            is_secondary = stype.str.contains("secondary|high|senior|combined|k-12", na=False)
            is_primary   = stype.str.contains("primary|infants|prep|junior", na=False)

            # Sector breakdown
            is_independent = sector.str.contains("independent|private", na=False)
            is_catholic    = sector.str.contains("catholic", na=False)
            is_government  = sector.str.contains("government|public|state", na=False)

            icsea_vals = grp["icsea_score"].dropna()
            naplan_vals = grp["naplan_mean_score"].dropna() if "naplan_mean_score" in grp.columns else pd.Series(dtype=float)

            icsea_median = icsea_vals.median() if len(icsea_vals) else np.nan
            naplan_mean  = naplan_vals.mean()  if len(naplan_vals) else np.nan

            # ICSEA → 0–10 (practical range 800–1200)
            icsea_score_norm = float(np.clip((icsea_median - 800) / 400 * 10, 0, 10)) if not np.isnan(icsea_median) else np.nan

            # NAPLAN → 0–10 (typical range 270–570, mean ~400)
            naplan_score_norm = float(np.clip((naplan_mean - 270) / 300 * 10, 0, 10)) if not np.isnan(naplan_mean) else np.nan

            # Composite school quality score — equal weight ICSEA + NAPLAN
            # If only one is available, use it alone
            available = [s for s in [icsea_score_norm, naplan_score_norm] if not (s is None or np.isnan(s))]
            quality_score = float(np.mean(available)) if available else np.nan

            result_rows.append({
                "suburb":               suburb,
                "state":                state,
                "school_quality_score": round(quality_score, 2) if not np.isnan(quality_score) else None,
                "school_icsea_median":  round(icsea_median, 1)  if not np.isnan(icsea_median)  else None,
                "naplan_mean_score":    round(naplan_mean, 1)   if not np.isnan(naplan_mean)   else None,
                "school_count":         n,
                "primary_count":        int(is_primary.sum()),
                "secondary_count":      int(is_secondary.sum()),
                "pct_independent":      round(is_independent.mean() * 100, 1),
                "pct_catholic":         round(is_catholic.mean() * 100, 1),
                "pct_government":       round(is_government.mean() * 100, 1),
                "has_secondary":        bool(is_secondary.any()),
            })

        agg = pd.DataFrame(result_rows)
        logger.info(
            f"ACARA: aggregated to {len(agg):,} suburbs — "
            f"quality range {agg['school_quality_score'].min():.1f}–{agg['school_quality_score'].max():.1f}, "
            f"NAPLAN coverage {agg['naplan_mean_score'].notna().mean():.0%}"
        )
        return agg
