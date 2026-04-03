import logging

import pandas as pd

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

# NSW Valuer General bulk property sales endpoint returns HTTP 500 as of 2026.
# The download portal at valuation.property.nsw.gov.au/embed/propeye requires
# a browser session and is not available via direct HTTP GET.
#
# Alternative: download manually from
#   https://www.valuergeneral.nsw.gov.au/land_values/property_sales_information
# and upload the CSV/ZIP via the Data Import page.


class NSWSalesFetcher(BaseFetcher):
    """Stub — NSW VG bulk download not available via API. Returns empty gracefully."""

    SOURCE_KEY = "nsw_vg_sales"

    def __init__(self, cache: DataCache):
        super().__init__(cache)

    def _fetch_raw(self) -> pd.DataFrame:
        logger.warning(
            "NSW Valuer General bulk sales endpoint is unavailable programmatically "
            "(returns HTTP 500). Upload a CSV manually from "
            "https://www.valuergeneral.nsw.gov.au/land_values/property_sales_information"
        )
        return pd.DataFrame()

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(columns=["suburb", "state", "nsw_median_sale_price", "nsw_sale_count"])
