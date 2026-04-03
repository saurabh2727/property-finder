import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from services.data_fetcher.sa2_concordance import SA2Concordance
from services.data_fetcher.column_schema import (
    SOURCE_SEIFA, SOURCE_ERP, SOURCE_BUILDING, SOURCE_CENSUS,
    SOURCE_NSW_SALES, SOURCE_VIC_SALES, SOURCE_RENTAL_GOV,
    SOURCE_ACARA, SOURCE_DOMAIN_LISTINGS, SOURCE_DOMAIN_RENTAL,
    columns_for_source,
)

logger = logging.getLogger(__name__)

# SA2-keyed enrichment sources and the columns they contribute
# Derived from column_schema.py — single source of truth
_SA2_SOURCES = {
    "seifa":              columns_for_source(SOURCE_SEIFA),
    "census":             columns_for_source(SOURCE_CENSUS),
    "erp":                columns_for_source(SOURCE_ERP),
    "building_approvals": columns_for_source(SOURCE_BUILDING),
}

# Remove sa2_code itself from the enrichment column lists (it's the join key)
_SA2_SOURCES = {k: [c for c in v if c != "sa2_code"] for k, v in _SA2_SOURCES.items()}

# Suburb+State-keyed enrichment sources
_SUBURB_SOURCES = {
    "nsw_sales":        columns_for_source(SOURCE_NSW_SALES),
    "vic_sales":        columns_for_source(SOURCE_VIC_SALES),
    "rental":           columns_for_source(SOURCE_RENTAL_GOV),
    "acara_schools":    columns_for_source(SOURCE_ACARA),
    "domain_listings":  columns_for_source(SOURCE_DOMAIN_LISTINGS),
    "domain_rental_avm": columns_for_source(SOURCE_DOMAIN_RENTAL),
}

# Remove suburb/state from enrichment column lists (they're the join keys)
_SUBURB_SOURCES = {
    k: [c for c in v if c not in ("Suburb", "State", "suburb", "state")]
    for k, v in _SUBURB_SOURCES.items()
}


