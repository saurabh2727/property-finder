import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from models.ml_recommender import PropertyRecommendationEngine
from utils.session_state import update_workflow_step

def render_suburb_analysis_page():
    """Render the suburb analysis and filtering page"""

    st.title("🔍 Suburb Analysis & Filtering")
    st.subheader("Intelligent Property Market Analysis")

    # Progress indicator
    progress_cols = st.columns(5)
    with progress_cols[0]:
        st.markdown("✅ Step 1: Customer Profile")
    with progress_cols[1]:
        st.markdown("✅ Step 2: Data Upload")
    with progress_cols[2]:
        st.markdown("🔄 **Step 3: Analysis**")
    with progress_cols[3]:
        st.markdown("⏳ Step 4: Recommendations")
    with progress_cols[4]:
        st.markdown("⏳ Step 5: Reports")

    st.markdown("---")

    # Check prerequisites
    if not st.session_state.get('profile_generated', False):
        st.warning("⚠️ Please complete customer profiling first!")
        if st.button("← Go to Customer Profile"):
            st.session_state.current_page = 'customer_profile'
            st.rerun()
        return

    if not st.session_state.get('data_uploaded', False):
        st.warning("⚠️ Please upload suburb data first!")
        if st.button("← Go to Data Upload"):
            st.session_state.current_page = 'data_upload'
            st.rerun()
        return

    # Get data
    df = st.session_state.suburb_data
    customer_profile = st.session_state.customer_profile

    if df is None or df.empty:
        st.error("No suburb data available. Please upload data first.")
        return

    # Analysis options
    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(["🎯 Filtering", "📊 Analytics", "🤖 ML Training"])

    with analysis_tab1:
        render_filtering_section(df, customer_profile)

    with analysis_tab2:
        render_analytics_section(df, customer_profile)

    with analysis_tab3:
        render_ml_training_section(df, customer_profile)

