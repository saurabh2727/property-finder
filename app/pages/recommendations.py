import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from services.openai_service import OpenAIService
from utils.session_state import update_workflow_step
from models.ml_recommender import PropertyRecommendationEngine

def render_recommendations_page():
    """Render the AI/ML recommendations page"""

    st.title("⭐ AI Property Recommendations")
    st.subheader("Machine Learning-Powered Investment Insights")

    # Progress indicator
    progress_cols = st.columns(5)
    with progress_cols[0]:
        st.markdown("✅ Step 1: Customer Profile")
    with progress_cols[1]:
        st.markdown("✅ Step 2: Data Upload")
    with progress_cols[2]:
        st.markdown("✅ Step 3: Analysis")
    with progress_cols[3]:
        st.markdown("🔄 **Step 4: Recommendations**")
    with progress_cols[4]:
        st.markdown("⏳ Step 5: Reports")

    st.markdown("---")

    # Check prerequisites
    if not check_prerequisites():
        return

    # Get data
    df = st.session_state.suburb_data
    customer_profile = st.session_state.customer_profile

    # Check if recommendations already exist
    if st.session_state.get('recommendations') is not None:
        display_existing_recommendations()
    else:
        generate_new_recommendations(df, customer_profile)

def check_prerequisites():
    """Check if all prerequisites are met"""

    if not st.session_state.get('profile_generated', False):
        st.warning("⚠️ Please complete customer profiling first!")
        if st.button("← Go to Customer Profile"):
            st.session_state.current_page = 'customer_profile'
            st.rerun()
        return False

    if not st.session_state.get('data_uploaded', False):
        st.warning("⚠️ Please upload suburb data first!")
        if st.button("← Go to Data Upload"):
            st.session_state.current_page = 'data_upload'
            st.rerun()
        return False

    return True

def generate_new_recommendations(df, customer_profile):
    """Generate new recommendations using ML and AI"""

    st.subheader("🤖 Generate AI Recommendations")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Recommendation Settings")

        # Number of recommendations
        num_recommendations = st.slider("Number of Recommendations", 5, 20, 10)

        # Recommendation approach
        approach = st.selectbox(
            "Recommendation Approach",
            ["Balanced", "Growth Focused", "Yield Focused", "Conservative"]
        )

        # Generate button
        if st.button("🚀 Generate Recommendations", type="primary", use_container_width=True):
            generate_recommendations(df, customer_profile, num_recommendations, approach)

    with col2:
        st.markdown("#### Approach Details")

        approach_details = {
            "Balanced": "Equal weight to yield and growth potential. Best for diversified investors seeking stable returns with moderate growth.",
            "Growth Focused": "Prioritizes capital growth opportunities. Suitable for long-term investors willing to accept lower initial yields for higher appreciation.",
            "Yield Focused": "Emphasizes high rental returns. Ideal for investors seeking immediate cash flow and steady income streams.",
            "Conservative": "Lower risk, stable investment options. Perfect for risk-averse investors prioritizing capital preservation."
        }

        selected_approach = approach_details.get(approach, "")
        st.info(f"**{approach}:** {selected_approach}")

        st.markdown("#### AI Analysis")
        st.write("""
        🤖 **AI Features:**
        - Customer profile analysis
        - Market trend evaluation
        - Risk assessment
        - Investment strategy alignment
        """)

