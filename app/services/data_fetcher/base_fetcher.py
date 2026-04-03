import logging
from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from utils.data_cache import DataCache


class BaseFetcher(ABC):
    """Abstract base class for all external data fetchers."""

    SOURCE_KEY: str = ""
    CACHE_TTL_HOURS: Optional[int] = None  # None → use DataCache default

    def __init__(self, cache: DataCache):
        self.cache = cache
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, force_refresh: bool = False) -> pd.DataFrame:
        """Return cached data if fresh, otherwise fetch and cache."""
        if not force_refresh and self.cache.is_fresh(self.SOURCE_KEY, self.CACHE_TTL_HOURS):
            df = self.cache.get(self.SOURCE_KEY)
            if df is not None:
                self.logger.info(f"Cache hit for {self.SOURCE_KEY} ({len(df)} rows)")
                return df

        self.logger.info(f"Fetching fresh data for {self.SOURCE_KEY}")
        df = self._fetch_raw()
        df = self._normalise(df)
        self.cache.set(self.SOURCE_KEY, df)
        self.logger.info(f"Cached {len(df)} rows for {self.SOURCE_KEY}")
        return df

    @abstractmethod
    def _fetch_raw(self) -> pd.DataFrame:
        """Download/read data from source. Returns unnormalised DataFrame."""

    @abstractmethod
    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardise column names and types. Must include sa2_code or suburb+state."""