def render_filtering_section(df, customer_profile):
    """Render the filtering and configuration section"""

    st.subheader("🎯 Configure Analysis Parameters")

    # Customer profile summary
    with st.expander("👤 Customer Profile Summary", expanded=False):
        display_customer_summary(customer_profile)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 💰 Budget Filters")

        # Price range
        if 'Median Price' in df.columns:
            price_min, price_max = int(df['Median Price'].min()), int(df['Median Price'].max())

            # Get customer preferred range
            customer_price = customer_profile.get('property_preferences', {}).get('price_range', {})
            customer_min = customer_price.get('min', str(price_min))
            customer_max = customer_price.get('max', str(price_max))

            try:
                default_min = int(str(customer_min).replace('$', '').replace(',', ''))
                default_max = int(str(customer_max).replace('$', '').replace(',', ''))
            except:
                default_min, default_max = price_min, price_max

            # Ensure values are step-aligned and within bounds
            def align_to_step(value, step, min_val, max_val):
                """Align value to step and ensure it's within bounds"""
                aligned = round(value / step) * step
                return max(min_val, min(max_val, aligned))

            aligned_min = align_to_step(max(price_min, default_min), 10000, price_min, price_max)
            aligned_max = align_to_step(min(price_max, default_max), 10000, price_min, price_max)

            # Ensure min <= max
            if aligned_min > aligned_max:
                aligned_min, aligned_max = aligned_max, aligned_min

            price_range = st.slider(
                "Price Range ($)",
                min_value=price_min,
                max_value=price_max,
                value=(aligned_min, aligned_max),
                step=10000,
                format="$%d"
            )

        # Rental yield filter
        if 'Rental Yield on Houses' in df.columns:
            yield_min, yield_max = float(df['Rental Yield on Houses'].min()), float(df['Rental Yield on Houses'].max())

            customer_target_yield = customer_profile.get('investment_goals', {}).get('target_yield', '4.0')
            try:
                default_yield = float(str(customer_target_yield).replace('%', ''))
            except:
                default_yield = 4.0

            # Align yield value to step
            aligned_yield = align_to_step(max(yield_min, default_yield * 0.8), 0.1, yield_min, yield_max)

            min_yield = st.slider(
                "Minimum Rental Yield (%)",
                min_value=yield_min,
                max_value=yield_max,
                value=aligned_yield,
                step=0.1
            )

    with col2:
        st.markdown("#### 📍 Location Filters")

        # State filter
        if 'State' in df.columns:
            available_states = df['State'].unique().tolist()
            selected_states = st.multiselect(
                "States",
                available_states,
                default=available_states
            )

        # Distance to CBD
        if 'Distance (km) to CBD' in df.columns:
            distance_max = int(df['Distance (km) to CBD'].max())

            # Get customer preference
            cbd_importance = customer_profile.get('lifestyle_factors', {}).get('proximity_to_cbd', 'Medium').lower()
            if cbd_importance == 'high':
                default_distance = min(20, distance_max)
            elif cbd_importance == 'low':
                default_distance = distance_max
            else:
                default_distance = min(35, distance_max)

            # Align distance value to step
            aligned_distance = align_to_step(default_distance, 5, 0, distance_max)

            max_distance = st.slider(
                "Maximum Distance to CBD (km)",
                min_value=0,
                max_value=distance_max,
                value=aligned_distance,
                step=5
            )

    # Advanced filters
    with st.expander("⚙️ Advanced Filters", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # Growth rate filter
            if '10 yr Avg. Annual Growth' in df.columns:
                growth_min = st.number_input(
                    "Minimum 10-year Growth Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=3.0,
                    step=0.5
                )

            # Vacancy rate filter
            if 'Vacancy Rate' in df.columns:
                max_vacancy = st.number_input(
                    "Maximum Vacancy Rate (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=5.0,
                    step=0.5
                )

        with col2:
            # Population filter
            if 'Population' in df.columns:
                min_population = st.number_input(
                    "Minimum Population",
                    min_value=0,
                    max_value=100000,
                    value=5000,
                    step=1000
                )

    # Apply filters
    st.markdown("#### 🔍 Apply Filters")

    if st.button("🎯 Filter Suburbs", type="primary", use_container_width=True):
        filtered_df = apply_filters(
            df,
            price_range=price_range if 'Median Price' in df.columns else None,
            min_yield=min_yield if 'Rental Yield on Houses' in df.columns else None,
            selected_states=selected_states if 'State' in df.columns else None,
            max_distance=max_distance if 'Distance (km) to CBD' in df.columns else None,
            growth_min=growth_min if '10 yr Avg. Annual Growth' in df.columns else None,
            max_vacancy=max_vacancy if 'Vacancy Rate' in df.columns else None,
            min_population=min_population if 'Population' in df.columns else None
        )

        st.session_state.filtered_suburbs = filtered_df
        st.success(f"✅ Filtered to {len(filtered_df)} suburbs from {len(df)} total")

        # Display filtered results
        if not filtered_df.empty:
            display_filtered_results(filtered_df)

def apply_filters(df, price_range=None, min_yield=None, selected_states=None,
                 max_distance=None, growth_min=None, max_vacancy=None, min_population=None):
    """Apply filtering criteria to suburb data"""

    filtered_df = df.copy()

    # Price filter
    if price_range and 'Median Price' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Median Price'] >= price_range[0]) &
            (filtered_df['Median Price'] <= price_range[1])
        ]

    # Yield filter
    if min_yield and 'Rental Yield on Houses' in df.columns:
        filtered_df = filtered_df[filtered_df['Rental Yield on Houses'] >= min_yield]

    # State filter
    if selected_states and 'State' in df.columns:
        filtered_df = filtered_df[filtered_df['State'].isin(selected_states)]

    # Distance filter
    if max_distance and 'Distance (km) to CBD' in df.columns:
        filtered_df = filtered_df[filtered_df['Distance (km) to CBD'] <= max_distance]

    # Growth filter
    if growth_min and '10 yr Avg. Annual Growth' in df.columns:
        filtered_df = filtered_df[filtered_df['10 yr Avg. Annual Growth'] >= growth_min]

    # Vacancy filter
    if max_vacancy and 'Vacancy Rate' in df.columns:
        filtered_df = filtered_df[filtered_df['Vacancy Rate'] <= max_vacancy]

    # Population filter
    if min_population and 'Population' in df.columns:
        filtered_df = filtered_df[filtered_df['Population'] >= min_population]

    return filtered_df

