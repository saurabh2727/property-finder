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
    [data-testid="collapsedControl"],
    button[kind="header"],
    button[kind="headerNoPadding"] {
        display: none !important;
    }

    /* Force sidebar to stay visible and prevent collapse */
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        flex-shrink: 0 !important;
        transform: none !important;
        transition: none !important;
    }

    /* All child divs should use full width */
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] .css-1544g2n,
    [data-testid="stSidebar"] section {
        width: 100% !important;
        max-width: 100% !important;
        visibility: visible !important;
        display: block !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Ensure sidebar content is visible */
    [data-testid="stSidebar"] * {
        visibility: visible !important;
        max-width: 100% !important;
    }

    /* Make sure main content doesn't overlap */
    .main {
        margin-left: 280px !important;
    }

    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Hide collapse button in all states */
    section[data-testid="stSidebar"] button[kind="header"],
    section[data-testid="stSidebar"] button[kind="headerNoPadding"] {
        display: none !important;
    }
    </style>

    <script>
    // Force sidebar to stay open and expand content
    function fixSidebar() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            // Remove any collapsed classes
            sidebar.classList.remove('collapsed');
            sidebar.style.display = 'flex';
            sidebar.style.visibility = 'visible';
            sidebar.style.width = '280px';
            sidebar.style.minWidth = '280px';
            sidebar.style.maxWidth = '280px';
            sidebar.style.transform = 'none';

            // Force all child divs to use full width
            const sidebarDivs = sidebar.querySelectorAll('div, section');
            sidebarDivs.forEach(function(div) {
                div.style.width = '100%';
                div.style.maxWidth = '100%';
            });
        }

        // Adjust main content
        const main = document.querySelector('.main');
        if (main) {
            main.style.marginLeft = '280px';
        }
    }

    // Run on load
    setTimeout(fixSidebar, 100);

    // Run periodically to ensure sidebar stays open
    setInterval(function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar && sidebar.offsetWidth < 250) {
            fixSidebar();
        }
    }, 500);
    </script>
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

if __name__ == "__main__":
    main()