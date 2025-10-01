"""
API Key management for Property Finder app
Supports both admin-configured keys (Streamlit secrets) and user-provided keys
"""
import streamlit as st

def render_api_key_input_with_storage():
    """
    Render API key input with session persistence

    Two modes:
    1. Admin mode: Use shared API key from Streamlit secrets (for deployment)
    2. User mode: Each user provides their own key (persists for their browser session)
    """

    st.markdown("**🔑 API Configuration**")

    # Try to load from Streamlit secrets first (admin key for shared use)
    admin_key_configured = False
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            admin_key_configured = True
            if 'user_openai_api_key' not in st.session_state:
                st.session_state.user_openai_api_key = st.secrets['OPENAI_API_KEY']
    except:
        pass

    # Mode 1: Admin key is configured (shared key for all users)
    if admin_key_configured:
        st.success("✅ API Key configured (Shared)")

        with st.expander("ℹ️ About API Key"):
            st.info("""
            **Using Shared API Key**

            An admin API key is configured for all users. This means:
            - ✅ No need to enter your own key
            - ✅ Starts working immediately
            - ⚠️ Usage costs are shared across all users

            If you prefer to use your own API key to track your own usage,
            contact the admin to disable the shared key.
            """)

        return st.session_state.user_openai_api_key

    # Mode 2: No admin key - each user provides their own
    else:
        # Initialize session state for user's key
        if 'user_openai_api_key' not in st.session_state:
            st.session_state.user_openai_api_key = None

        current_key = st.session_state.user_openai_api_key

        # Show input field
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=current_key if current_key else "",
            placeholder="sk-...",
            help="Enter your personal OpenAI API key - it will persist during your browser session",
            key="api_key_input"
        )

        # Update session state when key is entered
        if api_key_input and api_key_input != current_key:
            st.session_state.user_openai_api_key = api_key_input
            st.rerun()

        # Show status
        if st.session_state.user_openai_api_key:
            st.success("✅ API Key configured")

            # Option to clear
            if st.button("🗑️ Clear API Key", help="Clear your API key from this session"):
                st.session_state.user_openai_api_key = None
                st.rerun()
        else:
            st.warning("⚠️ Please enter your OpenAI API key to continue")
            st.caption("💡 Get your API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)")

        # Help section
        with st.expander("ℹ️ About API Keys"):
            st.markdown("""
            **Personal API Key Mode**

            - 🔐 Your API key is stored only in your browser session
            - 💰 You control your own OpenAI usage and costs
            - 🔄 Key persists while your browser tab is open
            - ⚠️ You'll need to re-enter it if you close the tab or refresh

            **To avoid re-entering:**
            The app admin can configure a shared API key in Streamlit secrets.
            See `.streamlit/README.md` for instructions.
            """)

        return st.session_state.user_openai_api_key