def display_filtered_results(filtered_df):
    """Display filtered results with visualizations"""

    st.subheader(f"📋 Filtered Results ({len(filtered_df)} suburbs)")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if 'Median Price' in filtered_df.columns:
            avg_price = filtered_df['Median Price'].mean()
            st.metric("Avg Median Price", f"${avg_price:,.0f}")

    with col2:
        if 'Rental Yield on Houses' in filtered_df.columns:
            avg_yield = filtered_df['Rental Yield on Houses'].mean()
            st.metric("Avg Rental Yield", f"{avg_yield:.1f}%")

    with col3:
        if '10 yr Avg. Annual Growth' in filtered_df.columns:
            avg_growth = filtered_df['10 yr Avg. Annual Growth'].mean()
            st.metric("Avg Growth Rate", f"{avg_growth:.1f}%")

    with col4:
        if 'Distance (km) to CBD' in filtered_df.columns:
            avg_distance = filtered_df['Distance (km) to CBD'].mean()
            st.metric("Avg Distance CBD", f"{avg_distance:.0f} km")

    # Top performers table
    st.subheader("🏆 Top Performing Suburbs")

    # Create composite score
    if 'Rental Yield on Houses' in filtered_df.columns and '10 yr Avg. Annual Growth' in filtered_df.columns:
        filtered_df['Composite_Score'] = (
            filtered_df['Rental Yield on Houses'] * 0.4 +
            filtered_df['10 yr Avg. Annual Growth'] * 0.6
        )
        top_suburbs = filtered_df.nlargest(10, 'Composite_Score')
    else:
        top_suburbs = filtered_df.head(10)

    # Display table
    display_cols = ['Suburb', 'State']
    if 'Median Price' in filtered_df.columns:
        display_cols.append('Median Price')
    if 'Rental Yield on Houses' in filtered_df.columns:
        display_cols.append('Rental Yield on Houses')
    if '10 yr Avg. Annual Growth' in filtered_df.columns:
        display_cols.append('10 yr Avg. Annual Growth')
    if 'Distance (km) to CBD' in filtered_df.columns:
        display_cols.append('Distance (km) to CBD')

    available_cols = [col for col in display_cols if col in top_suburbs.columns]
    st.dataframe(top_suburbs[available_cols], use_container_width=True)

    # Continue button
    if st.button("➡️ Continue to ML Recommendations", type="primary", use_container_width=True):
        st.session_state.current_page = 'recommendations'
        update_workflow_step(4)
        st.rerun()

