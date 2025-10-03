import streamlit as st
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.append(str(app_dir))

from pages.clean_home import render_clean_home_page
from pages.user_guide import render_user_guide_page
from pages.customer_profile import render_customer_profile_page
from pages.data_upload import render_data_upload_page
from pages.recommendations import render_recommendations_page
from pages.reports import render_reports_page
from pages.agent_review import render_agent_review_page
from pages.system_tests import render_system_tests_page
from components.clean_sidebar import render_clean_sidebar
from utils.session_state import initialize_session_state
from services.mcp_agent import render_chat_page
from styles.global_styles import get_global_css

# Inject custom CSS to remove top padding from all pages
st.markdown(
    """
    <style>
    /* Aggressive removal of all top spacing */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stAppViewContainer"] {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    [data-testid="stAppViewContainer"] > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-top: 0px !important;
    }

    .main {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    .main > div {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    .block-container {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    section[data-testid="stSidebar"] + section {
        padding-top: 0px !important;
    }

    /* Target the element container */
    .element-container:first-child {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    /* Hide header if present */
    header {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    /* Remove default Streamlit top spacing */
    [data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Force hero section to top */
    .hero-section:first-child,
    div:has(> .hero-section) {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
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
    /* Hide sidebar collapse button */
    [data-testid="collapsedControl"],
    button[kind="header"],
    button[kind="headerNoPadding"] {
        display: none !important;
    }

    /* Force sidebar to stay visible - simple approach */
    section[data-testid="stSidebar"] {
        width: 21rem !important;
        min-width: 21rem !important;
    }

    /* Adjust main content */
    .main {
        margin-left: 0 !important;
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
        render_customer_profile_page()
    elif page == 'data_upload':
        render_data_upload_page()
    elif page == 'recommendations':
        render_recommendations_page()
    elif page == 'agent_review':
        render_agent_review_page()
    elif page == 'reports':
        render_reports_page()
    elif page == 'ai_chat':
        render_chat_page()
    elif page == 'system_tests':
        render_system_tests_page()

if __name__ == "__main__":
    main()