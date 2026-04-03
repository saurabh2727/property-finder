import logging
from typing import List, Optional

import pandas as pd
import requests

from services.data_fetcher.base_fetcher import BaseFetcher
from utils.data_cache import DataCache

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.domain.com.au"

# Free endpoints (Sandbox tier — 500 calls/day, no charge)
_LISTINGS_SEARCH_URL = f"{_BASE_URL}/v1/listings/residential/_search"

# Rental AVM API — unlimited calls, request access required
_RENTAL_AVM_URL = f"{_BASE_URL}/v2/properties/{{property_id}}/rentalEstimate"

# Suburb performance statistics (part of Properties & Locations — paid,
# but a subset is available via the listings search aggregation)
_SUBURB_PERFORMANCE_URL = (
    f"{_BASE_URL}/v1/suburbPerformanceStatistics/{{state}}/{{suburb}}/{{postcode}}"
    "?propertyCategory=house&chronologicalSpan=3&tPricePercentile=50"
)

_AU_STATES = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]


class DomainListingsFetcher(BaseFetcher):
    """
    Fetches current residential listings per suburb using Domain Listings Management
    sandbox (free tier — 500 calls/day).

    Aggregates to suburb level: median list price, listing count, median bedrooms.
    """

    SOURCE_KEY = "domain_listings"
    CACHE_TTL_HOURS = 4  # listings change frequently

    def __init__(self, cache: DataCache, api_key: str, suburbs: Optional[List[dict]] = None):
        """
        Args:
            api_key: Domain developer API key (free registration at developer.domain.com.au)
            suburbs: List of {"suburb": str, "state": str} dicts to query.
                     If None, fetches nothing (must call fetch_for_suburbs directly).
        """
        super().__init__(cache)
        self.api_key = api_key
        self.suburbs = suburbs or []

    def _headers(self) -> dict:
        return {"X-Api-Key": self.api_key, "Content-Type": "application/json"}

    def _fetch_raw(self) -> pd.DataFrame:
        if not self.api_key:
            raise ValueError(
                "Domain API key required. Register free at https://developer.domain.com.au"
            )
        if not self.suburbs:
            logger.warning("DomainListingsFetcher: no suburbs specified — returning empty")
            return pd.DataFrame()

        return self._fetch_listings_for_suburbs(self.suburbs)

    def _fetch_listings_for_suburbs(self, suburbs: List[dict]) -> pd.DataFrame:
        """Fetch listings for a list of suburb dicts, respecting 500 call/day limit."""
        all_records = []
        calls_made = 0
        max_calls = 450  # stay under 500/day limit with buffer

        for entry in suburbs:
            if calls_made >= max_calls:
                logger.warning(f"Domain: reached {max_calls} call limit, stopping")
                break

            suburb = entry.get("suburb", "")
            state = entry.get("state", "")
            if not suburb or not state:
                continue

            payload = {
                "listingType": "Sale",
                "propertyTypes": ["House", "ApartmentUnitFlat", "Townhouse"],
                "locations": [{"state": state, "suburb": suburb}],
                "pageSize": 50,
                "sort": {"sortKey": "Default", "direction": "Descending"},
            }

            try:
                resp = requests.post(
                    _LISTINGS_SEARCH_URL,
                    json=payload,
                    headers=self._headers(),
                    timeout=15,
                )
                calls_made += 1

                if resp.status_code == 200:
                    for item in resp.json():
                        listing = item.get("listing", {})
                        price = listing.get("priceDetails", {})
                        prop = listing.get("propertyDetails", {})
                        all_records.append({
                            "suburb": suburb,
                            "state": state,
                            "listing_id": listing.get("id"),
                            "list_price": price.get("price") or price.get("displayPrice"),
                            "bedrooms": prop.get("bedrooms"),
                            "bathrooms": prop.get("bathrooms"),
                            "parking": prop.get("carspaces"),
                            "property_type": prop.get("propertyType"),
                            "land_area": prop.get("landArea"),
                        })
                elif resp.status_code == 403:
                    logger.warning("Domain API: access denied — check API key and sandbox permissions")
                    break

            except Exception as e:
                logger.warning(f"Domain listings failed for {suburb} {state}: {e}")

        logger.info(f"Domain listings: {len(all_records)} listings fetched in {calls_made} API calls")
        return pd.DataFrame(all_records)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df["list_price"] = pd.to_numeric(df["list_price"], errors="coerce")
        df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce")
        df = df.dropna(subset=["suburb", "list_price"])
        df = df[df["list_price"] > 100000]

        agg = df.groupby(["suburb", "state"]).agg(
            domain_median_list_price=("list_price", "median"),
            domain_listing_count=("list_price", "count"),
            domain_median_bedrooms=("bedrooms", "median"),
        ).reset_index()

        agg["domain_median_list_price"] = agg["domain_median_list_price"].round(0).astype(int)
        logger.info(f"Domain listings: normalised to {len(agg)} suburbs")
        return agg


