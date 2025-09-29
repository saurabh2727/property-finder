import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging

# SHAP imports with error handling
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    st.warning("SHAP not available. Install with: pip install shap")

class PropertyRecommendationEngine:
    """Machine Learning-based property recommendation system with explainability"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.is_trained = False
        self.explainer = None
        self.training_data = None
        self.feature_importance_log = []
        self.shap_values = None

        # Setup logging
        self._setup_logging()

    def prepare_features(self, df, customer_profile):
        """Prepare features for ML model"""
        if df is None or df.empty:
            return pd.DataFrame()

        df_features = df.copy()

        # Basic feature engineering
        self._add_derived_features(df_features)

        # Customer preference scoring
        self._add_customer_preference_features(df_features, customer_profile)

        return df_features

    def _setup_logging(self):
        """Setup logging for feature importance tracking"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/ml_feature_importance.log'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('PropertyMLEngine')
        except Exception:
            # Fallback if logs directory doesn't exist
            self.logger = logging.getLogger('PropertyMLEngine')
            self.logger.addHandler(logging.StreamHandler())
            self.logger.setLevel(logging.INFO)

    def _add_derived_features(self, df):
        """Add derived features for better predictions"""

        # Price-to-income ratios if population data available
        if 'Population' in df.columns and 'Median Price' in df.columns:
            df['Price_per_Capita'] = df['Median Price'] / (df['Population'] + 1)

        # Investment attractiveness score
        if 'Rental Yield on Houses' in df.columns and 'Median Price' in df.columns:
            df['Investment_Score'] = (df['Rental Yield on Houses'] / 100) * 1000000 / (df['Median Price'] + 1)

        # Distance categories
        if 'Distance (km) to CBD' in df.columns:
            df['Distance_Category'] = pd.cut(
                df['Distance (km) to CBD'],
                bins=[0, 10, 25, 50, 100],
                labels=['Inner', 'Middle', 'Outer', 'Regional']
            ).astype(str)

        # Price categories
        if 'Median Price' in df.columns:
            df['Price_Category'] = pd.cut(
                df['Median Price'],
                bins=[0, 500000, 800000, 1200000, float('inf')],
                labels=['Budget', 'Mid', 'Premium', 'Luxury']
            ).astype(str)

        # Growth potential indicator
        if '10 yr Avg. Annual Growth' in df.columns:
            df['High_Growth'] = (df['10 yr Avg. Annual Growth'] > df['10 yr Avg. Annual Growth'].median()).astype(int)

        return df

    def _add_customer_preference_features(self, df, customer_profile):
        """Add customer-specific preference features"""

        # Extract customer preferences
        financial_profile = customer_profile.get('financial_profile', {})
        investment_goals = customer_profile.get('investment_goals', {})
        property_preferences = customer_profile.get('property_preferences', {})
        lifestyle_factors = customer_profile.get('lifestyle_factors', {})

        # Budget alignment score
        price_range = property_preferences.get('price_range', {})
        if price_range.get('min') and price_range.get('max') and 'Median Price' in df.columns:
            try:
                min_price = float(str(price_range['min']).replace('$', '').replace(',', ''))
                max_price = float(str(price_range['max']).replace('$', '').replace(',', ''))

                df['Budget_Alignment'] = np.where(
                    (df['Median Price'] >= min_price) & (df['Median Price'] <= max_price),
                    1.0,
                    np.maximum(0, 1 - abs(df['Median Price'] - (min_price + max_price) / 2) / ((max_price - min_price) / 2))
                )
            except (ValueError, TypeError):
                df['Budget_Alignment'] = 0.5

        # Yield preference alignment
        target_yield = investment_goals.get('target_yield', '4.0')
        if 'Rental Yield on Houses' in df.columns:
            try:
                target = float(str(target_yield).replace('%', ''))
                df['Yield_Alignment'] = 1 / (1 + abs(df['Rental Yield on Houses'] - target))
            except (ValueError, TypeError):
                df['Yield_Alignment'] = 0.5

        # Location preference alignment
        preferred_suburbs = property_preferences.get('preferred_suburbs', [])
        if preferred_suburbs and 'Suburb' in df.columns:
            # Clean and normalize suburb names
            preferred_clean = [s.strip().lower() for s in preferred_suburbs if s.strip()]
            df['Suburb_Preference'] = df['Suburb'].str.lower().isin(preferred_clean).astype(float)
        else:
            df['Suburb_Preference'] = 0.0

        # Lifestyle factor scoring
        lifestyle_weights = {
            'proximity_to_cbd': 0.3,
            'school_quality': 0.2,
            'transport_access': 0.2,
            'shopping_amenities': 0.15,
            'future_development': 0.15
        }

        lifestyle_score = 0
        for factor, weight in lifestyle_weights.items():
            importance = lifestyle_factors.get(factor, 'Medium').lower()
            score = {'low': 0.3, 'medium': 0.6, 'high': 1.0}.get(importance, 0.6)
            lifestyle_score += score * weight

        df['Lifestyle_Score'] = lifestyle_score

        return df

    def train_models(self, df, customer_profile):
        """Train ML models for recommendations"""

        if df is None or df.empty:
            return False

        try:
            # Prepare features
            df_features = self.prepare_features(df, customer_profile)

            # Select numeric features for training
            numeric_features = df_features.select_dtypes(include=[np.number]).columns.tolist()

            # Remove target variables and identifiers
            exclude_cols = ['Suburb', 'State', 'Region']
            numeric_features = [col for col in numeric_features if col not in exclude_cols]

            if len(numeric_features) < 3:
                import streamlit as st
                st.error(f"❌ Insufficient numeric features for ML training")
                st.write(f"Found {len(numeric_features)} numeric features, need at least 3")
                st.write(f"Available features: {numeric_features}")
                return False

            self.feature_columns = numeric_features

            # Prepare training data
            X = df_features[numeric_features].fillna(0)

            # Create composite target variable (investment attractiveness)
            y_investment = self._create_investment_target(df_features)

            # Split data
            if len(X) > 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_investment, test_size=0.2, random_state=42
                )
            else:
                X_train, X_test, y_train, y_test = X, X, y_investment, y_investment

            # Scale features
            self.scalers['investment'] = StandardScaler()
            X_train_scaled = self.scalers['investment'].fit_transform(X_train)
            X_test_scaled = self.scalers['investment'].transform(X_test)

            # Train model
            self.models['investment'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )

            self.models['investment'].fit(X_train_scaled, y_train)

            # Evaluate model
            y_pred = self.models['investment'].predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)

            # Store training data for SHAP explanations
            self.training_data = X_train_scaled

            # Initialize SHAP explainer
            if SHAP_AVAILABLE:
                try:
                    self.explainer = shap.TreeExplainer(self.models['investment'])
                    # Calculate SHAP values for a sample
                    sample_size = min(100, len(X_train_scaled))
                    sample_indices = np.random.choice(len(X_train_scaled), sample_size, replace=False)
                    self.shap_values = self.explainer.shap_values(X_train_scaled[sample_indices])

                    self.logger.info(f"SHAP explainer initialized with {sample_size} samples")
                except Exception as e:
                    self.logger.warning(f"Could not initialize SHAP explainer: {e}")
                    self.explainer = None

            # Log feature importance
            self._log_feature_importance(r2)

            self.is_trained = True
            return True

        except Exception as e:
            import streamlit as st
            st.error(f"🔍 **ML Training Debug Info:**")
            st.write(f"Error: {str(e)}")
            st.write(f"Dataset shape: {df.shape}")
            st.write(f"Available columns: {list(df.columns)}")
            st.write(f"Numeric features found: {len(numeric_features) if 'numeric_features' in locals() else 'N/A'}")
            if 'numeric_features' in locals():
                st.write(f"Features: {numeric_features}")

            import traceback
            st.code(traceback.format_exc())
            print(f"Error training models: {str(e)}")
            return False

    def _create_investment_target(self, df):
        """Create composite investment attractiveness target"""

        target_components = []

        # Rental yield component
        if 'Rental Yield on Houses' in df.columns:
            yield_norm = (df['Rental Yield on Houses'] - df['Rental Yield on Houses'].min()) / \
                        (df['Rental Yield on Houses'].max() - df['Rental Yield on Houses'].min() + 1e-6)
            target_components.append(yield_norm * 0.3)

        # Growth component
        if '10 yr Avg. Annual Growth' in df.columns:
            growth_norm = (df['10 yr Avg. Annual Growth'] - df['10 yr Avg. Annual Growth'].min()) / \
                         (df['10 yr Avg. Annual Growth'].max() - df['10 yr Avg. Annual Growth'].min() + 1e-6)
            target_components.append(growth_norm * 0.25)

        # Vacancy rate component (lower is better)
        if 'Vacancy Rate' in df.columns:
            vacancy_inv = 1 - ((df['Vacancy Rate'] - df['Vacancy Rate'].min()) / \
                              (df['Vacancy Rate'].max() - df['Vacancy Rate'].min() + 1e-6))
            target_components.append(vacancy_inv * 0.2)

        # Customer preference components
        if 'Budget_Alignment' in df.columns:
            target_components.append(df['Budget_Alignment'] * 0.15)

        if 'Yield_Alignment' in df.columns:
            target_components.append(df['Yield_Alignment'] * 0.1)

        if target_components:
            return np.sum(target_components, axis=0)
        else:
            return np.random.random(len(df))  # Fallback

    def predict_recommendations(self, df, customer_profile, top_n=10):
        """Generate property recommendations"""

        if not self.is_trained or df is None or df.empty:
            return pd.DataFrame()

        try:
            # Prepare features
            df_features = self.prepare_features(df, customer_profile)

            # Select features
            X = df_features[self.feature_columns].fillna(0)

            # Scale features
            X_scaled = self.scalers['investment'].transform(X)

            # Predict investment scores
            investment_scores = self.models['investment'].predict(X_scaled)

            # Add predictions to dataframe
            df_results = df_features.copy()
            df_results['Investment_Score_Predicted'] = investment_scores

            # Apply rule-based filters
            df_filtered = self._apply_customer_filters(df_results, customer_profile)

            # Sort by investment score and return top N
            df_recommendations = df_filtered.nlargest(top_n, 'Investment_Score_Predicted')

            return df_recommendations

        except Exception as e:
            print(f"Error generating predictions: {str(e)}")
            return df.head(top_n)  # Fallback

    def _apply_customer_filters(self, df, customer_profile):
        """Apply customer-specific filters"""

        df_filtered = df.copy()

        # Budget filter
        property_preferences = customer_profile.get('property_preferences', {})
        price_range = property_preferences.get('price_range', {})

        if price_range.get('min') and price_range.get('max') and 'Median Price' in df.columns:
            try:
                min_price = float(str(price_range['min']).replace('$', '').replace(',', ''))
                max_price = float(str(price_range['max']).replace('$', '').replace(',', ''))

                # Apply some flexibility (±20%)
                flex_min = min_price * 0.8
                flex_max = max_price * 1.2

                df_filtered = df_filtered[
                    (df_filtered['Median Price'] >= flex_min) &
                    (df_filtered['Median Price'] <= flex_max)
                ]
            except (ValueError, TypeError):
                pass

        # Yield filter
        investment_goals = customer_profile.get('investment_goals', {})
        target_yield = investment_goals.get('target_yield', '')

        if target_yield and 'Rental Yield on Houses' in df_filtered.columns:
            try:
                min_yield = float(str(target_yield).replace('%', '')) * 0.8
                df_filtered = df_filtered[df_filtered['Rental Yield on Houses'] >= min_yield]
            except (ValueError, TypeError):
                pass

        return df_filtered

    def get_feature_importance(self):
        """Get feature importance from trained models"""

        if not self.is_trained or 'investment' not in self.models:
            return {}

        importance = self.models['investment'].feature_importances_
        feature_names = self.feature_columns

        importance_dict = dict(zip(feature_names, importance))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

    def explain_recommendation(self, suburb_data, customer_profile):
        """Provide explanation for recommendations"""

        explanations = []

        # Budget alignment
        if 'Budget_Alignment' in suburb_data:
            alignment = suburb_data.get('Budget_Alignment', 0)
            if alignment > 0.8:
                explanations.append("✅ Excellent budget alignment")
            elif alignment > 0.6:
                explanations.append("✅ Good budget fit")
            else:
                explanations.append("⚠️ Outside preferred budget range")

        # Yield performance
        if 'Rental Yield on Houses' in suburb_data:
            yield_val = suburb_data.get('Rental Yield on Houses', 0)
            target_yield = customer_profile.get('investment_goals', {}).get('target_yield', '4.0')
            try:
                target = float(str(target_yield).replace('%', ''))
                if yield_val >= target:
                    explanations.append(f"✅ High rental yield ({yield_val:.1f}% vs {target:.1f}% target)")
                else:
                    explanations.append(f"⚠️ Below target yield ({yield_val:.1f}% vs {target:.1f}% target)")
            except (ValueError, TypeError):
                explanations.append(f"💰 Rental yield: {yield_val:.1f}%")

        # Growth potential
        if '10 yr Avg. Annual Growth' in suburb_data:
            growth = suburb_data.get('10 yr Avg. Annual Growth', 0)
            if growth > 6:
                explanations.append(f"📈 Strong historical growth ({growth:.1f}% p.a.)")
            elif growth > 4:
                explanations.append(f"📊 Moderate growth potential ({growth:.1f}% p.a.)")
            else:
                explanations.append(f"📉 Slower growth area ({growth:.1f}% p.a.)")

        return explanations

    def _log_feature_importance(self, model_score):
        """Log feature importance for tracking model performance"""
        try:
            importance_dict = self.get_feature_importance()

            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_score': model_score,
                'feature_importance': importance_dict,
                'top_5_features': list(importance_dict.keys())[:5],
                'training_samples': len(self.training_data) if self.training_data is not None else 0
            }

            self.feature_importance_log.append(log_entry)

            # Log to file
            self.logger.info(f"Model trained with R² score: {model_score:.3f}")
            self.logger.info(f"Top 5 features: {log_entry['top_5_features']}")

            # Keep only last 10 entries to avoid memory issues
            if len(self.feature_importance_log) > 10:
                self.feature_importance_log = self.feature_importance_log[-10:]

        except Exception as e:
            self.logger.error(f"Error logging feature importance: {e}")

    def get_shap_explanation(self, suburb_data_row, top_n_features=5):
        """Get SHAP explanation for a specific suburb recommendation"""
        if not SHAP_AVAILABLE or self.explainer is None or not self.is_trained:
            return None

        try:
            # Prepare the data row
            if isinstance(suburb_data_row, pd.Series):
                suburb_data_row = suburb_data_row.to_frame().T

            # Select and scale features
            X_row = suburb_data_row[self.feature_columns].fillna(0)
            X_row_scaled = self.scalers['investment'].transform(X_row)

            # Get SHAP values for this specific row
            shap_values = self.explainer.shap_values(X_row_scaled)

            # Create explanation dictionary
            feature_impacts = {}
            for i, feature in enumerate(self.feature_columns):
                feature_impacts[feature] = {
                    'shap_value': float(shap_values[0][i]),
                    'feature_value': float(X_row.iloc[0, i]),
                    'impact_direction': 'positive' if shap_values[0][i] > 0 else 'negative'
                }

            # Sort by absolute SHAP value and return top N
            sorted_features = sorted(
                feature_impacts.items(),
                key=lambda x: abs(x[1]['shap_value']),
                reverse=True
            )[:top_n_features]

            return dict(sorted_features)

        except Exception as e:
            self.logger.error(f"Error generating SHAP explanation: {e}")
            return None

    def create_feature_importance_chart(self):
        """Create interactive feature importance visualization"""
        if not self.is_trained:
            return None

        try:
            importance_dict = self.get_feature_importance()

            if not importance_dict:
                return None

            # Get top 10 features
            top_features = dict(list(importance_dict.items())[:10])

            fig = px.bar(
                x=list(top_features.values()),
                y=list(top_features.keys()),
                orientation='h',
                title='Feature Importance (Random Forest)',
                labels={'x': 'Importance Score', 'y': 'Features'},
                color=list(top_features.values()),
                color_continuous_scale='viridis'
            )

            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating feature importance chart: {e}")
            return None

    def create_shap_summary_plot(self):
        """Create SHAP summary visualization"""
        if not SHAP_AVAILABLE or self.explainer is None or self.shap_values is None:
            return None

        try:
            # Create SHAP summary plot data
            shap_mean = np.mean(np.abs(self.shap_values), axis=0)

            # Get top 10 features by mean SHAP value
            top_indices = np.argsort(shap_mean)[-10:]
            top_features = [self.feature_columns[i] for i in top_indices]
            top_shap_values = shap_mean[top_indices]

            fig = px.bar(
                x=top_shap_values,
                y=top_features,
                orientation='h',
                title='SHAP Feature Importance (Mean |SHAP value|)',
                labels={'x': 'Mean |SHAP value|', 'y': 'Features'},
                color=top_shap_values,
                color_continuous_scale='plasma'
            )

            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating SHAP summary plot: {e}")
            return None

    def get_model_insights(self):
        """Get comprehensive model insights and performance metrics"""
        if not self.is_trained:
            return {}

        insights = {
            'model_trained': True,
            'feature_count': len(self.feature_columns),
            'shap_available': SHAP_AVAILABLE and self.explainer is not None,
            'training_history': self.feature_importance_log,
            'top_features': list(self.get_feature_importance().keys())[:5] if self.get_feature_importance() else []
        }

        if self.feature_importance_log:
            latest_log = self.feature_importance_log[-1]
            insights['latest_model_score'] = latest_log.get('model_score', 'N/A')
            insights['latest_training_time'] = latest_log.get('timestamp', 'N/A')

        return insights