import streamlit as st
from utils.session_state import update_workflow_step
from components.sample_files import render_sample_files_section

def render_clean_home_page():
    """Render a modern, professional home page"""

    # Standard header to match other pages
    st.title("🏠 Dashboard")
    st.subheader("Property Investment Analysis Platform")

    # Feature cards with Streamlit columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: white; border: 1px solid #ecf0f1; border-radius: 16px; padding: 2rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; height: 300px;
                    transition: transform 0.3s ease; border-top: 4px solid #00a86b;">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; font-weight: 600;">Customer Profiling</h3>
            <p style="color: #7f8c8d; line-height: 1.6; font-size: 0.95rem;">
                Automated analysis of client requirements and investment goals from uploaded documents or manual entry.
            </p>
            <div style="margin-top: 1.5rem;">
                <span style="background: #00a86b; color: white;
                           padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                    AI-Powered
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: white; border: 1px solid #ecf0f1; border-radius: 16px; padding: 2rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; height: 300px;
                    transition: transform 0.3s ease; border-top: 4px solid #00a86b;">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; font-weight: 600;">Market Analysis</h3>
            <p style="color: #7f8c8d; line-height: 1.6; font-size: 0.95rem;">
                Advanced filtering and scoring of suburbs based on growth potential, rental yields, and risk factors.
            </p>
            <div style="margin-top: 1.5rem;">
                <span style="background: #3498db; color: white;
                           padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                    Data-Driven
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: white; border: 1px solid #ecf0f1; border-radius: 16px; padding: 2rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; height: 300px;
                    transition: transform 0.3s ease; border-top: 4px solid #00a86b;">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; font-weight: 600;">Investment Reports</h3>
            <p style="color: #7f8c8d; line-height: 1.6; font-size: 0.95rem;">
                Professional-grade reports with cash flow projections, suburb comparisons, and actionable recommendations.
            </p>
            <div style="margin-top: 1.5rem;">
                <span style="background: #9b59b6; color: white;
                           padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                    Professional
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

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
        st.subheader("Getting Started")

        st.markdown("""
        **Step 1: Customer Profiling**
        Upload customer discovery questionnaire or manually enter client requirements including:
        - Financial capacity and budget constraints
        - Investment goals and risk tolerance
        - Property preferences and location priorities

        **Step 2: Market Data Import**
        Import suburb data from sources like H-Tag, DSR, Suburb Finder, or upload your own CSV/Excel files with market metrics.

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

    with col2:
        st.markdown("### Quick Actions")

        if st.button("Start New Analysis", type="primary", use_container_width=True):
            update_workflow_step(1)
            st.session_state.current_page = 'customer_profile'
            st.rerun()

        if st.button("Import Sample Data", use_container_width=True):
            st.session_state.current_page = 'data_upload'
            st.rerun()

        if st.button("View Documentation", use_container_width=True):
            st.info("Documentation would open here")

        # System status
        st.markdown("---")
        st.markdown("**System Status**")

        col1_status, col2_status = st.columns(2)
        with col1_status:
            st.metric("Sessions Today", "0")
        with col2_status:
            st.metric("Reports Generated", "0")

    # Recent activity placeholder
    st.markdown("---")
    st.subheader("Recent Activity")

    if not st.session_state.get('profile_generated', False):
        st.info("No recent activity. Start by creating a customer profile.")
    else:
        # Show progress of current session
        progress_items = []

        if st.session_state.get('profile_generated'):
            progress_items.append("✓ Customer profile created")

        if st.session_state.get('data_uploaded'):
            progress_items.append("✓ Market data imported")

        if st.session_state.get('recommendations'):
            progress_items.append("✓ Recommendations generated")

        if progress_items:
            st.markdown("**Current Session Progress:**")
            for item in progress_items:
                st.write(item)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.85rem; padding: 1rem;">
        Property Insight Platform v1.0 | Professional Property Investment Analysis
    </div>
    """, unsafe_allow_html=True)