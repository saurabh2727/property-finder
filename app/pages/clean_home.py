import streamlit as st
from utils.session_state import update_workflow_step
from components.sample_files import render_sample_files_section
from styles.global_styles import get_global_css, COLORS
from components.property_card import render_hero_section, render_metric_grid

def render_clean_home_page():
    """Render a modern, professional home page with new design"""

    # Inject global CSS
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Hero Section
    render_hero_section(
        title="🏡 Property Investment Analysis Platform",
        subtitle="Data-driven insights for smarter property investment decisions"
    )

    # Quick Actions Section - Prominent at top
    st.markdown("## Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Start New Analysis", type="primary", use_container_width=True):
            update_workflow_step(1)
            st.session_state.current_page = 'customer_profile'
            st.rerun()

    with col2:
        if st.button("📊 Import Sample Data", use_container_width=True):
            st.session_state.current_page = 'data_upload'
            st.rerun()

    with col3:
        if st.button("📖 View Documentation", use_container_width=True):
            st.info("Documentation would open here")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Overview Metrics
    if st.session_state.get('workflow_step', 1) > 1:
        metrics = []
        if st.session_state.get('profile_generated'):
            metrics.append({'icon': '✓', 'value': 'Complete', 'label': 'Customer Profile'})
        if st.session_state.get('data_uploaded'):
            suburb_count = len(st.session_state.get('suburb_data', []))
            metrics.append({'icon': '📊', 'value': f"{suburb_count}", 'label': 'Suburbs Analyzed'})
        if st.session_state.get('recommendations'):
            rec_count = len(st.session_state.recommendations.get('primary_recommendations', []))
            metrics.append({'icon': '🎯', 'value': f"{rec_count}", 'label': 'Recommendations'})

        if metrics:
            render_metric_grid(metrics)
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Feature cards with new design
    st.markdown("## Platform Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="property-card" style="overflow: hidden; height: 400px;">
            <img src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&h=300&fit=crop"
                 style="width: 100%; height: 160px; object-fit: cover;"
                 alt="Customer Profiling">
            <div style="padding: 1.5rem; text-align: center;">
                <h3 style="color: {COLORS['dark_navy']}; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                    👤 Customer Profiling
                </h3>
                <p style="color: {COLORS['slate_gray']}; line-height: 1.6; font-size: 0.9rem; text-align: center;">
                    Automated analysis of client requirements and investment goals from uploaded documents or manual entry.
                </p>
                <div style="margin-top: 1.5rem;">
                    <span class="badge badge-success">AI-Powered</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="property-card" style="overflow: hidden; height: 400px;">
            <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=300&fit=crop"
                 style="width: 100%; height: 160px; object-fit: cover;"
                 alt="Market Analysis">
            <div style="padding: 1.5rem; text-align: center;">
                <h3 style="color: {COLORS['dark_navy']}; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                    📊 Market Analysis
                </h3>
                <p style="color: {COLORS['slate_gray']}; line-height: 1.6; font-size: 0.9rem; text-align: center;">
                    Advanced filtering and scoring of suburbs based on growth potential, rental yields, and risk factors.
                </p>
                <div style="margin-top: 1.5rem;">
                    <span class="badge badge-info">Data-Driven</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="property-card" style="overflow: hidden; height: 400px;">
            <img src="https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=800&h=300&fit=crop"
                 style="width: 100%; height: 160px; object-fit: cover;"
                 alt="Investment Reports">
            <div style="padding: 1.5rem; text-align: center;">
                <h3 style="color: {COLORS['dark_navy']}; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                    📄 Investment Reports
                </h3>
                <p style="color: {COLORS['slate_gray']}; line-height: 1.6; font-size: 0.9rem; text-align: center;">
                    Professional-grade reports with cash flow projections, suburb comparisons, and actionable recommendations.
                </p>
                <div style="margin-top: 1.5rem;">
                    <span class="badge badge-primary">Professional</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Sample files section
    render_sample_files_section()

    st.markdown("---")

    # Workflow overview - simplified
    st.subheader("Analysis Workflow")

    # Step indicators - clean design
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin: 2rem 0; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #1f2937;">1. Profile</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Customer requirements</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #1f2937;">2. Data</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Market information</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #1f2937;">3. Analysis</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Suburb scoring</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #1f2937;">4. Review</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Agent validation</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #1f2937;">5. Report</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Client presentation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Getting started section
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.expander("📚 Getting Started", expanded=False):
            st.markdown("""
            **Step 1: Customer Profiling**
            Upload customer discovery questionnaire or manually enter client requirements including:
            - Financial capacity and budget constraints
            - Investment goals and risk tolerance
            - Property preferences and location priorities

            **Step 2: Market Data Import**
            Import suburb data from sources like HtAG, DSR, Suburb Finder, or upload your own CSV/Excel files with market metrics.

            **Step 3: Analysis & Scoring**
            Run automated analysis to score suburbs on:
            - Growth potential (capital appreciation)
            - Rental yield performance
            - Risk factors (vacancy, market volatility)

            **Step 4: Agent Review**
            Review AI recommendations, adjust scoring weights, and add professional insights and notes.

            **Step 5: Generate Reports**
            Create professional client presentations with suburb rankings, property listings, and cash flow projections.
            """)


    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.85rem; padding: 1rem;">
        Property Insight Platform v1.0 | Professional Property Investment Analysis
    </div>
    """, unsafe_allow_html=True)