import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
import tempfile
import os
from utils.session_state import backup_session_data, render_workflow_progress
from styles.global_styles import get_global_css, COLORS
from components.property_card import render_hero_section

def render_reports_page():
    """Render the comprehensive reports page"""

    # Inject global CSS
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Hero Section
    render_hero_section(
        title="📋 Comprehensive Property Reports",
        subtitle="Professional investment analysis and client presentations"
    )

    # Progress indicator
    render_workflow_progress(current_step=4)

    st.markdown("---")

    # Check prerequisites
    if not check_prerequisites():
        return

    # Report generation options
    tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "📈 Detailed Analysis", "📄 Custom Reports"])

    with tab1:
        render_executive_summary()

    with tab2:
        render_detailed_analysis()

    with tab3:
        render_custom_reports()

def check_prerequisites():
    """Check if all required data is available with session recovery"""

    # Import session management functions
    from utils.session_state import recover_session_data

    # Try to recover session data if missing
    if not st.session_state.get('recommendations') and not st.session_state.get('profile_generated'):
        if recover_session_data():
            st.info("🔄 Session data recovered successfully!")

    missing_components = []

    if not st.session_state.get('profile_generated', False):
        missing_components.append("Customer Profile")

    if not st.session_state.get('data_uploaded', False):
        missing_components.append("Suburb Data")

    if st.session_state.get('recommendations') is None:
        missing_components.append("Recommendations")

    if missing_components:
        st.warning(f"⚠️ Missing required components: {', '.join(missing_components)}")

        # Show session recovery option
        with st.expander("🔧 Troubleshooting"):
            st.write("**Session Status:**")
            st.write(f"- Profile Generated: {'✅' if st.session_state.get('profile_generated') else '❌'}")
            st.write(f"- Data Uploaded: {'✅' if st.session_state.get('data_uploaded') else '❌'}")
            st.write(f"- Recommendations Available: {'✅' if st.session_state.get('recommendations') else '❌'}")
            st.write(f"- Backup Available: {'✅' if st.session_state.get('session_backup_available') else '❌'}")

            if st.button("🔄 Try Session Recovery"):
                if recover_session_data():
                    st.success("✅ Data recovered!")
                    st.rerun()
                else:
                    st.warning("⚠️ No recoverable data found")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Customer Profile"):
                st.session_state.current_page = 'customer_profile'
                st.rerun()

        with col2:
            if st.button("← Data Upload"):
                st.session_state.current_page = 'data_upload'
                st.rerun()

        with col3:
            if st.button("← Recommendations"):
                st.session_state.current_page = 'recommendations'
                st.rerun()

        return False

    return True

def render_executive_summary():
    """Render executive summary report"""

    st.subheader("📊 Executive Summary Report")

    # Generate and display executive summary
    generate_executive_summary()

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Generate PDF Report", use_container_width=True, key="pdf_standard_report"):
            generate_pdf_report()

    with col2:
        if st.button("📧 Email Report", use_container_width=True, key="email_standard_report"):
            st.info("Email functionality coming soon!")

    with col3:
        if st.button("💾 Save Report", use_container_width=True, key="save_standard_report"):
            save_report_data()

