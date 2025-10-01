import streamlit as st
from utils.session_state import update_workflow_step

def render_home_page():
    """Render the home page with overview and getting started guide"""

    st.title("🏠 Property Insight App")
    st.subheader("Residential Property Analysis for Buyer's Agents")

    # Hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="color: white; margin-bottom: 1rem;">Automate Your Property Research Process</h2>
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            Transform manual property research into intelligent, data-driven insights with AI-powered analysis,
            machine learning recommendations, and automated market research.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🤖 AI Customer Profiling</h4>
            <p>Upload customer documents and let AI analyze financial capacity, preferences, and investment goals automatically.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Smart Data Integration</h4>
            <p>Connect with multiple data sources (HtAG, DSR, Suburb Finder) and process complex market data effortlessly.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>⭐ ML Recommendations</h4>
            <p>Get intelligent property recommendations based on historical trends, market analysis, and customer requirements.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Getting started section
    st.subheader("🚀 Getting Started")

    # Step indicators
    st.markdown("""
    <div class="step-indicator">
        <div class="step">1. Customer Profile</div>
        <div class="step">2. Data Upload</div>
        <div class="step">3. Analysis</div>
        <div class="step">4. Recommendations</div>
        <div class="step">5. Reports</div>
    </div>
    """, unsafe_allow_html=True)

    # Workflow explanation
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### Workflow Overview

        **Step 1: Customer Profiling**
        - Upload customer discovery questionnaire document
        - AI analyzes financial capacity, investment goals, and preferences
        - Automated profile generation with key insights

        **Step 2: Data Integration**
        - Import suburb data from your preferred sources
        - Support for CSV, Excel, and API connections
        - Automated data validation and processing

        **Step 3: Intelligent Analysis**
        - Rule-based filtering based on customer criteria
        - Weightage-based suburb ranking
        - Market trend analysis and predictions

        **Step 4: ML Recommendations**
        - Machine learning-powered property suggestions
        - Cash flow projections and ROI calculations
        - Risk assessment and opportunity identification

        **Step 5: Comprehensive Reports**
        - Detailed suburb analysis reports
        - Property comparison matrices
        - Investment performance projections
        """)

    with col2:
        st.info("""
        💡 **Pro Tips:**

        - Ensure customer documents are complete
        - Use the most recent suburb data
        - Review AI insights before finalizing
        - Customize weights based on customer priorities
        - Export reports for client presentations
        """)

        if st.button("🎯 Start Analysis", type="primary", use_container_width=True):
            update_workflow_step(1)
            st.session_state.current_page = 'customer_profile'
            st.rerun()

    st.markdown("---")

    # Recent activity/stats (placeholder for future implementation)
    st.subheader("📈 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Profiles Generated", value="0", delta="This Session")

    with col2:
        st.metric(label="Suburbs Analyzed", value="0", delta="This Session")

    with col3:
        st.metric(label="Recommendations", value="0", delta="Generated")

    with col4:
        st.metric(label="Reports Created", value="0", delta="This Session")

    # Quick actions
    st.markdown("### Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Upload Customer Profile", use_container_width=True):
            st.session_state.current_page = 'customer_profile'
            st.rerun()

    with col2:
        if st.button("📊 Import Suburb Data", use_container_width=True):
            st.session_state.current_page = 'data_upload'
            st.rerun()

    with col3:
        if st.button("🔍 View Sample Analysis", use_container_width=True):
            st.info("Sample analysis feature coming soon!")

    st.markdown("---")

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Property Insight App v1.0 | Built for Professional Property Agents
    </div>
    """, unsafe_allow_html=True)