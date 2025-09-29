import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class EnhancedScoringEngine:
    """
    Enhanced Scoring Engine following the exact 10-step flow:
    Separate Growth, Yield, and Risk scores with composite Overall Suburb Score
    """

    def __init__(self):
        self.models = {
            'growth': None,
            'yield': None,
            'risk': None
        }
        self.scalers = {
            'growth': StandardScaler(),
            'yield': StandardScaler(),
            'risk': StandardScaler()
        }
        self.feature_columns = {
            'growth': [],
            'yield': [],
            'risk': []
        }
        self.is_trained = False
        self.feature_importance_log = {}

    def prepare_features(self, df, customer_profile):
        """Step 4: Feature Assembly - Clean/standardise and create composite features"""

        if df is None or df.empty:
            return pd.DataFrame()

        df_features = df.copy()

        # Clean and standardize fields
        self._standardize_fields(df_features)

        # Create composite features
        self._create_composite_features(df_features)

        # Normalize by state/region
        self._normalize_by_region(df_features)

        # Add customer-specific features
        self._add_customer_features(df_features, customer_profile)

        return df_features

    def _standardize_fields(self, df):
        """Clean and standardize field names and values"""

        # Standardize suburb names
        if 'Suburb' in df.columns:
            df['Suburb'] = df['Suburb'].astype(str).str.strip().str.title()

        # Handle missing values with intelligent defaults
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                # Use median for most metrics, 0 for growth rates
                if 'growth' in col.lower() or 'change' in col.lower():
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df[col].median())

    def _create_composite_features(self, df):
        """Create composite features as per your requirements"""

        # Affordability Index
        if 'Median Price' in df.columns and 'Median weekly household income' in df.columns:
            annual_income = df['Median weekly household income'] * 52
            df['Affordability_Index'] = annual_income / (df['Median Price'] + 1)

        # Demand/Supply Pressure
        if 'Potential Buyers Demand' in df.columns and 'Total For Sale Listings' in df.columns:
            df['Demand_Supply_Pressure'] = df['Potential Buyers Demand'] / (df['Total For Sale Listings'] + 1)

        # Investment Attractiveness (combines yield and growth)
        if 'Rental Yield on Houses' in df.columns and '10 yr Avg. Annual Growth' in df.columns:
            df['Investment_Attractiveness'] = (
                df['Rental Yield on Houses'] * 0.4 +
                df['10 yr Avg. Annual Growth'] * 0.6
            )

        # Market Momentum (recent activity)
        if 'Sales Days on Market' in df.columns and 'Stock on Market Percentage (SOM%)' in df.columns:
            # Lower DoM and lower SOM% = higher momentum
            df['Market_Momentum'] = 1 / ((df['Sales Days on Market'] / 30 + 1) * (df['Stock on Market Percentage (SOM%)'] / 100 + 1))

        # Demographic Strength
        if 'Population' in df.columns and 'More than $3000 gross weekly income' in df.columns:
            df['Demographic_Strength'] = np.log1p(df['Population']) * (df['More than $3000 gross weekly income'] / 100)

    def _normalize_by_region(self, df):
        """Normalize metrics by state/region to avoid city-size bias"""

        if 'State' not in df.columns:
            return

        # Metrics to normalize by state
        normalize_cols = [
            'Median Price', 'Rental Yield on Houses', 'Population',
            'Distance (km) to CBD', 'Sales Days on Market'
        ]

        for col in normalize_cols:
            if col in df.columns:
                # Create normalized version (z-score within state)
                df[f'{col}_State_Normalized'] = df.groupby('State')[col].transform(
                    lambda x: (x - x.mean()) / (x.std() + 1e-6)
                )

    def _add_customer_features(self, df, customer_profile):
        """Add customer-specific preference features"""

        # Budget alignment
        price_prefs = customer_profile.get('property_preferences', {}).get('price_range', {})
        if price_prefs.get('min') and price_prefs.get('max') and 'Median Price' in df.columns:
            try:
                min_price = float(str(price_prefs['min']).replace('$', '').replace(',', ''))
                max_price = float(str(price_prefs['max']).replace('$', '').replace(',', ''))

                df['Budget_Alignment_Score'] = np.where(
                    (df['Median Price'] >= min_price) & (df['Median Price'] <= max_price),
                    1.0,
                    np.maximum(0, 1 - abs(df['Median Price'] - (min_price + max_price) / 2) / ((max_price - min_price) / 2))
                )
            except (ValueError, TypeError):
                df['Budget_Alignment_Score'] = 0.5
        else:
            df['Budget_Alignment_Score'] = 0.5

        # Yield preference alignment
        target_yield = customer_profile.get('investment_goals', {}).get('target_yield', '4.0')
        if 'Rental Yield on Houses' in df.columns:
            try:
                target = float(str(target_yield).replace('%', ''))
                df['Yield_Preference_Score'] = 1 / (1 + abs(df['Rental Yield on Houses'] - target))
            except (ValueError, TypeError):
                df['Yield_Preference_Score'] = 0.5
        else:
            df['Yield_Preference_Score'] = 0.5

    def train_scoring_models(self, df, customer_profile):
        """Step 5: Scoring Engine - Train separate Growth, Yield, and Risk models"""

        if df is None or df.empty:
            return False

        try:
            # Prepare features
            df_features = self.prepare_features(df, customer_profile)

            # Define feature sets for each model
            self._define_feature_sets(df_features)

            # Train individual models
            success_growth = self._train_growth_model(df_features)
            success_yield = self._train_yield_model(df_features)
            success_risk = self._train_risk_model(df_features)

            self.is_trained = success_growth and success_yield and success_risk

            return self.is_trained

        except Exception as e:
            print(f"Error training scoring models: {str(e)}")
            return False

    def _define_feature_sets(self, df):
        """Define specific features for each scoring model"""

        all_numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Growth model features - focus on price appreciation indicators
        growth_features = [
            '10 yr Avg. Annual Growth',
            '3 mos. Change on Median Price',
            '12 mos. Change on Median Price',
            '36 mos. Change on Median Price',
            'Population',
            'LGA Population Forecast 2026',
            'LGA Population Forecast 2031',
            '10 Year Population Change',
            'Demand_Supply_Pressure',
            'Market_Momentum',
            'Demographic_Strength'
        ]

        # Yield model features - focus on rental returns
        yield_features = [
            'Rental Yield on Houses',
            'Rental Yield on 2 BR House',
            'Rental Yield on 3 BR House',
            'Rental Yield on 4 BR House',
            'Median Rent',
            'Percentage of Renter',
            'More than $3000 gross weekly income',
            'Households where rent repayments are < 30% of household income',
            'Yield_Preference_Score'
        ]

        # Risk model features - focus on volatility and vacancy
        risk_features = [
            'Vacancy Rate',
            'Sales Days on Market',
            'Stock on Market Percentage (SOM%)',
            'Avg. Vendor Discount',
            'Inventory Levels (Months)',
            '3 mos. Change on Sales Days on Market',
            '12 mos. Change on Sales Days on Market',
            'Households with mortgage repayments >= 30% of household income',
            'Less than $650 gross weekly income'
        ]

        # Filter to only include available columns
        self.feature_columns['growth'] = [col for col in growth_features if col in all_numeric_cols]
        self.feature_columns['yield'] = [col for col in yield_features if col in all_numeric_cols]
        self.feature_columns['risk'] = [col for col in risk_features if col in all_numeric_cols]

        # Add any remaining numeric columns to appropriate models
        remaining_cols = set(all_numeric_cols) - set(self.feature_columns['growth'] + self.feature_columns['yield'] + self.feature_columns['risk'])
        remaining_cols = [col for col in remaining_cols if not any(x in col for x in ['_Normalized', '_Score', 'Suburb', 'State'])]

        # Distribute remaining columns
        for i, col in enumerate(remaining_cols):
            if i % 3 == 0:
                self.feature_columns['growth'].append(col)
            elif i % 3 == 1:
                self.feature_columns['yield'].append(col)
            else:
                self.feature_columns['risk'].append(col)

    def _train_growth_model(self, df):
        """Train the Growth scoring model"""

        if len(self.feature_columns['growth']) < 3:
            return False

        try:
            X = df[self.feature_columns['growth']].fillna(0)

            # Create growth target
            y_growth = self._create_growth_target(df)

            # Train model
            X_train, X_test, y_train, y_test = self._split_data(X, y_growth)
            X_train_scaled = self.scalers['growth'].fit_transform(X_train)
            X_test_scaled = self.scalers['growth'].transform(X_test)

            self.models['growth'] = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            self.models['growth'].fit(X_train_scaled, y_train)

            # Store feature importance
            self.feature_importance_log['growth'] = dict(zip(self.feature_columns['growth'], self.models['growth'].feature_importances_))

            return True

        except Exception as e:
            print(f"Error training growth model: {str(e)}")
            return False

    def _train_yield_model(self, df):
        """Train the Yield scoring model"""

        if len(self.feature_columns['yield']) < 3:
            return False

        try:
            X = df[self.feature_columns['yield']].fillna(0)

            # Create yield target
            y_yield = self._create_yield_target(df)

            # Train model
            X_train, X_test, y_train, y_test = self._split_data(X, y_yield)
            X_train_scaled = self.scalers['yield'].fit_transform(X_train)
            X_test_scaled = self.scalers['yield'].transform(X_test)

            self.models['yield'] = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            self.models['yield'].fit(X_train_scaled, y_train)

            # Store feature importance
            self.feature_importance_log['yield'] = dict(zip(self.feature_columns['yield'], self.models['yield'].feature_importances_))

            return True

        except Exception as e:
            print(f"Error training yield model: {str(e)}")
            return False

    def _train_risk_model(self, df):
        """Train the Risk scoring model"""

        if len(self.feature_columns['risk']) < 3:
            return False

        try:
            X = df[self.feature_columns['risk']].fillna(0)

            # Create risk target (lower is better)
            y_risk = self._create_risk_target(df)

            # Train model
            X_train, X_test, y_train, y_test = self._split_data(X, y_risk)
            X_train_scaled = self.scalers['risk'].fit_transform(X_train)
            X_test_scaled = self.scalers['risk'].transform(X_test)

            self.models['risk'] = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            self.models['risk'].fit(X_train_scaled, y_train)

            # Store feature importance
            self.feature_importance_log['risk'] = dict(zip(self.feature_columns['risk'], self.models['risk'].feature_importances_))

            return True

        except Exception as e:
            print(f"Error training risk model: {str(e)}")
            return False

    def _create_growth_target(self, df):
        """Create growth target based on capital appreciation indicators"""

        target_components = []

        if '10 yr Avg. Annual Growth' in df.columns:
            growth_norm = self._normalize_feature(df['10 yr Avg. Annual Growth'])
            target_components.append(growth_norm * 0.4)

        if '12 mos. Change on Median Price' in df.columns:
            price_change_norm = self._normalize_feature(df['12 mos. Change on Median Price'])
            target_components.append(price_change_norm * 0.3)

        if 'Demand_Supply_Pressure' in df.columns:
            pressure_norm = self._normalize_feature(df['Demand_Supply_Pressure'])
            target_components.append(pressure_norm * 0.3)

        return np.sum(target_components, axis=0) if target_components else np.random.random(len(df))

    def _create_yield_target(self, df):
        """Create yield target based on rental return indicators"""

        target_components = []

        if 'Rental Yield on Houses' in df.columns:
            yield_norm = self._normalize_feature(df['Rental Yield on Houses'])
            target_components.append(yield_norm * 0.5)

        if 'Percentage of Renter' in df.columns:
            renter_norm = self._normalize_feature(df['Percentage of Renter'])
            target_components.append(renter_norm * 0.3)

        if 'Yield_Preference_Score' in df.columns:
            target_components.append(df['Yield_Preference_Score'] * 0.2)

        return np.sum(target_components, axis=0) if target_components else np.random.random(len(df))

    def _create_risk_target(self, df):
        """Create risk target (lower values = lower risk)"""

        target_components = []

        # High vacancy = high risk
        if 'Vacancy Rate' in df.columns:
            vacancy_risk = self._normalize_feature(df['Vacancy Rate'])
            target_components.append(vacancy_risk * 0.3)

        # High days on market = high risk
        if 'Sales Days on Market' in df.columns:
            dom_risk = self._normalize_feature(df['Sales Days on Market'])
            target_components.append(dom_risk * 0.3)

        # High stock on market = high risk
        if 'Stock on Market Percentage (SOM%)' in df.columns:
            som_risk = self._normalize_feature(df['Stock on Market Percentage (SOM%)'])
            target_components.append(som_risk * 0.4)

        return np.sum(target_components, axis=0) if target_components else np.random.random(len(df))

    def _normalize_feature(self, series):
        """Normalize a feature to 0-1 scale"""
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return np.zeros(len(series))
        return (series - min_val) / (max_val - min_val)

    def _split_data(self, X, y):
        """Split data for training"""
        if len(X) > 10:
            return train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            return X, X, y, y

    def predict_scores(self, df, customer_profile):
        """Generate Growth, Yield, Risk, and Overall scores"""

        if not self.is_trained:
            return pd.DataFrame()

        try:
            # Prepare features
            df_features = self.prepare_features(df, customer_profile)

            # Predict individual scores
            growth_scores = self._predict_growth_scores(df_features)
            yield_scores = self._predict_yield_scores(df_features)
            risk_scores = self._predict_risk_scores(df_features)

            # Create results dataframe
            results = df_features.copy()
            results['Growth_Score'] = growth_scores
            results['Yield_Score'] = yield_scores
            results['Risk_Score'] = risk_scores

            # Calculate overall score (customizable weights)
            investment_goals = customer_profile.get('investment_goals', {})
            purpose = investment_goals.get('primary_purpose', 'Both').lower()

            # Adjust weights based on customer purpose
            if 'growth' in purpose:
                growth_weight, yield_weight = 0.6, 0.3
            elif 'income' in purpose or 'rental' in purpose:
                growth_weight, yield_weight = 0.3, 0.6
            else:  # Balanced
                growth_weight, yield_weight = 0.4, 0.4

            risk_weight = 0.2

            # Risk score is inverted (lower risk = higher overall score)
            results['Overall_Score'] = (
                results['Growth_Score'] * growth_weight +
                results['Yield_Score'] * yield_weight +
                (1 - results['Risk_Score']) * risk_weight
            )

            # Add confidence and reason codes
            results = self._add_explanations(results, customer_profile)

            return results

        except Exception as e:
            print(f"Error generating scores: {str(e)}")
            return df

    def _predict_growth_scores(self, df):
        """Predict growth scores"""
        X = df[self.feature_columns['growth']].fillna(0)
        X_scaled = self.scalers['growth'].transform(X)
        scores = self.models['growth'].predict(X_scaled)
        return np.clip(scores, 0, 1)

    def _predict_yield_scores(self, df):
        """Predict yield scores"""
        X = df[self.feature_columns['yield']].fillna(0)
        X_scaled = self.scalers['yield'].transform(X)
        scores = self.models['yield'].predict(X_scaled)
        return np.clip(scores, 0, 1)

    def _predict_risk_scores(self, df):
        """Predict risk scores"""
        X = df[self.feature_columns['risk']].fillna(0)
        X_scaled = self.scalers['risk'].transform(X)
        scores = self.models['risk'].predict(X_scaled)
        return np.clip(scores, 0, 1)

    def _add_explanations(self, df, customer_profile):
        """Add reason codes and confidence levels"""

        reasons = []
        confidence_levels = []

        for idx, row in df.iterrows():
            reason_codes = []

            # Growth reasons
            if row['Growth_Score'] > 0.7:
                reason_codes.append("strong growth outlook")

            # Yield reasons
            if row['Yield_Score'] > 0.7:
                reason_codes.append("high rental yield")

            # Risk reasons
            if row['Risk_Score'] < 0.3:
                reason_codes.append("low market risk")

            # Market momentum
            if 'Market_Momentum' in row and row['Market_Momentum'] > df['Market_Momentum'].median():
                reason_codes.append("active market")

            # Budget alignment
            if 'Budget_Alignment_Score' in row and row['Budget_Alignment_Score'] > 0.8:
                reason_codes.append("fits budget")

            reasons.append(", ".join(reason_codes[:3]) if reason_codes else "meets criteria")

            # Confidence based on score consistency
            score_std = np.std([row['Growth_Score'], row['Yield_Score'], 1-row['Risk_Score']])
            if score_std < 0.2:
                confidence_levels.append("High")
            elif score_std < 0.4:
                confidence_levels.append("Medium")
            else:
                confidence_levels.append("Low")

        df['Reason_Codes'] = reasons
        df['Confidence_Level'] = confidence_levels

        return df

    def get_feature_importance(self, model_type='all'):
        """Get feature importance for transparency"""

        if model_type == 'all':
            return self.feature_importance_log
        else:
            return self.feature_importance_log.get(model_type, {})

    def generate_shortlist(self, df, customer_profile, top_n=20):
        """Step 7: Shortlist Generator - Top N suburbs with explanations"""

        scored_df = self.predict_scores(df, customer_profile)

        if scored_df.empty:
            return pd.DataFrame()

        # Apply rule filters (Step 6)
        filtered_df = self._apply_rule_filters(scored_df, customer_profile)

        # Get top N by overall score
        shortlist = filtered_df.nlargest(top_n, 'Overall_Score')

        return shortlist

    def _apply_rule_filters(self, df, customer_profile):
        """Step 6: Apply rule filters and constraints"""

        filtered_df = df.copy()

        # Budget constraints
        price_prefs = customer_profile.get('property_preferences', {}).get('price_range', {})
        if price_prefs.get('min') and price_prefs.get('max') and 'Median Price' in df.columns:
            try:
                min_price = float(str(price_prefs['min']).replace('$', '').replace(',', ''))
                max_price = float(str(price_prefs['max']).replace('$', '').replace(',', ''))

                # Apply with some flexibility (±10%)
                flex_min = min_price * 0.9
                flex_max = max_price * 1.1

                filtered_df = filtered_df[
                    (filtered_df['Median Price'] >= flex_min) &
                    (filtered_df['Median Price'] <= flex_max)
                ]
            except (ValueError, TypeError):
                pass

        # Risk tolerance filter
        risk_tolerance = customer_profile.get('investment_goals', {}).get('risk_tolerance', 'Medium').lower()
        if risk_tolerance == 'low':
            filtered_df = filtered_df[filtered_df['Risk_Score'] < 0.5]
        elif risk_tolerance == 'high':
            # No risk filter for high tolerance
            pass
        else:  # medium
            filtered_df = filtered_df[filtered_df['Risk_Score'] < 0.7]

        return filtered_df