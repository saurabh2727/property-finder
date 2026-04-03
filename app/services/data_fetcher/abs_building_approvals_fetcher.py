import logging

import pandas as pd

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# ABS does not expose building approvals at SA2 level via any public API.
# The BUILDING_ACTIVITY dataflow (api.data.abs.gov.au) only goes down to state level.
# SA2-level building approvals are published in the ABS Building Approvals release
# but only as manual downloads, not machine-readable API endpoints.
# This fetcher returns an empty DataFrame so the pipeline degrades gracefully.


class ABSBuildingApprovalsFetcher(BaseFetcher):
    """Stub fetcher — SA2-level building approvals not available via ABS API."""

    SOURCE_KEY = "abs_building_approvals"

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        logger.warning(
            "SA2-level building approvals are not available via the ABS public API. "
            "Skipping this source — total_approvals_12m will be NaN for all suburbs."
        )
        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        # Return correctly-typed empty frame so merger doesn't fail on column checks
        return pd.DataFrame(columns=["sa2_code", "total_approvals_12m", "avg_monthly_approvals"])