def render_analytics_section(df, customer_profile):
    """Render analytics and visualizations section"""

    st.subheader("📊 Market Analytics")

    # Market overview
    col1, col2 = st.columns([2, 1])

    with col1:
        # Price vs Yield scatter plot
        if 'Median Price' in df.columns and 'Rental Yield on Houses' in df.columns:
            fig = px.scatter(
                df,
                x='Median Price',
                y='Rental Yield on Houses',
                color='State' if 'State' in df.columns else None,
                hover_data=['Suburb'] if 'Suburb' in df.columns else None,
                title="Median Price vs Rental Yield"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Key insights
        st.markdown("#### 💡 Key Insights")

        if 'Rental Yield on Houses' in df.columns:
            high_yield_suburbs = df[df['Rental Yield on Houses'] > df['Rental Yield on Houses'].quantile(0.8)]
            st.write(f"🎯 **High Yield Areas:** {len(high_yield_suburbs)} suburbs with >80th percentile yield")

        if '10 yr Avg. Annual Growth' in df.columns:
            high_growth_suburbs = df[df['10 yr Avg. Annual Growth'] > df['10 yr Avg. Annual Growth'].quantile(0.8)]
            st.write(f"📈 **Growth Areas:** {len(high_growth_suburbs)} suburbs with strong historical growth")

        # Customer alignment analysis
        analyze_customer_alignment(df, customer_profile)

    # Detailed analytics
    tab1, tab2, tab3 = st.tabs(["Price Analysis", "Yield Analysis", "Growth Analysis"])

    with tab1:
        render_price_analysis(df)

    with tab2:
        render_yield_analysis(df)

    with tab3:
        render_growth_analysis(df)

def analyze_customer_alignment(df, customer_profile):
    """Analyze alignment with customer preferences"""

    st.markdown("#### 🎯 Customer Alignment")

    # Budget alignment
    price_prefs = customer_profile.get('property_preferences', {}).get('price_range', {})
    if price_prefs.get('min') and price_prefs.get('max') and 'Median Price' in df.columns:
        try:
            min_price = float(str(price_prefs['min']).replace('$', '').replace(',', ''))
            max_price = float(str(price_prefs['max']).replace('$', '').replace(',', ''))

            aligned_suburbs = df[
                (df['Median Price'] >= min_price) &
                (df['Median Price'] <= max_price)
            ]

            alignment_pct = len(aligned_suburbs) / len(df) * 100
            st.write(f"💰 **Budget Aligned:** {len(aligned_suburbs)} suburbs ({alignment_pct:.1f}%)")
        except:
            pass

    # Yield alignment
    yield_target = customer_profile.get('investment_goals', {}).get('target_yield', '')
    if yield_target and 'Rental Yield on Houses' in df.columns:
        try:
            target = float(str(yield_target).replace('%', ''))
            above_target = df[df['Rental Yield on Houses'] >= target]
            st.write(f"📊 **Above Target Yield:** {len(above_target)} suburbs")
        except:
            pass

def render_price_analysis(df):
    """Render price analysis visualizations"""

    if 'Median Price' not in df.columns:
        st.info("Price analysis requires 'Median Price' column")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Price distribution
        fig = px.histogram(df, x='Median Price', title="Price Distribution", nbins=30)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Price by state
        if 'State' in df.columns:
            fig = px.box(df, x='State', y='Median Price', title="Price Distribution by State")
            st.plotly_chart(fig, use_container_width=True)

def render_yield_analysis(df):
    """Render yield analysis visualizations"""

    if 'Rental Yield on Houses' not in df.columns:
        st.info("Yield analysis requires 'Rental Yield on Houses' column")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Yield distribution
        fig = px.histogram(df, x='Rental Yield on Houses', title="Rental Yield Distribution", nbins=30)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Yield vs Distance
        if 'Distance (km) to CBD' in df.columns:
            fig = px.scatter(df, x='Distance (km) to CBD', y='Rental Yield on Houses',
                           title="Rental Yield vs Distance to CBD")
            st.plotly_chart(fig, use_container_width=True)

def render_growth_analysis(df):
    """Render growth analysis visualizations"""

    if '10 yr Avg. Annual Growth' not in df.columns:
        st.info("Growth analysis requires '10 yr Avg. Annual Growth' column")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Growth distribution
        fig = px.histogram(df, x='10 yr Avg. Annual Growth', title="Growth Rate Distribution", nbins=30)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Growth vs Price
        if 'Median Price' in df.columns:
            fig = px.scatter(df, x='Median Price', y='10 yr Avg. Annual Growth',
                           title="Growth Rate vs Median Price")
            st.plotly_chart(fig, use_container_width=True)

def render_ml_training_section(df, customer_profile):
    """Render ML model training section"""

    st.subheader("🤖 Machine Learning Model Training")

    st.info("""
    Train ML models to generate intelligent property recommendations based on:
    - Customer profile and preferences
    - Historical market performance
    - Suburb characteristics and trends
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Model Configuration")

        # Model parameters
        with st.expander("⚙️ Advanced Settings"):
            n_estimators = st.slider("Number of Trees", 50, 200, 100, step=10)
            max_depth = st.slider("Maximum Depth", 5, 20, 10, step=1)
            test_size = st.slider("Test Split", 0.1, 0.3, 0.2, step=0.05)

        # Training button
        if st.button("🚀 Train ML Models", type="primary", use_container_width=True):
            train_ml_models(df, customer_profile)

    with col2:
        st.markdown("#### Model Features")
        st.write("""
        **Input Features:**
        - Price metrics
        - Rental yields
        - Growth rates
        - Location factors
        - Customer preferences

        **Output Predictions:**
        - Investment attractiveness
        - Risk assessment
        - Recommendation scores
        """)

def train_ml_models(df, customer_profile):
    """Train machine learning models"""

    with st.spinner("🔄 Training ML models..."):
        try:
            # Initialize recommender
            recommender = PropertyRecommendationEngine()

            # Train models
            success = recommender.train_models(df, customer_profile)

            if success:
                # Store trained model in session state
                st.session_state.ml_recommender = recommender

                st.success("✅ ML models trained successfully!")

                # Show feature importance
                feature_importance = recommender.get_feature_importance()
                if feature_importance:
                    st.subheader("📊 Feature Importance")

                    importance_df = pd.DataFrame([
                        {'Feature': k, 'Importance': v}
                        for k, v in list(feature_importance.items())[:10]
                    ])

                    fig = px.bar(importance_df, x='Importance', y='Feature',
                               orientation='h', title="Top 10 Most Important Features")
                    st.plotly_chart(fig, use_container_width=True)

                # Enable recommendations
                st.balloons()

                if st.button("➡️ Generate Recommendations", type="primary"):
                    st.session_state.current_page = 'recommendations'
                    update_workflow_step(4)
                    st.rerun()

            else:
                st.error("❌ Failed to train ML models. Please check your data.")

        except Exception as e:
            st.error(f"Error training models: {str(e)}")

def display_customer_summary(customer_profile):
    """Display a concise customer profile summary"""

    col1, col2 = st.columns(2)

    with col1:
        # Financial summary
        financial = customer_profile.get('financial_profile', {})
        st.write(f"**Income:** {financial.get('annual_income', 'N/A')}")
        st.write(f"**Equity:** {financial.get('available_equity', 'N/A')}")

        # Investment goals
        goals = customer_profile.get('investment_goals', {})
        st.write(f"**Purpose:** {goals.get('primary_purpose', 'N/A')}")
        st.write(f"**Target Yield:** {goals.get('target_yield', 'N/A')}")

    with col2:
        # Preferences
        prefs = customer_profile.get('property_preferences', {})
        price_range = prefs.get('price_range', {})
        st.write(f"**Budget:** ${price_range.get('min', 'N/A')} - ${price_range.get('max', 'N/A')}")

        lifestyle = customer_profile.get('lifestyle_factors', {})
        st.write(f"**CBD Proximity:** {lifestyle.get('proximity_to_cbd', 'N/A')}")
        st.write(f"**School Quality:** {lifestyle.get('school_quality', 'N/A')}")