class DomainRentalAVMFetcher(BaseFetcher):
    """
    Fetches rental estimates using Domain Rental AVM API (free, unlimited calls).

    Queries rental estimates for a list of property IDs or addresses, then
    aggregates to suburb-level median weekly rent.

    Note: Rental AVM requires a valid Domain property ID. To get IDs for a suburb
    we first search listings, then query AVM per property.
    """

    SOURCE_KEY = "domain_rental_avm"
    CACHE_TTL_HOURS = 24

    def __init__(self, cache: DataCache, api_key: str, property_ids: Optional[List[str]] = None):
        super().__init__(cache)
        self.api_key = api_key
        self.property_ids = property_ids or []

    def _headers(self) -> dict:
        return {"X-Api-Key": self.api_key, "Accept": "application/json"}

    def get_rental_estimate(self, property_id: str) -> Optional[dict]:
        """Get rental estimate for a single property ID."""
        if not self.api_key:
            raise ValueError("Domain API key required")

        url = _RENTAL_AVM_URL.format(property_id=property_id)
        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "property_id": property_id,
                    "rental_estimate_lower": data.get("lowerPrice"),
                    "rental_estimate_upper": data.get("upperPrice"),
                    "rental_estimate_mid": data.get("midPrice") or (
                        (data.get("lowerPrice", 0) + data.get("upperPrice", 0)) / 2
                        if data.get("lowerPrice") and data.get("upperPrice") else None
                    ),
                    "confidence": data.get("confidence"),
                }
        except Exception as e:
            logger.warning(f"Rental AVM failed for property {property_id}: {e}")
        return None

    def fetch_rental_estimates_for_suburbs(
        self,
        suburb_listing_df: pd.DataFrame,
        max_per_suburb: int = 10,
    ) -> pd.DataFrame:
        """
        Given a DataFrame with listing_id, suburb, state columns,
        fetches rental AVM for up to max_per_suburb listings per suburb
        and aggregates to suburb-level median weekly rent.
        """
        if suburb_listing_df.empty or "listing_id" not in suburb_listing_df.columns:
            return pd.DataFrame()

        records = []
        for _, group in suburb_listing_df.groupby(["suburb", "state"]):
            suburb = group["suburb"].iloc[0]
            state = group["state"].iloc[0]
            sample = group["listing_id"].dropna().head(max_per_suburb)

            estimates = []
            for pid in sample:
                result = self.get_rental_estimate(str(pid))
                if result and result.get("rental_estimate_mid"):
                    estimates.append(result["rental_estimate_mid"])

            if estimates:
                records.append({
                    "suburb": suburb,
                    "state": state,
                    "domain_median_rental_estimate": pd.Series(estimates).median(),
                    "domain_rental_sample_size": len(estimates),
                })

        logger.info(f"Rental AVM: got estimates for {len(records)} suburbs")
        return pd.DataFrame(records)

    def _fetch_raw(self) -> pd.DataFrame:
        if not self.property_ids:
            return pd.DataFrame()
        records = []
        for pid in self.property_ids:
            result = self.get_rental_estimate(pid)
            if result:
                records.append(result)
        return pd.DataFrame(records)

    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
