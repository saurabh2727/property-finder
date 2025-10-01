import streamlit as st
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.append(str(app_dir))

from pages.clean_home import render_clean_home_page
from pages.user_guide import render_user_guide_page
from pages.clean_customer_profile import render_clean_customer_profile_page
from pages.data_upload import render_data_upload_page
from pages.suburb_analysis import render_suburb_analysis_page
from pages.recommendations import render_recommendations_page
from pages.reports import render_reports_page
from pages.agent_review import render_agent_review_page
from components.clean_sidebar import render_clean_sidebar
from utils.session_state import initialize_session_state
from services.mcp_agent import render_chat_page
from styles.global_styles import get_global_css

# Inject custom CSS to remove top padding from all pages
st.markdown(
    """
    <style>
    /* Remove all top and bottom padding from the main container using Streamlit's data-testid attribute */
    [data-testid="stAppViewContainer"] > div {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    /* Hide header if present */
    header { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

def add_sidebar_toggle():
    """Add sidebar toggle functionality when sidebar is collapsed"""

    # Simple toggle button in the main content area
    if not st.session_state.get('sidebar_visible', True):
        if st.button("☰ Show Sidebar", key="sidebar_toggle"):
            st.session_state.sidebar_visible = True
            st.rerun()

    # Add CSS for better positioning
    st.markdown("""
    <style>
    /* Fixed position toggle button */
    .stButton[data-testid="baseButton-secondary"] {
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999 !important;
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    /* Always show toggle when sidebar is hidden */
    .main[data-sidebar-state="collapsed"] .sidebar-toggle {
        display: block !important;
    }
    </style>

    <script>
    // Simple detection script
    setTimeout(function() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        const main = document.querySelector('.main');

        if (main) {
            if (!sidebar || sidebar.offsetWidth < 50) {
                main.setAttribute('data-sidebar-state', 'collapsed');
            } else {
                main.setAttribute('data-sidebar-state', 'expanded');
            }
        }
    }, 1000);
    </script>
    """, unsafe_allow_html=True)

# Configure the page
st.set_page_config(
    page_title="Property Insight App",
    page_icon="⬆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Alternative: Disable sidebar collapse completely
def disable_sidebar_collapse():
    """Alternative approach: disable sidebar collapse button entirely"""
    st.markdown("""
    <style>
    /* Hide all possible sidebar collapse buttons */
    .css-1rs6os,
    [data-testid="collapsedControl"],
    .css-1v0mbdj,
    button[kind="header"],
    .css-14xtw13.e8zbici0 {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Force sidebar to stay visible */
    .css-1d391kg,
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 350px !important;
        min-width: 350px !important;
        max-width: 350px !important;
        position: relative !important;
    }
    /* Prevent any collapse animations */
    .css-1d391kg * {
        transition: none !important;
    }

    /* Hide the << symbol specifically */
    .css-1rs6os::before,
    .css-1rs6os::after {
        display: none !important;
    }

    /* Target the collapse button content */
    .css-1rs6os .css-1v0mbdj {
        display: none !important;
    }

    /* Make sure main content adjusts properly */
    .main .block-container {
        margin-left: 0 !important;
        padding-left: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Initialize session state with recovery
    initialize_session_state()

    # Show session recovery notification if applicable
    if st.session_state.get('session_backup_available', False) and not st.session_state.get('recovery_notification_shown', False):
        st.info("🔄 **Session Restored**: Your previous work has been automatically recovered.")
        st.session_state.recovery_notification_shown = True

    # Apply global design system
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Choose sidebar approach:
    # Option 1: Add toggle button when collapsed (current approach)
    # add_sidebar_toggle()

    # Option 2: Disable collapse entirely (recommended - simple and reliable)
    disable_sidebar_collapse()

    # Render clean sidebar
    render_clean_sidebar()

    # Route to appropriate page based on navigation
    page = st.session_state.get('current_page', 'home')

    if page == 'home':
        render_clean_home_page()
    elif page == 'user_guide':
        render_user_guide_page()
    elif page == 'customer_profile':
        render_clean_customer_profile_page()
    elif page == 'data_upload':
        render_data_upload_page()
    elif page == 'suburb_analysis':
        render_suburb_analysis_page()
    elif page == 'recommendations':
        render_recommendations_page()
    elif page == 'agent_review':
        render_agent_review_page()
    elif page == 'reports':
        render_reports_page()
    elif page == 'ai_chat':
        render_chat_page()

if __name__ == "__main__":
    main()