class DataMerger:
    """
    Joins multiple fetched datasets onto a base suburb DataFrame.

    Join strategy:
    - ABS sources (SEIFA, Census, ERP, Building Approvals): joined on sa2_code
    - Sales and rental sources: joined on Suburb + State

    All joins are LEFT joins — unmatched rows retain NaN for enrichment columns.
    The base DataFrame schema (Suburb, State, Median Price, etc.) is always preserved.
    """

    def __init__(self, concordance: SA2Concordance):
        self.concordance = concordance

    def merge(self,
              base_df: pd.DataFrame,
              fetched: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Merge all available fetched datasets onto base_df.

        Args:
            base_df: The base suburb DataFrame (from file upload or ERP seed).
            fetched: Dict of {source_key: DataFrame} from the fetchers.

        Returns:
            Enriched DataFrame with all available columns added.
        """
        if base_df is None or base_df.empty:
            # Build from ERP as seed if no base
            base_df = self._build_from_erp_seed(fetched)
            if base_df.empty:
                logger.error("DataMerger: no base data available")
                return pd.DataFrame()

        result = base_df.copy()

        # Step 1: Add SA2 codes via concordance
        if "sa2_code" not in result.columns:
            result = self.concordance.enrich_dataframe(result)

        # Step 2: SA2-keyed merges
        for source_key, cols in _SA2_SOURCES.items():
            if source_key not in fetched or fetched[source_key].empty:
                continue
            source_df = fetched[source_key]
            if "sa2_code" not in source_df.columns:
                continue
            available_cols = [c for c in cols if c in source_df.columns]
            if not available_cols:
                continue
            source_df["sa2_code"] = source_df["sa2_code"].astype(str)
            result["sa2_code"] = result["sa2_code"].astype(str)
            result = result.merge(
                source_df[["sa2_code"] + available_cols],
                on="sa2_code",
                how="left",
                suffixes=("", f"_{source_key}"),
            )
            logger.info(f"Merged {source_key}: added {len(available_cols)} columns, "
                        f"coverage={result[available_cols[0]].notna().mean():.0%}")

        # Step 3: Suburb+State-keyed merges
        for source_key, cols in _SUBURB_SOURCES.items():
            if source_key not in fetched or fetched[source_key].empty:
                continue
            source_df = fetched[source_key]
            if "suburb" not in source_df.columns or "state" not in source_df.columns:
                continue

            # Normalise for join
            source_df = source_df.copy()
            source_df["_suburb_key"] = source_df["suburb"].str.strip().str.title()
            source_df["_state_key"] = source_df["state"].str.strip().str.upper()

            result["_suburb_key"] = result.get("Suburb", result.get("suburb", "")).str.strip().str.title()
            result["_state_key"] = result.get("State", result.get("state", "")).str.strip().str.upper()

            available_cols = [c for c in cols if c in source_df.columns]
            if not available_cols:
                continue

            result = result.merge(
                source_df[["_suburb_key", "_state_key"] + available_cols],
                on=["_suburb_key", "_state_key"],
                how="left",
                suffixes=("", f"_{source_key}"),
            )
            logger.info(f"Merged {source_key}: added {len(available_cols)} columns, "
                        f"coverage={result[available_cols[0]].notna().mean():.0%}")

        # Clean up temporary join keys
        result = result.drop(columns=["_suburb_key", "_state_key"], errors="ignore")

        return result

    def _build_from_erp_seed(self, fetched: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Build a base suburb DataFrame from ERP population data when no file was uploaded."""
        if "erp" not in fetched or fetched["erp"].empty:
            return pd.DataFrame()

        erp = fetched["erp"].copy()
        if "sa2_code" not in erp.columns:
            return pd.DataFrame()

        # Use SEIFA sa2_name if available, else just use sa2_code as suburb placeholder
        if "seifa" in fetched and not fetched["seifa"].empty and "sa2_name" in fetched["seifa"].columns:
            seifa_names = fetched["seifa"][["sa2_code", "sa2_name"]].copy()
            seifa_names["sa2_code"] = seifa_names["sa2_code"].astype(str)
            erp["sa2_code"] = erp["sa2_code"].astype(str)
            base = erp.merge(seifa_names, on="sa2_code", how="left")
            base["Suburb"] = base["sa2_name"].fillna(base["sa2_code"])
        else:
            base = erp.copy()
            base["Suburb"] = base["sa2_code"]

        # Derive state from first digit of SA2 code (ABS standard)
        _SA2_STATE_MAP = {
            "1": "NSW", "2": "VIC", "3": "QLD", "4": "SA",
            "5": "WA", "6": "TAS", "7": "NT", "8": "ACT", "9": "OT",
        }
        base["State"] = base["sa2_code"].astype(str).str[0].map(_SA2_STATE_MAP).fillna("N/A")
        base["Median Price"] = None
        base["Rental Yield on Houses"] = None

        logger.info(f"Built ERP seed with {len(base)} SA2 records")
        return base

    def validate_enriched(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Report column coverage after merging."""
        enrichment_cols = (
            [c for cols in _SA2_SOURCES.values() for c in cols] +
            [c for cols in _SUBURB_SOURCES.values() for c in cols]
        )
        present = {c: df[c].notna().mean() for c in enrichment_cols if c in df.columns}
        missing = [c for c in enrichment_cols if c not in df.columns]

        warnings = []
        for col, coverage in present.items():
            if coverage < 0.3:
                warnings.append(f"{col}: only {coverage:.0%} of suburbs have data")

        if "sa2_code" in df.columns:
            sa2_coverage = df["sa2_code"].notna().mean()
            if sa2_coverage < 0.5:
                warnings.append(f"SA2 mapping: only {sa2_coverage:.0%} of suburbs matched to SA2 codes — "
                                 "ABS enrichment will be limited")

        return {
            "total_rows": len(df),
            "column_coverage": {k: f"{v:.0%}" for k, v in present.items()},
            "missing_enrichment_columns": missing,
            "warnings": warnings,
        }

    def get_enrichment_summary(self, fetched: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Returns a list of available source summaries for display in the UI."""
        summary = []
        all_sources = {**{k: list(v) for k, v in _SA2_SOURCES.items()},
                       **{k: list(v) for k, v in _SUBURB_SOURCES.items()}}
        for key, cols in all_sources.items():
            df = fetched.get(key)
            summary.append({
                "source": key,
                "available": df is not None and not df.empty,
                "rows": len(df) if df is not None else 0,
                "columns_provided": cols,
            })
        return summary
