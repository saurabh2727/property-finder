import streamlit as st
from utils.session_state import get_workflow_progress

def render_sidebar():
    """Render the application sidebar with navigation and progress"""

    with st.sidebar:
        st.title("🏠 Property Insight")
        st.markdown("---")

        # Progress indicator
        progress = get_workflow_progress()
        st.progress(progress / 100)
        st.text(f"Progress: {progress:.0f}%")
        st.markdown("---")

        # Navigation menu
        st.subheader("Navigation")

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()

        if st.button("👤 Customer Profile", use_container_width=True):
            st.session_state.current_page = 'customer_profile'
            st.rerun()

        if st.button("📊 Data Upload", use_container_width=True):
            st.session_state.current_page = 'data_upload'
            st.rerun()

        if st.button("🔍 Suburb Analysis", use_container_width=True):
            st.session_state.current_page = 'suburb_analysis'
            st.rerun()

        if st.button("⭐ Recommendations", use_container_width=True):
            st.session_state.current_page = 'recommendations'
            st.rerun()

        if st.button("📋 Reports", use_container_width=True):
            st.session_state.current_page = 'reports'
            st.rerun()

        if st.button("🤖 AI Assistant", use_container_width=True):
            st.session_state.current_page = 'ai_chat'
            st.rerun()

        st.markdown("---")

        # Workflow steps indicator
        st.subheader("Workflow Steps")

        steps = [
            ("Customer Profile", st.session_state.get('profile_generated', False)),
            ("Data Upload", st.session_state.get('data_uploaded', False)),
            ("Analysis", st.session_state.get('analysis_complete', False)),
            ("Recommendations", st.session_state.get('recommendations') is not None),
            ("Report", st.session_state.get('final_report') is not None)
        ]

        for i, (step_name, is_complete) in enumerate(steps, 1):
            if is_complete:
                st.success(f"✅ {i}. {step_name}")
            elif i == st.session_state.workflow_step:
                st.info(f"🔄 {i}. {step_name}")
            else:
                st.text(f"⏳ {i}. {step_name}")

        st.markdown("---")

        # Help section
        with st.expander("ℹ️ Help"):
            st.write("""
            **Getting Started:**
            1. Upload customer requirements document
            2. Import suburb data from your sources
            3. Configure analysis parameters
            4. Review AI recommendations
            5. Generate detailed reports

            **Features:**
            - AI-powered customer profiling
            - ML-based property recommendations
            - Automated data analysis
            - Customizable filtering criteria
            - Detailed performance reports
            """)

        # Reset button
        if st.button("🔄 Reset All", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['current_page']:
                    del st.session_state[key]
            st.session_state.workflow_step = 1
            st.rerun()