def generate_recommendations(df, customer_profile, num_recommendations, approach):
    """Generate recommendations using AI as primary engine"""

    with st.spinner("🔄 Generating AI recommendations..."):
        try:
            st.info("🔍 **Generation Process:**")
            progress_bar = st.progress(0)
            status_text = st.empty()

            recommendations_data = {}

            # Method 1: AI-based recommendations (PRIMARY)
            status_text.text("🧠 Generating AI recommendations...")
            progress_bar.progress(30)
            status_text.text("🧠 Generating AI analysis...")
            progress_bar.progress(50)

            try:
                openai_service = OpenAIService()
                ai_recommendations = openai_service.generate_suburb_recommendations(
                    customer_profile, df, num_recommendations, approach
                )
                recommendations_data['ai_analysis'] = ai_recommendations

                # Convert AI recommendations to primary ranking
                ai_ranked_suburbs = convert_ai_to_ranked_list(ai_recommendations, df, num_recommendations)

                if ai_ranked_suburbs is not None and len(ai_ranked_suburbs) > 0:
                    recommendations_data['primary_recommendations'] = ai_ranked_suburbs
                    st.success(f"✅ AI recommendations: {len(ai_ranked_suburbs)} suburbs ranked")

                    # Store recommendations and finish
                    st.session_state.recommendations = recommendations_data
                    update_workflow_step(5)

                    progress_bar.progress(100)
                    status_text.text("✅ AI recommendations completed!")
                    st.success(f"🎉 Found {len(ai_ranked_suburbs)} AI-recommended suburbs using {approach.lower()} approach")
                    st.rerun()
                    return

            except Exception as ai_error:
                st.warning(f"⚠️ AI analysis failed: {str(ai_error)}")
                recommendations_data['ai_analysis'] = {}

            # Method 2: Rule-based fallback (only if AI fails)
            status_text.text("📊 Generating rule-based recommendations...")
            progress_bar.progress(75)

            rule_based_recs = generate_rule_based_recommendations(
                df, customer_profile, num_recommendations, approach
            )
            recommendations_data['rule_based'] = rule_based_recs

            progress_bar.progress(100)
            status_text.text("✅ All recommendations generated!")
            st.success(f"🎉 Found {len(rule_based_recs)} recommended suburbs using {approach.lower()} approach")

            # Store recommendations
            st.session_state.recommendations = recommendations_data
            update_workflow_step(5)

            st.success("🎉 Recommendations generated successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating recommendations: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

def convert_ai_to_ranked_list(ai_recommendations, df, num_recommendations):
    """Convert AI recommendations to ranked DataFrame format for display"""

    try:
        ai_suburbs = ai_recommendations.get('recommended_suburbs', [])

        if not ai_suburbs:
            return None

        # Create a list to store matched suburbs with AI data
        ranked_suburbs = []

        for ai_suburb in ai_suburbs[:num_recommendations]:
            suburb_name = ai_suburb.get('suburb_name', '')
            ai_score = float(ai_suburb.get('score', 0))

            # Find matching suburb in original data
            # Try exact match first
            matched_rows = df[df['Suburb'].str.contains(suburb_name, case=False, na=False)]

            if matched_rows.empty:
                # Try partial match
                for _, row in df.iterrows():
                    if suburb_name.lower() in str(row['Suburb']).lower():
                        matched_rows = pd.DataFrame([row])
                        break

            if not matched_rows.empty:
                # Take the first match
                suburb_row = matched_rows.iloc[0].copy()

                # Add AI-specific data
                suburb_row['AI_Score'] = ai_score
                suburb_row['AI_Reasons'] = '; '.join(ai_suburb.get('reasons', []))
                suburb_row['Investment_Potential'] = ai_suburb.get('investment_potential', 'medium')
                suburb_row['Rank'] = len(ranked_suburbs) + 1

                ranked_suburbs.append(suburb_row)

        if ranked_suburbs:
            result_df = pd.DataFrame(ranked_suburbs)
            result_df = result_df.sort_values('AI_Score', ascending=False).reset_index(drop=True)
            result_df['Rank'] = range(1, len(result_df) + 1)
            return result_df

        return None

    except Exception as e:
        st.error(f"Error converting AI recommendations: {e}")
        return None

def generate_rule_based_recommendations(df, customer_profile, num_recommendations, approach):
    """Generate rule-based recommendations as fallback"""

    try:
        df_scored = df.copy()

        # Calculate composite scores based on approach
        if approach == "Growth Focused":
            weights = {"growth": 0.6, "yield": 0.2, "price": 0.1, "distance": 0.1}
        elif approach == "Yield Focused":
            weights = {"growth": 0.2, "yield": 0.6, "price": 0.1, "distance": 0.1}
        elif approach == "Conservative":
            weights = {"growth": 0.3, "yield": 0.3, "price": 0.2, "distance": 0.2}
        else:  # Balanced
            weights = {"growth": 0.3, "yield": 0.3, "price": 0.2, "distance": 0.2}

        # Score calculation
        composite_score = 0

        if '10 yr Avg. Annual Growth' in df.columns:
            growth_col = df_scored['10 yr Avg. Annual Growth'].fillna(0)
            growth_min, growth_max = growth_col.min(), growth_col.max()
            if growth_max > growth_min:
                growth_norm = (growth_col - growth_min) / (growth_max - growth_min)
                composite_score += growth_norm * weights["growth"]

        if 'Rental Yield on Houses' in df.columns:
            yield_col = df_scored['Rental Yield on Houses'].fillna(0)
            yield_min, yield_max = yield_col.min(), yield_col.max()
            if yield_max > yield_min:
                yield_norm = (yield_col - yield_min) / (yield_max - yield_min)
                composite_score += yield_norm * weights["yield"]

        if 'Median Price' in df.columns:
            price_col = df_scored['Median Price'].fillna(df_scored['Median Price'].median())
            price_min, price_max = price_col.min(), price_col.max()
            if price_max > price_min:
                # Price score (inverse - lower prices score higher for affordability)
                price_inv = 1 - (price_col - price_min) / (price_max - price_min)
                composite_score += price_inv * weights["price"]

        if 'Distance (km) to CBD' in df.columns:
            distance_col = df_scored['Distance (km) to CBD'].fillna(df_scored['Distance (km) to CBD'].median())
            distance_min, distance_max = distance_col.min(), distance_col.max()
            if distance_max > distance_min:
                # Distance score (inverse - closer is better)
                distance_inv = 1 - (distance_col - distance_min) / (distance_max - distance_min)
                composite_score += distance_inv * weights["distance"]

        df_scored['Composite_Score'] = composite_score

        # Apply customer filters
        df_filtered = apply_customer_constraints(df_scored, customer_profile)

        # Return top recommendations
        result = df_filtered.nlargest(num_recommendations, 'Composite_Score')
        return result

    except Exception as e:
        st.error(f"❌ Error in rule-based recommendations: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()  # Return empty dataframe on error

def apply_customer_constraints(df, customer_profile):
    """Apply customer-specific constraints"""

    df_filtered = df.copy()

    # Budget constraints
    price_prefs = customer_profile.get('property_preferences', {}).get('price_range', {})
    if price_prefs.get('min') and price_prefs.get('max') and 'Median Price' in df.columns:
        try:
            min_price = float(str(price_prefs['min']).replace('$', '').replace(',', ''))
            max_price = float(str(price_prefs['max']).replace('$', '').replace(',', ''))

            # Apply with 20% flexibility
            df_filtered = df_filtered[
                (df_filtered['Median Price'] >= min_price * 0.8) &
                (df_filtered['Median Price'] <= max_price * 1.2)
            ]
        except (ValueError, TypeError):
            pass

    return df_filtered

def display_existing_recommendations():
    """Display existing recommendations with analysis"""

    st.success("✅ AI recommendations have been generated!")

    recommendations = st.session_state.recommendations

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.recommendations = None
            st.rerun()

    with col2:
        if st.button("➡️ Generate Reports", type="primary", use_container_width=True):
            st.session_state.current_page = 'reports'
            update_workflow_step(5)
            st.rerun()

    with col3:
        if st.button("📊 Export Data", use_container_width=True):
            export_recommendations(recommendations)

    st.markdown("---")

    # Display recommendations in tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Top Recommendations", "🤖 AI Analysis", "📊 Detailed Insights"])

    with tab1:
        display_top_recommendations(recommendations)

    with tab2:
        display_ai_analysis(recommendations)

    with tab3:
        display_detailed_insights(recommendations)

def display_top_recommendations(recommendations):
    """Display top suburb recommendations"""

    st.subheader("🏆 Recommended Suburbs")

    # Summary insights - prioritize AI recommendations
    ai_recs = recommendations.get('primary_recommendations')
    ml_recs = recommendations.get('ml_recommendations')
    rule_recs = recommendations.get('rule_based')

    # Use AI first, then ML, then rule-based as fallback
    if ai_recs is not None and not ai_recs.empty:
        top_suburbs = ai_recs
        engine_type = "🤖 AI-Powered"
    elif ml_recs is not None and not ml_recs.empty:
        top_suburbs = ml_recs
        engine_type = "🤖 ML-Powered"
    else:
        top_suburbs = rule_recs
        engine_type = "📊 Rule-Based"

    if top_suburbs is not None and not top_suburbs.empty:
        # Show engine type
        st.info(f"**Recommendation Engine:** {engine_type}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            avg_price = top_suburbs['Median Price'].mean() if 'Median Price' in top_suburbs.columns else 0
            st.metric("Average Price", f"${avg_price:,.0f}")

        with col2:
            avg_yield = top_suburbs['Rental Yield on Houses'].mean() if 'Rental Yield on Houses' in top_suburbs.columns else 0
            st.metric("Average Yield", f"{avg_yield:.1f}%")

        with col3:
            avg_growth = top_suburbs['10 yr Avg. Annual Growth'].mean() if '10 yr Avg. Annual Growth' in top_suburbs.columns else 0
            st.metric("Average Growth", f"{avg_growth:.1f}%")

        with col4:
            states = top_suburbs['State'].nunique() if 'State' in top_suburbs.columns else 0
            st.metric("States Covered", states)

        st.markdown("---")

    # Get the best recommendations
    ml_recs = recommendations.get('ml_recommendations')
    rule_recs = recommendations.get('rule_based')

    # Use ML recommendations if available, otherwise rule-based
    top_suburbs = ml_recs if ml_recs is not None and not ml_recs.empty else rule_recs

    if top_suburbs is None or top_suburbs.empty:
        st.warning("No recommendations available. Please regenerate.")
        return

    # Display top suburbs with enhanced information
    for idx, (_, suburb) in enumerate(top_suburbs.head(10).iterrows(), 1):
        suburb_name = suburb.get('Suburb', 'Unknown')
        state = suburb.get('State', '')

        # Create a score indicator
        score_indicator = ""
        if 'Investment_Score_Predicted' in suburb:
            score = suburb['Investment_Score_Predicted']
            if score > 0.7:
                score_indicator = "🌟"
            elif score > 0.5:
                score_indicator = "⭐"
            else:
                score_indicator = "📊"
        elif 'Composite_Score' in suburb:
            score = suburb['Composite_Score']
            if score > 0.7:
                score_indicator = "🏆"
            elif score > 0.5:
                score_indicator = "🥈"
            else:
                score_indicator = "🥉"

        with st.expander(f"{idx}. {score_indicator} {suburb_name}, {state}", expanded=idx <= 3):

            col1, col2 = st.columns([2, 1])

            with col1:
                # Key metrics
                st.markdown("#### 📊 Key Metrics")

                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    if 'Median Price' in suburb:
                        st.metric("Median Price", f"${suburb['Median Price']:,.0f}")
                    if 'Rental Yield on Houses' in suburb:
                        st.metric("Rental Yield", f"{suburb['Rental Yield on Houses']:.1f}%")

                with metric_col2:
                    if '10 yr Avg. Annual Growth' in suburb:
                        st.metric("10yr Growth", f"{suburb['10 yr Avg. Annual Growth']:.1f}%")
                    if 'Distance (km) to CBD' in suburb:
                        st.metric("Distance to CBD", f"{suburb['Distance (km) to CBD']:.0f} km")

                # Investment potential
                if 'Investment_Score_Predicted' in suburb:
                    score = suburb['Investment_Score_Predicted']
                    # Normalize score to 0-1 range for progress bar
                    normalized_score = max(0.0, min(1.0, score))
                    st.progress(normalized_score)
                    st.caption(f"ML Investment Score: {score:.2f}")

            with col2:
                # Cash flow projection
                st.markdown("#### 💰 Cash Flow Projection")

                if 'Median Price' in suburb and 'Rental Yield on Houses' in suburb:
                    price = suburb['Median Price']
                    yield_rate = suburb['Rental Yield on Houses'] / 100

                    # Simple cash flow calculation
                    annual_rent = price * yield_rate
                    monthly_rent = annual_rent / 12

                    # Approximate expenses (30% of rent)
                    net_monthly = monthly_rent * 0.7

                    st.write(f"**Gross Rent:** ${monthly_rent:,.0f}/month")
                    st.write(f"**Net Cash Flow:** ${net_monthly:,.0f}/month")

                    # ROI calculation
                    deposit_20 = price * 0.2
                    annual_net = net_monthly * 12
                    roi = (annual_net / deposit_20) * 100 if deposit_20 > 0 else 0

                    st.metric("Estimated ROI", f"{roi:.1f}%")

    # Comparison chart
    st.subheader("📈 Recommendation Comparison")
    create_comparison_chart(top_suburbs.head(5))

def create_comparison_chart(top_suburbs):
    """Create comparison chart for top recommendations"""

    if top_suburbs.empty:
        st.info("No data available for comparison chart")
        return

    # Multi-metric comparison
    metrics = []
    if 'Rental Yield on Houses' in top_suburbs.columns:
        metrics.append('Rental Yield on Houses')
    if '10 yr Avg. Annual Growth' in top_suburbs.columns:
        metrics.append('10 yr Avg. Annual Growth')

    if not metrics:
        st.info("Insufficient data for comparison chart")
        return

    # Create subplot
    fig = go.Figure()

    suburbs = top_suburbs['Suburb'].tolist() if 'Suburb' in top_suburbs.columns else [f"Suburb {i+1}" for i in range(len(top_suburbs))]

    for metric in metrics:
        fig.add_trace(go.Bar(
            name=metric,
            x=suburbs,
            y=top_suburbs[metric].tolist(),
        ))

    fig.update_layout(
        title="Top Suburbs Comparison",
        xaxis_title="Suburbs",
        yaxis_title="Value",
        barmode='group',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def display_ai_analysis(recommendations):
    """Display AI-generated analysis"""

    st.subheader("🤖 AI Investment Analysis")

    ai_analysis = recommendations.get('ai_analysis', {})

    if not ai_analysis:
        st.info("No AI analysis available")
        return

    # Investment strategy
    strategy = ai_analysis.get('investment_strategy', 'N/A')
    st.markdown(f"#### 🎯 Recommended Investment Strategy")
    st.info(strategy)

    # Risk assessment
    risk_assessment = ai_analysis.get('risk_assessment', 'N/A')
    st.markdown(f"#### ⚠️ Risk Assessment")
    st.warning(risk_assessment)

    # AI recommended suburbs
    ai_suburbs = ai_analysis.get('recommended_suburbs', [])
    if ai_suburbs:
        st.markdown("#### 🏘️ AI Top Picks")

        for idx, suburb_info in enumerate(ai_suburbs[:5], 1):
            with st.expander(f"{idx}. {suburb_info.get('suburb_name', 'Unknown')}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Score:** {suburb_info.get('score', 'N/A')}")
                    st.write(f"**Investment Potential:** {suburb_info.get('investment_potential', 'N/A')}")

                with col2:
                    key_metrics = suburb_info.get('key_metrics', {})
                    for metric, value in key_metrics.items():
                        st.write(f"**{metric.replace('_', ' ').title()}:** {value}")

                reasons = suburb_info.get('reasons', [])
                if reasons:
                    st.markdown("**Why this suburb:**")
                    for reason in reasons:
                        st.write(f"• {reason}")

    # Next steps
    next_steps = ai_analysis.get('next_steps', [])
    if next_steps:
        st.markdown("#### 📋 Next Steps")
        for step in next_steps:
            st.write(f"• {step}")

def display_detailed_insights(recommendations):
    """Display detailed insights and analytics"""

    st.subheader("📊 Detailed Investment Insights")

    # Get recommendations data
    ml_recs = recommendations.get('ml_recommendations')
    rule_recs = recommendations.get('rule_based')

    # Use best available data
    data = ml_recs if ml_recs is not None and not ml_recs.empty else rule_recs

    if data is None or data.empty:
        st.info("No detailed insights available")
        return

    # Market analysis
    tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Risk Analysis", "Performance Metrics", "ML Explainability"])

    with tab1:
        display_market_overview(data)

    with tab2:
        display_risk_analysis(data)

    with tab3:
        display_performance_metrics(data)

    with tab4:
        display_ml_explainability(recommendations)

def display_market_overview(data):
    """Display market overview analysis"""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Price Distribution")
        if 'Median Price' in data.columns:
            fig = px.histogram(data, x='Median Price', title="Recommended Suburbs - Price Range")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Geographic Spread")
        if 'State' in data.columns:
            state_counts = data['State'].value_counts()
            fig = px.pie(values=state_counts.values, names=state_counts.index,
                        title="Recommendations by State")
            st.plotly_chart(fig, use_container_width=True)

    # Summary statistics
    st.markdown("#### Summary Statistics")
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.dataframe(data[numeric_cols].describe(), use_container_width=True)

def display_risk_analysis(data):
    """Display risk analysis"""

    st.markdown("#### Investment Risk Assessment")

    # Price volatility analysis
    if 'Median Price' in data.columns:
        price_std = data['Median Price'].std()
        price_mean = data['Median Price'].mean()
        price_cv = (price_std / price_mean) * 100 if price_mean > 0 else 0

        st.metric("Price Volatility (CV)", f"{price_cv:.1f}%")

        if price_cv < 20:
            st.success("✅ Low price volatility - Stable market")
        elif price_cv < 40:
            st.warning("⚠️ Moderate price volatility")
        else:
            st.error("🔴 High price volatility - Higher risk")

    # Yield stability
    if 'Rental Yield on Houses' in data.columns:
        yield_std = data['Rental Yield on Houses'].std()
        yield_mean = data['Rental Yield on Houses'].mean()

        st.metric("Average Yield", f"{yield_mean:.2f}%")
        st.metric("Yield Standard Deviation", f"{yield_std:.2f}%")

    # Distance risk assessment
    if 'Distance (km) to CBD' in data.columns:
        avg_distance = data['Distance (km) to CBD'].mean()
        st.metric("Average Distance to CBD", f"{avg_distance:.0f} km")

        if avg_distance < 15:
            st.success("✅ Close to CBD - Lower location risk")
        elif avg_distance < 30:
            st.info("ℹ️ Moderate distance - Medium location risk")
        else:
            st.warning("⚠️ Far from CBD - Higher location risk")

def display_performance_metrics(data):
    """Display performance metrics"""

    st.markdown("#### Performance Metrics")

    if len(data) == 0:
        st.info("No performance data available")
        return

    # Key performance indicators
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'Rental Yield on Houses' in data.columns:
            max_yield = data['Rental Yield on Houses'].max()
            avg_yield = data['Rental Yield on Houses'].mean()
            st.metric("Highest Yield", f"{max_yield:.1f}%")
            st.metric("Average Yield", f"{avg_yield:.1f}%")

    with col2:
        if '10 yr Avg. Annual Growth' in data.columns:
            max_growth = data['10 yr Avg. Annual Growth'].max()
            avg_growth = data['10 yr Avg. Annual Growth'].mean()
            st.metric("Highest Growth", f"{max_growth:.1f}%")
            st.metric("Average Growth", f"{avg_growth:.1f}%")

    with col3:
        if 'Median Price' in data.columns:
            min_price = data['Median Price'].min()
            max_price = data['Median Price'].max()
            st.metric("Most Affordable", f"${min_price:,.0f}")
            st.metric("Most Expensive", f"${max_price:,.0f}")

    # Performance comparison
    if len(data) > 1:
        st.markdown("#### Performance Comparison")

        performance_metrics = []
        for metric in ['Rental Yield on Houses', '10 yr Avg. Annual Growth']:
            if metric in data.columns:
                performance_metrics.append(metric)

        if performance_metrics:
            # Correlation matrix
            corr_data = data[performance_metrics + ['Median Price']].corr()
            fig = px.imshow(corr_data, text_auto=True, aspect="auto",
                          title="Metric Correlations")
            st.plotly_chart(fig, use_container_width=True)

def export_recommendations(recommendations):
    """Export recommendations to various formats"""

    st.subheader("📥 Export Recommendations")

    # Prepare export data
    export_data = {}

    if 'ml_recommendations' in recommendations and recommendations['ml_recommendations'] is not None:
        export_data['ML_Recommendations'] = recommendations['ml_recommendations']

    if 'rule_based' in recommendations and recommendations['rule_based'] is not None:
        export_data['Rule_Based_Recommendations'] = recommendations['rule_based']

    if 'ai_analysis' in recommendations:
        export_data['AI_Analysis'] = recommendations['ai_analysis']

    # CSV export for numerical data
    if export_data:
        # Export ML/Rule-based recommendations as CSV
        for key, data in export_data.items():
            if isinstance(data, pd.DataFrame) and not data.empty:
                csv_data = data.to_csv(index=False)
                st.download_button(
                    f"📄 Download {key.replace('_', ' ')} (CSV)",
                    csv_data,
                    f"{key.lower()}.csv",
                    "text/csv",
                    key=f"download_{key}"
                )

        st.success("✅ Export options generated!")

def display_ml_explainability(recommendations):
    """Display ML model explainability features"""
    st.subheader("🔍 Machine Learning Model Explainability")

    # Initialize ML engine if we have data
    if not st.session_state.get('suburb_data') is None and not st.session_state.get('customer_profile') is None:
        try:
            ml_engine = PropertyRecommendationEngine()

            # Check if we have ML recommendations (indicates model was trained)
            ml_recs = recommendations.get('ml_recommendations')

            if ml_recs is not None and not ml_recs.empty:
                st.info("🤖 ML model has been trained for these recommendations")

                # Try to retrain model for explainability
                with st.spinner("🔄 Preparing model explainability..."):
                    df = st.session_state.suburb_data
                    customer_profile = st.session_state.customer_profile

                    # Train the model
                    training_success = ml_engine.train_models(df, customer_profile)

                    if training_success:
                        st.success("✅ Model ready for explainability analysis")

                        # Feature Importance Section
                        st.markdown("### 📊 Feature Importance")
                        col1, col2 = st.columns(2)

                        with col1:
                            # Display feature importance chart
                            importance_chart = ml_engine.create_feature_importance_chart()
                            if importance_chart:
                                st.plotly_chart(importance_chart, use_container_width=True)
                            else:
                                st.info("Feature importance chart not available")

                        with col2:
                            # Display SHAP summary plot
                            shap_chart = ml_engine.create_shap_summary_plot()
                            if shap_chart:
                                st.plotly_chart(shap_chart, use_container_width=True)
                            else:
                                st.info("SHAP analysis not available (requires shap package)")

                        # Model Insights
                        st.markdown("### 🧠 Model Insights")
                        insights = ml_engine.get_model_insights()

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Features Used", insights.get('feature_count', 'N/A'))
                        with col2:
                            st.metric("Model Score", f"{insights.get('latest_model_score', 'N/A'):.3f}" if isinstance(insights.get('latest_model_score'), (int, float)) else 'N/A')
                        with col3:
                            st.metric("SHAP Available", "✅" if insights.get('shap_available', False) else "❌")

                        # Top Contributing Features
                        if insights.get('top_features'):
                            st.markdown("### 🏆 Top Contributing Features")
                            for i, feature in enumerate(insights['top_features'], 1):
                                st.write(f"{i}. **{feature}**")

                        # Individual Suburb Explanation
                        st.markdown("### 🔍 Individual Suburb Explanation")

                        # Let user select a suburb for detailed explanation
                        available_suburbs = ml_recs['Suburb'].tolist() if 'Suburb' in ml_recs.columns else []

                        if available_suburbs:
                            selected_suburb = st.selectbox(
                                "Select a suburb for detailed SHAP explanation:",
                                available_suburbs
                            )

                            if selected_suburb:
                                # Get the suburb data
                                suburb_row = ml_recs[ml_recs['Suburb'] == selected_suburb].iloc[0]

                                # Get SHAP explanation
                                shap_explanation = ml_engine.get_shap_explanation(suburb_row)

                                if shap_explanation:
                                    st.markdown(f"#### SHAP Analysis for {selected_suburb}")

                                    # Display SHAP values
                                    for feature, impact in shap_explanation.items():
                                        direction = "📈" if impact['impact_direction'] == 'positive' else "📉"
                                        st.write(f"{direction} **{feature}**: {impact['shap_value']:.4f} (value: {impact['feature_value']:.2f})")

                                else:
                                    st.info("SHAP explanation not available for this suburb")

                        # Training History
                        if insights.get('training_history'):
                            st.markdown("### 📈 Model Training History")
                            with st.expander("View Training Log"):
                                for entry in insights['training_history'][-3:]:  # Show last 3 entries
                                    st.json(entry)

                    else:
                        st.warning("⚠️ Could not train ML model for explainability")

            else:
                st.info("🔄 No ML recommendations available. ML explainability requires model training.")
                st.write("To see ML explainability features:")
                st.write("1. Ensure you have sufficient data (>10 suburbs)")
                st.write("2. Regenerate recommendations with ML enabled")

        except Exception as e:
            st.error(f"❌ Error in ML explainability: {str(e)}")
            with st.expander("Error Details"):
                import traceback
                st.code(traceback.format_exc())

    else:
        st.info("📊 ML explainability requires both customer profile and suburb data to be loaded.")