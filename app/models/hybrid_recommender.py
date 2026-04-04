"""
Hybrid Recommendation Engine
=============================
Implements the Suburb Intelligence Layer strategy:

1. SuburbIntelligenceEngine  — pre-compute 7 normalized dimension scores (0–1)
2. Hard filter               — budget + location constraints
3. Mode-based weights        — Home Buyer / Family / Investor / Young Professional
4. Content-based similarity  — cosine sim between user preference vector and suburb vector
5. Hybrid final score        — 0.5 * content_sim + 0.3 * suburb_score + 0.2 * pref_alignment
6. LLM explanations          — via OpenAIService (optional)
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ── Dimension definitions ─────────────────────────────────────────────────────

DIMENSIONS = ['affordability', 'schools', 'crime', 'transport', 'lifestyle', 'employment', 'investment']

DIM_LABELS = {
    'affordability': 'Affordability',
    'schools':       'Schools',
    'crime':         'Safety',
    'transport':     'Transport',
    'lifestyle':     'Lifestyle',
    'employment':    'Employment',
    'investment':    'Investment',
}

# Columns that feed each dimension.
# pos: higher value = better score
# neg: lower value = better score (score is inverted)
DIM_COLUMNS: Dict[str, Dict[str, List[str]]] = {
    'affordability': {
        'pos': [],
        'neg': ['Median Price', 'median_rent_weekly_census', 'median_rent_weekly_actual'],
    },
    'schools': {
        'pos': ['school_quality_score', 'school_icsea_median', 'naplan_mean_score', 'school_count'],
        'neg': [],
    },
    'crime': {
        'pos': [],
        'neg': ['crime_risk_score', 'crime_incidents_per_1000'],
    },
    'transport': {
        'pos': ['transit_score', 'train_station_count', 'bus_stop_count', 'tram_stop_count'],
        'neg': ['Distance (km) to CBD'],
    },
    'lifestyle': {
        'pos': ['amenity_score', 'walkability_score', 'cafe_count', 'park_count',
                'bike_score', 'restaurant_count', 'supermarket_count'],
        'neg': [],
    },
    'employment': {
        'pos': ['employment_score', 'labour_force_participation_rate'],
        'neg': ['unemployment_rate'],
    },
    'investment': {
        'pos': ['seifa_irsad_decile', 'pop_growth_rate_5yr',
                '10 yr Avg. Annual Growth', 'Rental Yield on Houses', 'seifa_irsad_score'],
        'neg': ['flood_risk_score', 'bushfire_risk_score', 'natural_hazard_risk', 'Vacancy Rate'],
    },
}

# ── Mode weights ──────────────────────────────────────────────────────────────

MODE_WEIGHTS: Dict[str, Dict[str, float]] = {
    'Investor - Growth': {
        'affordability': 0.05, 'schools': 0.05, 'crime': 0.10,
        'transport': 0.10,     'lifestyle': 0.05, 'employment': 0.15, 'investment': 0.50,
    },
    'Investor - Yield': {
        'affordability': 0.10, 'schools': 0.05, 'crime': 0.10,
        'transport': 0.10,     'lifestyle': 0.05, 'employment': 0.20, 'investment': 0.40,
    },
    'Home Buyer': {
        'affordability': 0.25, 'schools': 0.20, 'crime': 0.20,
        'transport': 0.15,     'lifestyle': 0.10, 'employment': 0.10, 'investment': 0.00,
    },
    'Family': {
        'affordability': 0.15, 'schools': 0.35, 'crime': 0.25,
        'transport': 0.10,     'lifestyle': 0.10, 'employment': 0.05, 'investment': 0.00,
    },
    'Young Professional': {
        'affordability': 0.20, 'schools': 0.05, 'crime': 0.15,
        'transport': 0.25,     'lifestyle': 0.25, 'employment': 0.10, 'investment': 0.00,
    },
}


def infer_mode(customer_profile: dict) -> str:
    """Infer the best mode from the customer profile fields."""
    purpose = customer_profile.get('investment_goals', {}).get('primary_purpose', '').lower()
    lifestyle = customer_profile.get('lifestyle_factors', {})

    if 'growth' in purpose and 'rental' not in purpose and 'both' not in purpose:
        return 'Investor - Growth'
    if 'rental' in purpose and 'growth' not in purpose and 'both' not in purpose:
        return 'Investor - Yield'
    if 'both' in purpose or ('growth' in purpose and 'rental' in purpose):
        return 'Investor - Growth'

    school = lifestyle.get('school_quality', '').lower()
    if school == 'high':
        return 'Family'

    transport = lifestyle.get('transport_access', '').lower()
    if transport == 'high':
        return 'Young Professional'

    return 'Home Buyer'


# ── Suburb Intelligence Engine ────────────────────────────────────────────────

class SuburbIntelligenceEngine:
    """
    Pre-computes 7 normalized dimension scores (0–1) for every suburb.
    Each dimension draws from multiple source columns; missing columns are
    skipped gracefully so partial data still produces useful scores.
    """

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return df with {dim}_dim_score columns added (0–1 each)."""
        result = df.copy()
        for dim, cols in DIM_COLUMNS.items():
            components = []
            for col in cols.get('pos', []):
                if col in df.columns:
                    s = pd.to_numeric(df[col], errors='coerce')
                    if s.notna().sum() > 1:
                        components.append(self._minmax(s))
            for col in cols.get('neg', []):
                if col in df.columns:
                    s = pd.to_numeric(df[col], errors='coerce')
                    if s.notna().sum() > 1:
                        components.append(1 - self._minmax(s))

            if components:
                dim_score = pd.concat(components, axis=1).mean(axis=1)
                n_used = len(components)
            else:
                dim_score = pd.Series(0.5, index=df.index)
                n_used = 0

            result[f'{dim}_dim_score'] = dim_score.clip(0, 1).fillna(0.5)
            logger.info(f"Dimension '{dim}': {n_used} column(s) used")

        return result

    def coverage(self, df: pd.DataFrame) -> Dict[str, int]:
        """Returns number of data columns available per dimension."""
        return {
            dim: sum(1 for c in cols.get('pos', []) + cols.get('neg', []) if c in df.columns)
            for dim, cols in DIM_COLUMNS.items()
        }

    @staticmethod
    def _minmax(s: pd.Series) -> pd.Series:
        mn, mx = s.min(), s.max()
        if mx == mn:
            return pd.Series(0.5, index=s.index)
        return ((s - mn) / (mx - mn)).fillna(0.5)