def generate_executive_summary():
    """Generate executive summary with key insights"""

    customer_profile = st.session_state.customer_profile
    recommendations = st.session_state.recommendations
    suburb_data = st.session_state.suburb_data

    # Report header
    st.markdown("---")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## Property Investment Analysis Report")
        st.markdown(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}")
        st.markdown(f"**Prepared for:** {customer_profile.get('additional_notes', 'Valued Client')}")

    with col2:
        st.image("https://via.placeholder.com/150x100/FF6B6B/FFFFFF?text=Property+Insight", width=150)

    st.markdown("---")

    # Customer profile summary
    st.markdown("### 👤 Client Profile Summary")

    col1, col2 = st.columns(2)

    with col1:
        financial = customer_profile.get('financial_profile', {})
        st.markdown(f"""
        **Financial Profile:**
        - Annual Income: {financial.get('annual_income', 'Not specified')}
        - Available Equity: {financial.get('available_equity', 'Not specified')}
        - Investment Budget: {get_budget_range(customer_profile)}
        """)

        investment_goals = customer_profile.get('investment_goals', {})
        st.markdown(f"""
        **Investment Objectives:**
        - Primary Purpose: {investment_goals.get('primary_purpose', 'Not specified')}
        - Target Yield: {investment_goals.get('target_yield', 'Not specified')}
        - Risk Tolerance: {investment_goals.get('risk_tolerance', 'Not specified')}
        """)

    with col2:
        preferences = customer_profile.get('property_preferences', {})
        lifestyle = customer_profile.get('lifestyle_factors', {})

        st.markdown(f"""
        **Property Preferences:**
        - Property Types: {', '.join(preferences.get('property_types', ['Not specified']))}
        - Bedroom Range: {preferences.get('bedroom_range', 'Not specified')}
        """)

        st.markdown(f"""
        **Location Priorities:**
        - CBD Proximity: {lifestyle.get('proximity_to_cbd', 'Not specified')}
        - School Quality: {lifestyle.get('school_quality', 'Not specified')}
        - Transport Access: {lifestyle.get('transport_access', 'Not specified')}
        """)

    # Market analysis summary
    st.markdown("### 📊 Market Analysis Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_suburbs = len(suburb_data) if suburb_data is not None else 0
        st.metric("Total Suburbs Analyzed", total_suburbs)

    with col2:
        if suburb_data is not None and 'Median Price' in suburb_data.columns:
            avg_price = suburb_data['Median Price'].mean()
            st.metric("Average Median Price", f"${avg_price:,.0f}")

    with col3:
        if suburb_data is not None and 'Rental Yield on Houses' in suburb_data.columns:
            avg_yield = suburb_data['Rental Yield on Houses'].mean()
            st.metric("Average Rental Yield", f"{avg_yield:.1f}%")

    with col4:
        # Number of recommendations
        num_recs = get_recommendation_count(recommendations)
        st.metric("Recommendations Generated", num_recs)

    # Top recommendations summary
    st.markdown("### 🏆 Top Investment Recommendations")

    top_recs = get_top_recommendations(recommendations, 5)

    if not top_recs.empty:
        for idx, (_, suburb) in enumerate(top_recs.iterrows(), 1):
            with st.expander(f"#{idx} {suburb.get('Suburb', 'Unknown')}, {suburb.get('State', '')}"):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Investment Metrics**")
                    if 'Median Price' in suburb:
                        st.write(f"Price: ${suburb['Median Price']:,.0f}")
                    if 'Rental Yield on Houses' in suburb:
                        st.write(f"Yield: {suburb['Rental Yield on Houses']:.1f}%")

                with col2:
                    st.markdown("**Growth Potential**")
                    if '10 yr Avg. Annual Growth' in suburb:
                        st.write(f"10yr Growth: {suburb['10 yr Avg. Annual Growth']:.1f}%")
                    if 'Distance (km) to CBD' in suburb:
                        st.write(f"CBD Distance: {suburb['Distance (km) to CBD']:.0f}km")

                with col3:
                    st.markdown("**Cash Flow Projection**")
                    if 'Median Price' in suburb and 'Rental Yield on Houses' in suburb:
                        monthly_rent = (suburb['Median Price'] * suburb['Rental Yield on Houses'] / 100) / 12
                        st.write(f"Gross Rent: ${monthly_rent:,.0f}/month")
                        net_rent = monthly_rent * 0.7  # Assume 30% expenses
                        st.write(f"Net Cash Flow: ${net_rent:,.0f}/month")

    # Investment strategy recommendations
    st.markdown("### 🎯 Investment Strategy Recommendations")

    ai_analysis = recommendations.get('ai_analysis', {})
    strategy = ai_analysis.get('investment_strategy', 'No specific strategy provided')
    risk_assessment = ai_analysis.get('risk_assessment', 'Risk assessment not available')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Recommended Strategy:**")
        st.info(strategy)

    with col2:
        st.markdown("**Risk Assessment:**")
        st.warning(risk_assessment)

    # Next steps
    st.markdown("### 📋 Recommended Next Steps")

    next_steps = ai_analysis.get('next_steps', [
        "Review detailed suburb analysis",
        "Conduct property inspections",
        "Obtain pre-approval for financing",
        "Engage with local real estate agents",
        "Consider professional property management"
    ])

    for i, step in enumerate(next_steps, 1):
        st.write(f"{i}. {step}")

    # Disclaimer
    st.markdown("---")
    st.markdown("### ⚠️ Important Disclaimer")
    st.caption("""
    This report is generated using AI and machine learning algorithms based on available market data.
    It is intended for informational purposes only and should not be considered as financial advice.
    Please consult with qualified financial advisors and conduct independent due diligence before making investment decisions.
    Past performance does not guarantee future results.
    """)

def render_detailed_analysis():
    """Render detailed analysis report"""

    st.subheader("📈 Detailed Market Analysis")

    suburb_data = st.session_state.suburb_data
    recommendations = st.session_state.recommendations

    if suburb_data is None or suburb_data.empty:
        st.warning("No suburb data available for detailed analysis")
        return

    # Market trends analysis
    st.markdown("### 📊 Market Trends Analysis")

    tab1, tab2, tab3, tab4 = st.tabs(["Price Trends", "Yield Analysis", "Growth Patterns", "Risk Assessment"])

    with tab1:
        render_price_trends_analysis(suburb_data)

    with tab2:
        render_yield_analysis_detailed(suburb_data)

    with tab3:
        render_growth_patterns_analysis(suburb_data)

    with tab4:
        render_risk_assessment_detailed(suburb_data, recommendations)

def render_price_trends_analysis(suburb_data):
    """Render detailed price trends analysis"""

    st.markdown("#### 💰 Price Distribution Analysis")

    if 'Median Price' not in suburb_data.columns:
        st.info("Price data not available")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Price distribution histogram
        fig = px.histogram(
            suburb_data,
            x='Median Price',
            nbins=30,
            title="Median Price Distribution",
            labels={'x': 'Median Price ($)', 'y': 'Number of Suburbs'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Price by state box plot
        if 'State' in suburb_data.columns:
            fig = px.box(
                suburb_data,
                x='State',
                y='Median Price',
                title="Price Distribution by State"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Price statistics
    price_stats = suburb_data['Median Price'].describe()
    st.markdown("#### 📊 Price Statistics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Minimum", f"${price_stats['min']:,.0f}")
    with col2:
        st.metric("Median", f"${price_stats['50%']:,.0f}")
    with col3:
        st.metric("Mean", f"${price_stats['mean']:,.0f}")
    with col4:
        st.metric("Maximum", f"${price_stats['max']:,.0f}")

def render_yield_analysis_detailed(suburb_data):
    """Render detailed yield analysis"""

    st.markdown("#### 📈 Rental Yield Analysis")

    if 'Rental Yield on Houses' not in suburb_data.columns:
        st.info("Rental yield data not available")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Yield distribution
        fig = px.histogram(
            suburb_data,
            x='Rental Yield on Houses',
            nbins=30,
            title="Rental Yield Distribution",
            labels={'x': 'Rental Yield (%)', 'y': 'Number of Suburbs'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Yield vs Price scatter
        if 'Median Price' in suburb_data.columns:
            fig = px.scatter(
                suburb_data,
                x='Median Price',
                y='Rental Yield on Houses',
                color='State' if 'State' in suburb_data.columns else None,
                title="Rental Yield vs Median Price"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Yield categories
    yield_col = suburb_data['Rental Yield on Houses']
    high_yield = len(yield_col[yield_col >= 6])
    medium_yield = len(yield_col[(yield_col >= 4) & (yield_col < 6)])
    low_yield = len(yield_col[yield_col < 4])

    st.markdown("#### 🎯 Yield Categories")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("High Yield (≥6%)", high_yield)
    with col2:
        st.metric("Medium Yield (4-6%)", medium_yield)
    with col3:
        st.metric("Low Yield (<4%)", low_yield)

def render_growth_patterns_analysis(suburb_data):
    """Render growth patterns analysis"""

    st.markdown("#### 📊 Historical Growth Analysis")

    if '10 yr Avg. Annual Growth' not in suburb_data.columns:
        st.info("Growth data not available")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Growth distribution
        fig = px.histogram(
            suburb_data,
            x='10 yr Avg. Annual Growth',
            nbins=30,
            title="10-Year Average Growth Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Growth vs Distance correlation
        if 'Distance (km) to CBD' in suburb_data.columns:
            fig = px.scatter(
                suburb_data,
                x='Distance (km) to CBD',
                y='10 yr Avg. Annual Growth',
                title="Growth Rate vs Distance to CBD"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Growth performance tiers
    growth_col = suburb_data['10 yr Avg. Annual Growth']
    high_growth = len(growth_col[growth_col >= 7])
    medium_growth = len(growth_col[(growth_col >= 5) & (growth_col < 7)])
    low_growth = len(growth_col[growth_col < 5])

    st.markdown("#### 🚀 Growth Performance Tiers")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("High Growth (≥7%)", high_growth)
    with col2:
        st.metric("Medium Growth (5-7%)", medium_growth)
    with col3:
        st.metric("Low Growth (<5%)", low_growth)

def render_risk_assessment_detailed(suburb_data, recommendations):
    """Render detailed risk assessment"""

    st.markdown("#### ⚠️ Investment Risk Analysis")

    # Portfolio diversification analysis
    if 'State' in suburb_data.columns:
        state_distribution = suburb_data['State'].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                values=state_distribution.values,
                names=state_distribution.index,
                title="Geographic Diversification"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Risk metrics
            st.markdown("**Risk Indicators:**")

            if 'Median Price' in suburb_data.columns:
                price_cv = (suburb_data['Median Price'].std() / suburb_data['Median Price'].mean()) * 100
                st.write(f"Price Volatility: {price_cv:.1f}%")

            if 'Rental Yield on Houses' in suburb_data.columns:
                yield_stability = suburb_data['Rental Yield on Houses'].std()
                st.write(f"Yield Stability: ±{yield_stability:.1f}%")

            if 'Vacancy Rate' in suburb_data.columns:
                avg_vacancy = suburb_data['Vacancy Rate'].mean()
                st.write(f"Average Vacancy: {avg_vacancy:.1f}%")

    # Risk categorization of recommendations
    top_recs = get_top_recommendations(recommendations, 10)
    if not top_recs.empty:
        st.markdown("#### 🎯 Recommendation Risk Profile")

        risk_categories = categorize_risk_levels(top_recs)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Low Risk", risk_categories.get('low', 0))
        with col2:
            st.metric("Medium Risk", risk_categories.get('medium', 0))
        with col3:
            st.metric("High Risk", risk_categories.get('high', 0))

def render_custom_reports():
    """Render custom report generation options"""

    st.subheader("📄 Custom Report Generation")

    # Report customization options
    st.markdown("### 🎨 Customize Your Report")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Report Sections")
        include_executive = st.checkbox("Executive Summary", value=True)
        include_customer = st.checkbox("Customer Profile", value=True)
        include_market = st.checkbox("Market Analysis", value=True)
        include_recommendations = st.checkbox("Recommendations", value=True)
        include_risk = st.checkbox("Risk Assessment", value=True)
        include_cashflow = st.checkbox("Cash Flow Projections", value=True)

    with col2:
        st.markdown("#### Report Format")
        report_format = st.selectbox("Format", ["PDF", "HTML", "Word Document", "Excel", "Suburb One-Pagers"])

        # Special options for suburb one-pagers
        if report_format == "Suburb One-Pagers":
            st.info("📄 Generate individual one-page reports for each recommended suburb")
            max_suburbs = st.slider("Max Suburbs to Include", 3, 10, 5)
            one_pager_style = st.selectbox("One-Pager Style", ["Executive", "Detailed", "Investor Brief"])
        else:
            max_suburbs = None
            one_pager_style = None

        st.markdown("#### Additional Options")
        include_charts = st.checkbox("Include Charts", value=True)
        include_data_tables = st.checkbox("Include Data Tables", value=True)
        include_disclaimer = st.checkbox("Include Disclaimer", value=True)

        # Branding options
        st.markdown("#### Branding")
        company_name = st.text_input("Company Name", placeholder="Your Company")
        company_logo = st.file_uploader("Company Logo", type=['png', 'jpg', 'jpeg'])

    # Report preview
    st.markdown("### 👀 Report Preview")

    if st.button("🔍 Generate Preview", type="primary"):
        generate_custom_report_preview(
            include_executive, include_customer, include_market,
            include_recommendations, include_risk, include_cashflow,
            report_format, include_charts, include_data_tables,
            include_disclaimer, company_name, max_suburbs, one_pager_style
        )

    # Export options
    st.markdown("### 📥 Export Options")

    if report_format == "Suburb One-Pagers":
        # Special export for one-pagers
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Export One-Pagers as PDF", use_container_width=True, key="pdf_one_pagers"):
                st.info("One-pager PDF export functionality coming soon!")

        with col2:
            if st.button("💾 Download Individual Reports", use_container_width=True, key="download_one_pagers"):
                generate_individual_suburb_reports(max_suburbs, one_pager_style, company_name, include_charts, include_disclaimer)

    else:
        # Standard export options
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Generate PDF", use_container_width=True, key="pdf_custom_report"):
                generate_pdf_report()

        with col2:
            if st.button("📊 Export to Excel", use_container_width=True, key="excel_custom_report"):
                export_to_excel()

        with col3:
            if st.button("📧 Email Report", use_container_width=True, key="email_custom_report"):
                st.info("Email functionality coming soon!")

def generate_custom_report_preview(include_executive, include_customer, include_market,
                                 include_recommendations, include_risk, include_cashflow,
                                 report_format, include_charts, include_data_tables,
                                 include_disclaimer, company_name, max_suburbs=None, one_pager_style=None):
    """Generate a preview of the custom report"""

    st.markdown("---")
    st.markdown("## 📋 Custom Report Preview")

    # Special handling for Suburb One-Pagers
    if report_format == "Suburb One-Pagers":
        generate_suburb_one_pagers_preview(max_suburbs, one_pager_style, company_name, include_charts, include_disclaimer)
        return

    # Header with branding
    if company_name:
        st.markdown(f"### {company_name}")
        st.markdown("#### Property Investment Analysis Report")
    else:
        st.markdown("### Property Investment Analysis Report")

    st.markdown(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}")
    st.markdown("---")

    # Include sections based on selection
    if include_executive:
        st.markdown("### Executive Summary")
        st.info("Executive summary section would appear here...")

    if include_customer:
        st.markdown("### Customer Profile")
        customer_profile = st.session_state.customer_profile
        display_customer_profile_summary(customer_profile)

    if include_market:
        st.markdown("### Market Analysis")
        if include_charts:
            st.info("Market analysis charts would appear here...")
        st.info("Market analysis content would appear here...")

    if include_recommendations:
        st.markdown("### Investment Recommendations")
        recommendations = st.session_state.recommendations
        top_recs = get_top_recommendations(recommendations, 3)
        if not top_recs.empty and include_data_tables:
            st.dataframe(top_recs[['Suburb', 'State', 'Median Price', 'Rental Yield on Houses'][:4]], use_container_width=True)

    if include_risk:
        st.markdown("### Risk Assessment")
        st.info("Risk assessment content would appear here...")

    if include_cashflow:
        st.markdown("### Cash Flow Projections")
        st.info("Cash flow projection tables would appear here...")

    if include_disclaimer:
        st.markdown("### Disclaimer")
        st.caption("""
        This report is generated using AI and machine learning algorithms.
        Please consult with qualified financial advisors before making investment decisions.
        """)

    st.success(f"✅ Preview generated for {report_format} format!")

# Helper functions

def get_budget_range(customer_profile):
    """Extract budget range from customer profile"""
    price_range = customer_profile.get('property_preferences', {}).get('price_range', {})
    min_price = price_range.get('min', 'Not specified')
    max_price = price_range.get('max', 'Not specified')
    return f"${min_price} - ${max_price}"

def get_recommendation_count(recommendations):
    """Get total number of recommendations"""
    count = 0
    if recommendations:
        if 'ml_recommendations' in recommendations and recommendations['ml_recommendations'] is not None:
            count = max(count, len(recommendations['ml_recommendations']))
        if 'rule_based' in recommendations and recommendations['rule_based'] is not None:
            count = max(count, len(recommendations['rule_based']))
        if 'ai_analysis' in recommendations:
            ai_suburbs = recommendations['ai_analysis'].get('recommended_suburbs', [])
            count = max(count, len(ai_suburbs))
    return count

def get_top_recommendations(recommendations, n=5):
    """Get top N recommendations"""
    if not recommendations:
        return pd.DataFrame()

    # Try ML recommendations first
    if 'ml_recommendations' in recommendations and recommendations['ml_recommendations'] is not None:
        df = recommendations['ml_recommendations']
        if not df.empty:
            return df.head(n)

    # Fallback to rule-based
    if 'rule_based' in recommendations and recommendations['rule_based'] is not None:
        df = recommendations['rule_based']
        if not df.empty:
            return df.head(n)

    return pd.DataFrame()

def categorize_risk_levels(recommendations_df):
    """Categorize recommendations by risk level"""
    risk_counts = {'low': 0, 'medium': 0, 'high': 0}

    for _, row in recommendations_df.iterrows():
        # Simple risk categorization based on yield and distance
        risk_score = 0

        if 'Rental Yield on Houses' in row:
            if row['Rental Yield on Houses'] > 6:
                risk_score += 2  # High yield = higher risk
            elif row['Rental Yield on Houses'] > 4:
                risk_score += 1

        if 'Distance (km) to CBD' in row:
            if row['Distance (km) to CBD'] > 30:
                risk_score += 2  # Far from CBD = higher risk
            elif row['Distance (km) to CBD'] > 15:
                risk_score += 1

        # Categorize
        if risk_score <= 1:
            risk_counts['low'] += 1
        elif risk_score <= 3:
            risk_counts['medium'] += 1
        else:
            risk_counts['high'] += 1

    return risk_counts

def display_customer_profile_summary(customer_profile):
    """Display customer profile summary in report"""
    col1, col2 = st.columns(2)

    with col1:
        financial = customer_profile.get('financial_profile', {})
        st.write(f"**Annual Income:** {financial.get('annual_income', 'N/A')}")
        st.write(f"**Available Equity:** {financial.get('available_equity', 'N/A')}")

    with col2:
        investment_goals = customer_profile.get('investment_goals', {})
        st.write(f"**Investment Purpose:** {investment_goals.get('primary_purpose', 'N/A')}")
        st.write(f"**Target Yield:** {investment_goals.get('target_yield', 'N/A')}")

def generate_pdf_report():
    """Generate comprehensive PDF report"""
    try:
        with st.spinner("📄 Generating PDF report..."):
            # Get data from session state
            customer_profile = st.session_state.get('customer_profile', {})
            suburb_data = st.session_state.get('suburb_data')
            recommendations = st.session_state.get('recommendations', {})

            if not customer_profile and not recommendations:
                st.warning("⚠️ No data available to generate report. Please complete the analysis first.")
                return

            # Create temporary PDF file
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)

            # Build PDF content
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#1f2937'),
                alignment=1  # Center alignment
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=12,
                textColor=colors.HexColor('#3b82f6')
            )

            # Title page
            story.append(Paragraph("Property Investment Analysis Report", title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
            story.append(Spacer(1, 40))

            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))

            # Get recommendation data with support for new structure
            primary_recs = recommendations.get('primary_recommendations')
            engine_used = recommendations.get('recommendation_engine', 'unknown')

            if primary_recs is not None and not primary_recs.empty:
                top_suburbs = primary_recs.head(5)
                engine_display = {
                    'ai_genai': 'AI/GenAI Engine (OpenAI GPT-4)',
                    'rule_based': 'Rule-Based Analysis Engine',
                    'ml': 'Machine Learning Engine'
                }

                story.append(Paragraph(f"Analysis conducted using: {engine_display.get(engine_used, engine_used)}", styles['Normal']))
                story.append(Spacer(1, 12))

                story.append(Paragraph(f"Our analysis has identified {len(top_suburbs)} top investment opportunities that align with your investment criteria:", styles['Normal']))
                story.append(Spacer(1, 12))

                # Top suburbs summary
                for idx, (_, suburb) in enumerate(top_suburbs.iterrows(), 1):
                    suburb_name = suburb.get('Suburb Name', suburb.get('Suburb', f'Suburb {idx}'))
                    state = suburb.get('State', '')

                    # Get metrics
                    price = suburb.get('Median Price', 0)
                    yield_val = suburb.get('Rental Yield on Houses', 0)
                    growth = suburb.get('10 yr Avg. Annual Growth', 0)

                    suburb_text = f"<b>{idx}. {suburb_name}, {state}</b><br/>"
                    if price > 0:
                        suburb_text += f"Median Price: ${price:,.0f} | "
                    if yield_val > 0:
                        suburb_text += f"Rental Yield: {yield_val:.1f}% | "
                    if growth > 0:
                        suburb_text += f"10yr Growth: {growth:.1f}%"

                    # Add AI reasoning if available
                    if 'AI_Reasons' in suburb and suburb['AI_Reasons']:
                        reasons = suburb['AI_Reasons'].split('; ')
                        suburb_text += f"<br/><i>Key Factors: {', '.join(reasons[:2])}</i>"

                    story.append(Paragraph(suburb_text, styles['Normal']))
                    story.append(Spacer(1, 8))
            else:
                story.append(Paragraph("No recommendations available in current analysis.", styles['Normal']))

            story.append(PageBreak())

            # Customer Profile Section
            if customer_profile:
                story.append(Paragraph("Investment Profile", heading_style))

                # Personal details
                personal = customer_profile.get('personal_details', {})
                if personal:
                    story.append(Paragraph("<b>Investor Profile:</b>", styles['Normal']))
                    if personal.get('age'):
                        story.append(Paragraph(f"Age: {personal['age']}", styles['Normal']))
                    if personal.get('location'):
                        story.append(Paragraph(f"Location: {personal['location']}", styles['Normal']))
                    story.append(Spacer(1, 12))

                # Financial details
                financial = customer_profile.get('financial_details', {})
                if financial:
                    story.append(Paragraph("<b>Financial Capacity:</b>", styles['Normal']))
                    if financial.get('annual_income'):
                        story.append(Paragraph(f"Annual Income: {financial['annual_income']}", styles['Normal']))
                    if financial.get('investment_budget'):
                        story.append(Paragraph(f"Investment Budget: {financial['investment_budget']}", styles['Normal']))
                    if financial.get('available_equity'):
                        story.append(Paragraph(f"Available Equity: {financial['available_equity']}", styles['Normal']))
                    story.append(Spacer(1, 12))

                # Investment goals
                goals = customer_profile.get('investment_goals', {})
                if goals:
                    story.append(Paragraph("<b>Investment Objectives:</b>", styles['Normal']))
                    if goals.get('primary_purpose'):
                        story.append(Paragraph(f"Primary Purpose: {goals['primary_purpose']}", styles['Normal']))
                    if goals.get('investment_timeline'):
                        story.append(Paragraph(f"Investment Timeline: {goals['investment_timeline']}", styles['Normal']))
                    if goals.get('risk_tolerance'):
                        story.append(Paragraph(f"Risk Tolerance: {goals['risk_tolerance']}", styles['Normal']))
                    story.append(Spacer(1, 12))

                story.append(PageBreak())

            # Detailed Recommendations
            if primary_recs is not None and not primary_recs.empty:
                story.append(Paragraph("Detailed Property Recommendations", heading_style))

                for idx, (_, suburb) in enumerate(primary_recs.head(10).iterrows(), 1):
                    suburb_name = suburb.get('Suburb Name', suburb.get('Suburb', f'Suburb {idx}'))
                    state = suburb.get('State', '')

                    story.append(Paragraph(f"<b>{idx}. {suburb_name}, {state}</b>", styles['Heading3']))

                    # Create table data for metrics
                    table_data = []

                    if 'Median Price' in suburb and suburb['Median Price'] > 0:
                        table_data.append(['Median Price', f"${suburb['Median Price']:,.0f}"])
                    if 'Rental Yield on Houses' in suburb and suburb['Rental Yield on Houses'] > 0:
                        table_data.append(['Rental Yield', f"{suburb['Rental Yield on Houses']:.1f}%"])
                    if '10 yr Avg. Annual Growth' in suburb and suburb['10 yr Avg. Annual Growth'] != 0:
                        table_data.append(['10-Year Growth', f"{suburb['10 yr Avg. Annual Growth']:.1f}%"])
                    if 'Distance (km) to CBD' in suburb and suburb['Distance (km) to CBD'] > 0:
                        table_data.append(['Distance to CBD', f"{suburb['Distance (km) to CBD']:.0f} km"])

                    if table_data:
                        table = Table(table_data, colWidths=[2*inch, 2*inch])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 12))

                    # AI Score and reasoning
                    if 'AI_Score' in suburb and suburb['AI_Score'] > 0:
                        story.append(Paragraph(f"<b>AI Investment Score:</b> {suburb['AI_Score']:.0f}/100", styles['Normal']))
                        if 'AI_Reasons' in suburb and suburb['AI_Reasons']:
                            story.append(Paragraph("<b>AI Analysis:</b>", styles['Normal']))
                            reasons = suburb['AI_Reasons'].split('; ')
                            for reason in reasons:
                                story.append(Paragraph(f"• {reason}", styles['Normal']))
                        story.append(Spacer(1, 12))

                    # Investment potential
                    if 'Investment_Potential' in suburb:
                        potential_colors = {
                            'high': colors.green,
                            'medium': colors.orange,
                            'low': colors.red
                        }
                        potential = suburb['Investment_Potential'].lower()
                        color = potential_colors.get(potential, colors.black)
                        story.append(Paragraph(f"<b>Investment Potential:</b> <font color='{color.hexval()}'>{suburb['Investment_Potential'].title()}</font>", styles['Normal']))

                    story.append(Spacer(1, 20))

                    if idx < len(primary_recs.head(10)):
                        story.append(Paragraph("<hr/>", styles['Normal']))
                        story.append(Spacer(1, 12))

            # Disclaimer
            story.append(PageBreak())
            story.append(Paragraph("Important Disclaimer", heading_style))
            disclaimer_text = """
            This report is generated for informational purposes only and should not be considered as financial advice.
            Property investment involves risks, and past performance is not indicative of future results.
            We recommend consulting with qualified financial advisors and conducting thorough due diligence
            before making any investment decisions. Market conditions can change rapidly, and property values may fluctuate.

            This analysis is based on available market data and AI-powered insights, but should be supplemented
            with professional property inspections, legal advice, and current market assessments.
            """
            story.append(Paragraph(disclaimer_text, styles['Normal']))

            # Build PDF
            doc.build(story)

            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()

            # Provide download button
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=f"property_investment_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                key="pdf_download"
            )

            st.success("✅ PDF report generated successfully!")
            st.info("📊 Your comprehensive property investment report is ready for download.")

    except Exception as e:
        st.error(f"❌ Error generating PDF report: {str(e)}")
        st.error("Please ensure all required data is available and try again.")

def export_to_excel():
    """Export data to Excel format"""
    try:
        # Prepare data for export
        export_data = {}

        if st.session_state.get('suburb_data') is not None:
            export_data['Market_Data'] = st.session_state.suburb_data

        recommendations = st.session_state.get('recommendations')
        if recommendations:
            top_recs = get_top_recommendations(recommendations, 20)
            if not top_recs.empty:
                export_data['Recommendations'] = top_recs

        if export_data:
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, data in export_data.items():
                    data.to_excel(writer, sheet_name=sheet_name, index=False)

            output.seek(0)

            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name=f"property_analysis_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Excel report ready for download!")

    except Exception as e:
        st.error(f"Error generating Excel report: {str(e)}")

def save_report_data():
    """Save comprehensive report data with multiple formats"""
    try:
        with st.spinner("💾 Preparing report data..."):
            # Gather all available data
            customer_profile = st.session_state.get('customer_profile', {})
            suburb_data = st.session_state.get('suburb_data')
            recommendations = st.session_state.get('recommendations', {})
            agent_notes = st.session_state.get('agent_notes', {})
            detailed_agent_notes = st.session_state.get('detailed_agent_notes', {})

            # Create comprehensive report data structure
            report_data = {
                'metadata': {
                    'generated_date': datetime.now().isoformat(),
                    'report_version': '2.0',
                    'application': 'Property Investment Analysis Platform',
                    'recommendation_engine': recommendations.get('recommendation_engine', 'unknown')
                },
                'customer_profile': customer_profile,
                'recommendations': recommendations,
                'agent_review': {
                    'quick_notes': agent_notes,
                    'detailed_notes': detailed_agent_notes,
                    'review_complete': len(agent_notes) > 0 or len(detailed_agent_notes) > 0
                },
                'session_summary': {
                    'profile_generated': st.session_state.get('profile_generated', False),
                    'data_uploaded': st.session_state.get('data_uploaded', False),
                    'analysis_complete': st.session_state.get('analysis_complete', False),
                    'workflow_step': st.session_state.get('workflow_step', 1)
                }
            }

            # Handle suburb data serialization
            if suburb_data is not None and not suburb_data.empty:
                # Convert DataFrame to dict for JSON serialization
                report_data['market_data'] = {
                    'suburb_count': len(suburb_data),
                    'columns': suburb_data.columns.tolist(),
                    'sample_data': suburb_data.head(10).to_dict('records'),  # Include sample for reference
                    'data_summary': {
                        'median_price_range': {
                            'min': float(suburb_data['Median Price'].min()) if 'Median Price' in suburb_data.columns else None,
                            'max': float(suburb_data['Median Price'].max()) if 'Median Price' in suburb_data.columns else None,
                            'mean': float(suburb_data['Median Price'].mean()) if 'Median Price' in suburb_data.columns else None
                        } if 'Median Price' in suburb_data.columns else {},
                        'yield_range': {
                            'min': float(suburb_data['Rental Yield on Houses'].min()) if 'Rental Yield on Houses' in suburb_data.columns else None,
                            'max': float(suburb_data['Rental Yield on Houses'].max()) if 'Rental Yield on Houses' in suburb_data.columns else None,
                            'mean': float(suburb_data['Rental Yield on Houses'].mean()) if 'Rental Yield on Houses' in suburb_data.columns else None
                        } if 'Rental Yield on Houses' in suburb_data.columns else {}
                    }
                }

            # Store in session state
            st.session_state.final_report = report_data

            # Auto-backup session data
            backup_session_data()

            # Provide multiple download options
            col1, col2, col3 = st.columns(3)

            with col1:
                # JSON download (detailed)
                json_data = json.dumps(report_data, indent=2, default=str)
                st.download_button(
                    label="📄 Download Complete Report (JSON)",
                    data=json_data,
                    file_name=f"property_analysis_complete_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    help="Complete analysis data including all session information"
                )

            with col2:
                # CSV download (recommendations only)
                primary_recs = recommendations.get('primary_recommendations')
                if primary_recs is not None and not primary_recs.empty:
                    csv_data = primary_recs.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Recommendations (CSV)",
                        data=csv_data,
                        file_name=f"property_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        help="Recommended suburbs data in spreadsheet format"
                    )
                else:
                    st.info("No recommendations available for CSV export")

            with col3:
                # Summary JSON (lightweight)
                summary_data = {
                    'generated_date': datetime.now().isoformat(),
                    'customer_summary': {
                        'budget': customer_profile.get('financial_details', {}).get('investment_budget', 'N/A'),
                        'purpose': customer_profile.get('investment_goals', {}).get('primary_purpose', 'N/A'),
                        'timeline': customer_profile.get('investment_goals', {}).get('investment_timeline', 'N/A')
                    },
                    'top_recommendations': []
                }

                # Add top 5 recommendations summary
                primary_recs = recommendations.get('primary_recommendations')
                if primary_recs is not None and not primary_recs.empty:
                    for idx, (_, suburb) in enumerate(primary_recs.head(5).iterrows(), 1):
                        suburb_summary = {
                            'rank': idx,
                            'suburb': suburb.get('Suburb Name', suburb.get('Suburb', f'Suburb {idx}')),
                            'state': suburb.get('State', ''),
                            'median_price': suburb.get('Median Price', 0),
                            'rental_yield': suburb.get('Rental Yield on Houses', 0),
                            'growth_10yr': suburb.get('10 yr Avg. Annual Growth', 0)
                        }
                        if 'AI_Score' in suburb:
                            suburb_summary['ai_score'] = suburb['AI_Score']
                        if 'AI_Reasons' in suburb:
                            suburb_summary['key_factors'] = suburb['AI_Reasons'].split('; ')[:3]

                        summary_data['top_recommendations'].append(suburb_summary)

                summary_json = json.dumps(summary_data, indent=2, default=str)
                st.download_button(
                    label="📋 Download Summary (JSON)",
                    data=summary_json,
                    file_name=f"property_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    help="Lightweight summary of key findings"
                )

            st.success("✅ Report data saved successfully!")
            st.info("💡 **Multiple formats available:** Complete analysis (JSON), Recommendations (CSV), and Summary (JSON)")

            # Show data summary
            with st.expander("📊 Report Data Summary"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Recommendations Generated", len(primary_recs) if primary_recs is not None else 0)
                    st.metric("Agent Notes", len(agent_notes))

                with col2:
                    st.metric("Market Data Points", len(suburb_data) if suburb_data is not None else 0)
                    st.metric("Workflow Completion", f"{st.session_state.get('workflow_step', 1)}/5")

                # Engine used
                engine_used = recommendations.get('recommendation_engine', 'unknown')
                engine_display = {
                    'ai_genai': '🤖 AI/GenAI Engine (OpenAI GPT-4)',
                    'rule_based': '📊 Rule-Based Analysis',
                    'ml': '🧠 Machine Learning Engine'
                }
                st.info(f"**Analysis Engine:** {engine_display.get(engine_used, engine_used)}")

    except Exception as e:
        st.error(f"❌ Error saving report data: {str(e)}")
        st.error("Please ensure analysis is complete and try again.")

def generate_suburb_one_pagers_preview(max_suburbs, one_pager_style, company_name, include_charts, include_disclaimer):
    """Generate preview of suburb one-pagers"""
    st.markdown(f"### 🏘️ Suburb One-Pagers Preview ({one_pager_style} Style)")

    # Get recommendations data
    recommendations = st.session_state.get('recommendations')
    if not recommendations:
        st.error("No recommendations data available")
        return

    # Get top suburbs
    top_suburbs = get_top_recommendations(recommendations, max_suburbs)
    if top_suburbs.empty:
        st.error("No suburb data available for one-pagers")
        return

    st.info(f"📄 Generating {len(top_suburbs)} one-page reports in {one_pager_style} style")

    # Generate one-pager for each suburb
    for idx, (_, suburb) in enumerate(top_suburbs.iterrows()):
        if idx >= max_suburbs:
            break

        st.markdown("---")
        generate_single_suburb_one_pager(suburb, idx + 1, one_pager_style, company_name, include_charts, include_disclaimer)

        # Add page break indicator for PDF generation
        if idx < len(top_suburbs) - 1:
            st.markdown("*--- Page Break ---*")

def generate_single_suburb_one_pager(suburb, rank, style, company_name, include_charts, include_disclaimer):
    """Generate a single suburb one-pager"""
    suburb_name = suburb.get('Suburb', 'Unknown Suburb')
    state = suburb.get('State', '')

    # Header section
    col1, col2 = st.columns([3, 1])

    with col1:
        if company_name:
            st.markdown(f"### {company_name}")
        st.markdown(f"## #{rank} {suburb_name}, {state}")
        st.markdown(f"*Investment Opportunity Brief - {style} Analysis*")

    with col2:
        # Investment Score Badge
        score = None
        if 'Investment_Score_Predicted' in suburb:
            score = suburb['Investment_Score_Predicted']
        elif 'Composite_Score' in suburb:
            score = suburb['Composite_Score']

        if score is not None:
            score_color = "🟢" if score > 0.7 else "🟡" if score > 0.5 else "🔴"
            st.markdown(f"## {score_color} {score:.2f}")
            st.caption("Investment Score")

    if style == "Executive":
        generate_executive_one_pager(suburb, include_charts)
    elif style == "Detailed":
        generate_detailed_one_pager(suburb, include_charts)
    elif style == "Investor Brief":
        generate_investor_brief_one_pager(suburb, include_charts)

    # Add disclaimer if requested
    if include_disclaimer:
        st.markdown("---")
        st.caption("⚠️ This analysis is for informational purposes only and should not be considered financial advice. Please consult with qualified professionals before making investment decisions.")

def generate_executive_one_pager(suburb, include_charts):
    """Generate executive style one-pager"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Key Metrics")
        if 'Median Price' in suburb:
            st.metric("Median Price", f"${suburb['Median Price']:,.0f}")
        if 'Rental Yield on Houses' in suburb:
            st.metric("Rental Yield", f"{suburb['Rental Yield on Houses']:.1f}%")
        if '10 yr Avg. Annual Growth' in suburb:
            st.metric("10yr Growth", f"{suburb['10 yr Avg. Annual Growth']:.1f}%")
        if 'Distance (km) to CBD' in suburb:
            st.metric("Distance to CBD", f"{suburb['Distance (km) to CBD']:.0f}km")

    with col2:
        st.markdown("### 💡 Investment Highlights")
        highlights = []

        # Generate highlights based on data
        if 'Rental Yield on Houses' in suburb and suburb['Rental Yield on Houses'] > 5:
            highlights.append("🔥 High rental yield opportunity")
        if '10 yr Avg. Annual Growth' in suburb and suburb['10 yr Avg. Annual Growth'] > 6:
            highlights.append("📈 Strong historical growth")
        if 'Distance (km) to CBD' in suburb and suburb['Distance (km) to CBD'] < 20:
            highlights.append("🏙️ Close to CBD")
        if 'Population' in suburb and suburb['Population'] > 20000:
            highlights.append("👥 Large population base")

        if not highlights:
            highlights = ["📋 Solid investment fundamentals", "🏘️ Established suburb profile"]

        for highlight in highlights[:4]:  # Show max 4 highlights
            st.write(f"• {highlight}")

def generate_detailed_one_pager(suburb, include_charts):
    """Generate detailed style one-pager"""
    # Financial Overview
    st.markdown("### 💰 Financial Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if 'Median Price' in suburb:
            st.metric("Median Price", f"${suburb['Median Price']:,.0f}")
    with col2:
        if 'Rental Yield on Houses' in suburb:
            st.metric("Rental Yield", f"{suburb['Rental Yield on Houses']:.1f}%")
    with col3:
        if '10 yr Avg. Annual Growth' in suburb:
            st.metric("Growth (10yr)", f"{suburb['10 yr Avg. Annual Growth']:.1f}%")
    with col4:
        if 'Vacancy Rate' in suburb:
            st.metric("Vacancy Rate", f"{suburb['Vacancy Rate']:.1f}%")

    # Location & Demographics
    st.markdown("### 📍 Location & Demographics")
    col1, col2 = st.columns(2)

    with col1:
        if 'Distance (km) to CBD' in suburb:
            st.write(f"**Distance to CBD:** {suburb['Distance (km) to CBD']:.0f}km")
        if 'Population' in suburb:
            st.write(f"**Population:** {suburb['Population']:,.0f}")

    with col2:
        if 'Sales Days on Market' in suburb:
            st.write(f"**Days on Market:** {suburb['Sales Days on Market']:.0f}")
        if 'Region' in suburb:
            st.write(f"**Region:** {suburb['Region']}")

    # Investment Analysis
    st.markdown("### 📈 Investment Analysis")

    # Generate risk assessment
    risk_factors = []
    if 'Vacancy Rate' in suburb and suburb['Vacancy Rate'] > 4:
        risk_factors.append("⚠️ Higher vacancy rate")
    if '10 yr Avg. Annual Growth' in suburb and suburb['10 yr Avg. Annual Growth'] < 3:
        risk_factors.append("⚠️ Lower historical growth")

    if risk_factors:
        st.markdown("**Risk Considerations:**")
        for risk in risk_factors:
            st.write(f"• {risk}")
    else:
        st.write("✅ Low risk profile based on available metrics")

def generate_investor_brief_one_pager(suburb, include_charts):
    """Generate investor brief style one-pager"""
    # Investment Summary
    st.markdown("### 🎯 Investment Summary")

    # Calculate investment potential score
    potential_score = calculate_investment_potential(suburb)

    col1, col2 = st.columns([2, 1])

    with col1:
        if potential_score >= 0.8:
            st.success("🟢 **STRONG BUY** - Excellent investment opportunity")
        elif potential_score >= 0.6:
            st.info("🟡 **BUY** - Good investment potential")
        else:
            st.warning("🔴 **HOLD** - Consider other options")

    with col2:
        st.metric("Potential Score", f"{potential_score:.2f}/1.00")

    # Quick Facts
    st.markdown("### ⚡ Quick Facts")
    facts_col1, facts_col2 = st.columns(2)

    with facts_col1:
        if 'Median Price' in suburb:
            st.write(f"💰 **Entry Price:** ${suburb['Median Price']:,.0f}")
        if 'Rental Yield on Houses' in suburb:
            st.write(f"💎 **Yield:** {suburb['Rental Yield on Houses']:.1f}%")

    with facts_col2:
        if '10 yr Avg. Annual Growth' in suburb:
            st.write(f"📊 **Growth:** {suburb['10 yr Avg. Annual Growth']:.1f}% p.a.")
        if 'Distance (km) to CBD' in suburb:
            st.write(f"🏙️ **Location:** {suburb['Distance (km) to CBD']:.0f}km from CBD")

    # Investment Rationale
    st.markdown("### 📝 Investment Rationale")
    rationale = generate_investment_rationale(suburb)
    st.write(rationale)

def calculate_investment_potential(suburb):
    """Calculate overall investment potential score"""
    score = 0.0
    factors = 0

    # Yield factor (30%)
    if 'Rental Yield on Houses' in suburb:
        yield_val = suburb['Rental Yield on Houses']
        yield_score = min(1.0, max(0.0, (yield_val - 2) / 6))  # Scale 2-8% to 0-1
        score += yield_score * 0.3
        factors += 0.3

    # Growth factor (30%)
    if '10 yr Avg. Annual Growth' in suburb:
        growth_val = suburb['10 yr Avg. Annual Growth']
        growth_score = min(1.0, max(0.0, growth_val / 10))  # Scale 0-10% to 0-1
        score += growth_score * 0.3
        factors += 0.3

    # Location factor (20%)
    if 'Distance (km) to CBD' in suburb:
        distance = suburb['Distance (km) to CBD']
        location_score = max(0.0, 1.0 - (distance / 50))  # Closer = better
        score += location_score * 0.2
        factors += 0.2

    # Vacancy factor (20%)
    if 'Vacancy Rate' in suburb:
        vacancy = suburb['Vacancy Rate']
        vacancy_score = max(0.0, 1.0 - (vacancy / 10))  # Lower vacancy = better
        score += vacancy_score * 0.2
        factors += 0.2

    return score / factors if factors > 0 else 0.5

def generate_investment_rationale(suburb):
    """Generate investment rationale text"""
    rationale_points = []

    if 'Rental Yield on Houses' in suburb:
        yield_val = suburb['Rental Yield on Houses']
        if yield_val > 5:
            rationale_points.append(f"Strong rental yield of {yield_val:.1f}% provides excellent cash flow potential")
        elif yield_val > 3.5:
            rationale_points.append(f"Solid rental yield of {yield_val:.1f}% supports investment returns")

    if '10 yr Avg. Annual Growth' in suburb:
        growth_val = suburb['10 yr Avg. Annual Growth']
        if growth_val > 6:
            rationale_points.append(f"Exceptional {growth_val:.1f}% historical growth indicates strong capital appreciation")
        elif growth_val > 4:
            rationale_points.append(f"Steady {growth_val:.1f}% growth track record demonstrates market confidence")

    if 'Distance (km) to CBD' in suburb:
        distance = suburb['Distance (km) to CBD']
        if distance < 15:
            rationale_points.append(f"Prime location just {distance:.0f}km from CBD ensures strong demand")
        elif distance < 30:
            rationale_points.append(f"Well-positioned {distance:.0f}km from CBD offers good accessibility")

    if not rationale_points:
        rationale_points.append("Solid fundamentals and market positioning make this a viable investment opportunity")

    return ". ".join(rationale_points) + "."

def generate_individual_suburb_reports(max_suburbs, one_pager_style, company_name, include_charts, include_disclaimer):
    """Generate downloadable individual suburb reports"""

    # Get recommendations data
    recommendations = st.session_state.get('recommendations')
    if not recommendations:
        st.error("No recommendations data available")
        return

    # Get top suburbs
    top_suburbs = get_top_recommendations(recommendations, max_suburbs)
    if top_suburbs.empty:
        st.error("No suburb data available for one-pagers")
        return

    st.success(f"✅ Generated {len(top_suburbs)} individual suburb reports!")

    # Create downloadable reports for each suburb
    for idx, (_, suburb) in enumerate(top_suburbs.iterrows()):
        if idx >= max_suburbs:
            break

        suburb_name = suburb.get('Suburb', 'Unknown Suburb')
        state = suburb.get('State', '')

        # Generate the report content as text
        report_content = generate_suburb_report_text(suburb, idx + 1, one_pager_style, company_name, include_disclaimer)

        # Create download button for this suburb
        st.download_button(
            label=f"📄 Download {suburb_name}, {state} Report",
            data=report_content,
            file_name=f"{suburb_name}_{state}_investment_report.txt",
            mime="text/plain",
            key=f"download_suburb_{idx}"
        )

def generate_suburb_report_text(suburb, rank, style, company_name, include_disclaimer):
    """Generate text-based suburb report for download"""
    suburb_name = suburb.get('Suburb', 'Unknown Suburb')
    state = suburb.get('State', '')

    report = []
    report.append("=" * 80)

    if company_name:
        report.append(f"{company_name.upper()}")
        report.append("")

    report.append(f"INVESTMENT OPPORTUNITY BRIEF #{rank}")
    report.append(f"{suburb_name.upper()}, {state}")
    report.append(f"{style} Analysis")
    report.append("=" * 80)
    report.append("")

    # Investment Score
    score = None
    if 'Investment_Score_Predicted' in suburb:
        score = suburb['Investment_Score_Predicted']
    elif 'Composite_Score' in suburb:
        score = suburb['Composite_Score']

    if score is not None:
        rating = "EXCELLENT" if score > 0.7 else "GOOD" if score > 0.5 else "FAIR"
        report.append(f"INVESTMENT SCORE: {score:.2f}/1.00 ({rating})")
        report.append("")

    # Key Metrics
    report.append("KEY FINANCIAL METRICS")
    report.append("-" * 40)

    if 'Median Price' in suburb:
        report.append(f"Median Price: ${suburb['Median Price']:,.0f}")
    if 'Rental Yield on Houses' in suburb:
        report.append(f"Rental Yield: {suburb['Rental Yield on Houses']:.1f}%")
    if '10 yr Avg. Annual Growth' in suburb:
        report.append(f"10-Year Growth: {suburb['10 yr Avg. Annual Growth']:.1f}% p.a.")
    if 'Distance (km) to CBD' in suburb:
        report.append(f"Distance to CBD: {suburb['Distance (km) to CBD']:.0f}km")
    if 'Vacancy Rate' in suburb:
        report.append(f"Vacancy Rate: {suburb['Vacancy Rate']:.1f}%")

    report.append("")

    # Location & Demographics
    report.append("LOCATION & DEMOGRAPHICS")
    report.append("-" * 40)

    if 'Population' in suburb:
        report.append(f"Population: {suburb['Population']:,.0f}")
    if 'Sales Days on Market' in suburb:
        report.append(f"Days on Market: {suburb['Sales Days on Market']:.0f}")
    if 'Region' in suburb:
        report.append(f"Region: {suburb['Region']}")

    report.append("")

    # Investment Analysis
    if style == "Investor Brief":
        potential_score = calculate_investment_potential(suburb)

        report.append("INVESTMENT RECOMMENDATION")
        report.append("-" * 40)

        if potential_score >= 0.8:
            report.append("RECOMMENDATION: STRONG BUY")
            report.append("Assessment: Excellent investment opportunity")
        elif potential_score >= 0.6:
            report.append("RECOMMENDATION: BUY")
            report.append("Assessment: Good investment potential")
        else:
            report.append("RECOMMENDATION: HOLD")
            report.append("Assessment: Consider other options")

        report.append("")

        # Investment Rationale
        report.append("INVESTMENT RATIONALE")
        report.append("-" * 40)
        rationale = generate_investment_rationale(suburb)

        # Wrap text at 80 characters
        import textwrap
        wrapped_rationale = textwrap.fill(rationale, width=80)
        report.append(wrapped_rationale)

    elif style == "Detailed":
        # Risk Assessment
        report.append("RISK ASSESSMENT")
        report.append("-" * 40)

        risk_factors = []
        if 'Vacancy Rate' in suburb and suburb['Vacancy Rate'] > 4:
            risk_factors.append("- Higher than average vacancy rate")
        if '10 yr Avg. Annual Growth' in suburb and suburb['10 yr Avg. Annual Growth'] < 3:
            risk_factors.append("- Lower historical growth performance")

        if risk_factors:
            report.append("Risk Considerations:")
            report.extend(risk_factors)
        else:
            report.append("Low risk profile based on available metrics")

    else:  # Executive
        # Investment Highlights
        report.append("INVESTMENT HIGHLIGHTS")
        report.append("-" * 40)

        highlights = []
        if 'Rental Yield on Houses' in suburb and suburb['Rental Yield on Houses'] > 5:
            highlights.append("- High rental yield opportunity")
        if '10 yr Avg. Annual Growth' in suburb and suburb['10 yr Avg. Annual Growth'] > 6:
            highlights.append("- Strong historical growth")
        if 'Distance (km) to CBD' in suburb and suburb['Distance (km) to CBD'] < 20:
            highlights.append("- Close proximity to CBD")
        if 'Population' in suburb and suburb['Population'] > 20000:
            highlights.append("- Large population base")

        if not highlights:
            highlights = ["- Solid investment fundamentals", "- Established suburb profile"]

        report.extend(highlights[:4])

    report.append("")

    # Footer
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

    if include_disclaimer:
        report.append("")
        report.append("IMPORTANT DISCLAIMER")
        report.append("-" * 40)
        report.append("This analysis is for informational purposes only and should not")
        report.append("be considered financial advice. Please consult with qualified")
        report.append("professionals before making investment decisions.")

    report.append("=" * 80)

    return "\n".join(report)