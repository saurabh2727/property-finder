import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_DEFAULT_CACHE_DIR = _PROJECT_ROOT / "data" / "processed" / "api_cache"


class DataCache:
    """Disk-backed cache for fetched API data using Parquet format."""

    CACHE_DIR = _DEFAULT_CACHE_DIR

    # Default TTL per source key (hours)
    DEFAULT_TTL = {
        "abs_seifa_2021": 720,          # 30 days — static annual release
        "abs_census_2021": 720,         # 30 days — static release
        "abs_erp": 168,                 # 7 days — quarterly updates
        "abs_building_approvals": 168,
        "nsw_vg_sales": 168,
        "vic_sales": 168,
        "qld_sales": 168,               # 7 days
        "rental_data": 168,
        "domain_listings": 1,           # 1 hour — live listings
        "sa2_concordance": 2160,        # 90 days — near-static
        # New sources
        "acara_schools": 720,           # 30 days — annual ACARA release
        "amenities": 720,               # 30 days — OSM data
        "transport": 720,               # 30 days — OSM data
        "healthcare": 720,              # 30 days — OSM + AIHW
        "crime": 720,                   # 30 days — annual releases
        "employment": 720,              # 30 days — 2021 Census, static
        "flood_risk": 2160,             # 90 days — near-static hazard data
        "walkability": 720,             # 30 days — OSM data
    }

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _parquet_path(self, key: str) -> Path:
        return self.CACHE_DIR / f"{key}.parquet"

    def _meta_path(self, key: str) -> Path:
        return self.CACHE_DIR / f"{key}.meta.json"

    def is_fresh(self, key: str, max_age_hours: Optional[int] = None) -> bool:
        meta_path = self._meta_path(key)
        parquet_path = self._parquet_path(key)

        if not meta_path.exists() or not parquet_path.exists():
            return False

        try:
            with open(meta_path) as f:
                meta = json.load(f)
            fetched_at = datetime.fromisoformat(meta["fetched_at"])
            ttl = max_age_hours or self.DEFAULT_TTL.get(key, 24)
            return datetime.now() - fetched_at < timedelta(hours=ttl)
        except Exception:
            return False

    def get(self, key: str) -> Optional[pd.DataFrame]:
        path = self._parquet_path(key)
        if not path.exists():
            return None
        try:
            return pd.read_parquet(path)
        except Exception as e:
            logger.warning(f"Cache read failed for {key}: {e}")
            return None

    def set(self, key: str, df: pd.DataFrame, source_url: str = "") -> None:
        try:
            df.to_parquet(self._parquet_path(key), index=False)
            meta = {
                "fetched_at": datetime.now().isoformat(),
                "source_url": source_url,
                "row_count": len(df),
                "columns": list(df.columns),
            }
            with open(self._meta_path(key), "w") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            logger.error(f"Cache write failed for {key}: {e}")

    def invalidate(self, key: str) -> None:
        for path in [self._parquet_path(key), self._meta_path(key)]:
            if path.exists():
                path.unlink()

    def list_cached(self) -> List[Dict[str, Any]]:
        entries = []
        for meta_file in self.CACHE_DIR.glob("*.meta.json"):
            key = meta_file.stem.replace(".meta", "")
            try:
                with open(meta_file) as f:
                    meta = json.load(f)
                fetched_at = datetime.fromisoformat(meta["fetched_at"])
                age_hours = (datetime.now() - fetched_at).total_seconds() / 3600
                ttl = self.DEFAULT_TTL.get(key, 24)
                entries.append({
                    "key": key,
                    "fetched_at": fetched_at.strftime("%Y-%m-%d %H:%M"),
                    "age_hours": round(age_hours, 1),
                    "ttl_hours": ttl,
                    "fresh": age_hours < ttl,
                    "row_count": meta.get("row_count", "?"),
                })
            except Exception:
                continue
        return entries