# ── Hybrid Recommender ────────────────────────────────────────────────────────

class HybridRecommender:
    """
    Full hybrid pipeline:
      suburb intelligence → hard filter → content similarity → hybrid score → top N
    """

    def __init__(self):
        self.suburb_engine = SuburbIntelligenceEngine()

    # ── Public API ────────────────────────────────────────────────────────────

    def recommend(
        self,
        df: pd.DataFrame,
        customer_profile: dict,
        weights: Optional[Dict[str, float]] = None,
        top_n: int = 10,
    ) -> pd.DataFrame:
        """
        Run the full pipeline. Returns top_n rows sorted by final_score descending.
        Adds columns: {dim}_dim_score, suburb_score, content_similarity,
                      preference_alignment, final_score.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # Step 1: suburb intelligence scores
        scored = self.suburb_engine.compute(df)

        # Step 2: hard filter (budget)
        filtered = self._hard_filter(scored, customer_profile)
        if filtered.empty:
            logger.warning("Hard filter removed all suburbs — using full dataset")
            filtered = scored

        # Step 3: normalize weights
        if weights is None:
            mode = infer_mode(customer_profile)
            weights = dict(MODE_WEIGHTS.get(mode, MODE_WEIGHTS['Home Buyer']))
        total_w = sum(weights.values()) or 1.0
        weights = {k: v / total_w for k, v in weights.items()}

        # Step 4: weighted suburb score (0–1)
        suburb_score = pd.Series(0.0, index=filtered.index)
        for dim, w in weights.items():
            col = f'{dim}_dim_score'
            if col in filtered.columns:
                suburb_score += filtered[col].fillna(0.5) * w

        # Step 5: content-based cosine similarity
        available_dims = [d for d in DIMENSIONS if f'{d}_dim_score' in filtered.columns]
        if len(available_dims) > 1:
            suburb_matrix = filtered[[f'{d}_dim_score' for d in available_dims]].fillna(0.5).values
            user_vec = np.array([weights.get(d, 0.0) for d in available_dims]).reshape(1, -1)
            if user_vec.sum() > 0:
                content_sim = cosine_similarity(suburb_matrix, user_vec).flatten()
            else:
                content_sim = np.full(len(filtered), 0.5)
        else:
            content_sim = np.full(len(filtered), 0.5)

        # Step 6: preference alignment
        pref_align = self._preference_alignment(filtered, customer_profile)

        # Step 7: hybrid final score
        final_score = (
            0.5 * content_sim
            + 0.3 * suburb_score.values
            + 0.2 * pref_align.values
        )

        result = filtered.copy()
        result['suburb_score']         = suburb_score.round(3).values
        result['content_similarity']   = content_sim.round(3)
        result['preference_alignment'] = pref_align.round(3).values
        result['final_score']          = final_score.round(3)

        return result.nlargest(top_n, 'final_score').reset_index(drop=True)

    def dimension_coverage(self, df: pd.DataFrame) -> Dict[str, int]:
        """How many source columns are available per dimension."""
        return self.suburb_engine.coverage(df)

    @staticmethod
    def available_modes() -> List[str]:
        return list(MODE_WEIGHTS.keys())

    @staticmethod
    def weights_for_mode(mode: str) -> Dict[str, float]:
        return dict(MODE_WEIGHTS.get(mode, MODE_WEIGHTS['Home Buyer']))

    # ── Private helpers ───────────────────────────────────────────────────────

    def _hard_filter(self, df: pd.DataFrame, customer_profile: dict) -> pd.DataFrame:
        mask = pd.Series(True, index=df.index)
        price_range = customer_profile.get('property_preferences', {}).get('price_range', {})
        if 'Median Price' in df.columns and price_range.get('min') and price_range.get('max'):
            try:
                lo = float(str(price_range['min']).replace('$', '').replace(',', ''))
                hi = float(str(price_range['max']).replace('$', '').replace(',', ''))
                prices = pd.to_numeric(df['Median Price'], errors='coerce')
                # 20% buffer to avoid over-filtering
                mask &= prices.between(lo * 0.8, hi * 1.2) | prices.isna()
            except (ValueError, TypeError):
                pass
        return df[mask]

    def _preference_alignment(self, df: pd.DataFrame, customer_profile: dict) -> pd.Series:
        scores = pd.Series(0.5, index=df.index, dtype=float)
        price_range = customer_profile.get('property_preferences', {}).get('price_range', {})

        if 'Median Price' in df.columns and price_range.get('min') and price_range.get('max'):
            try:
                lo = float(str(price_range['min']).replace('$', '').replace(',', ''))
                hi = float(str(price_range['max']).replace('$', '').replace(',', ''))
                mid = (lo + hi) / 2
                prices = pd.to_numeric(df['Median Price'], errors='coerce').fillna(mid)
                in_range = prices.between(lo, hi).values
                outside_pct = (prices - mid).abs() / max(hi - lo, 1)
                scores = pd.Series(
                    np.where(in_range, 1.0, np.maximum(0.0, 1.0 - outside_pct.values)),
                    index=df.index,
                )
            except (ValueError, TypeError):
                pass

        # Preferred suburb bonus
        preferred = [
            s.strip().lower()
            for s in customer_profile.get('property_preferences', {}).get('preferred_suburbs', [])
            if s.strip()
        ]
        if preferred and 'Suburb' in df.columns:
            bonus = df['Suburb'].str.lower().isin(preferred).astype(float) * 0.2
            scores = (scores + bonus).clip(0, 1)

        return scores
