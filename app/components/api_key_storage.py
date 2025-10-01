"""
API Key management for Property Finder app
Supports both admin-configured keys (Streamlit secrets) and user-provided keys
with browser localStorage persistence
"""
import streamlit as st
import streamlit.components.v1 as components
import hashlib

def _get_storage_key():
    """Generate a consistent key for localStorage"""
    return "property_finder_openai_api_key"

def load_key_from_browser():
    """
    Load API key from browser localStorage
    Returns the API key if found, None otherwise
    """

    storage_key = _get_storage_key()

    # Create an HTML component that reads from localStorage and returns the value
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; font-family: monospace; }}
            #status {{ padding: 5px; font-size: 11px; color: #666; }}
        </style>
    </head>
    <body>
        <div id="status">Checking browser storage...</div>
        <script>
            const STORAGE_KEY = '{storage_key}';

            try {{
                const encoded = localStorage.getItem(STORAGE_KEY);
                if (encoded && encoded !== 'null' && encoded !== 'undefined') {{
                    const apiKey = atob(encoded);

                    // Send to parent via Streamlit's iframe API
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: apiKey
                    }}, '*');

                    document.getElementById('status').textContent = '✓ Found saved API key';
                    document.getElementById('status').style.color = 'green';
                }} else {{
                    document.getElementById('status').textContent = '○ No saved API key found';
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: null
                    }}, '*');
                }}
            }} catch(e) {{
                document.getElementById('status').textContent = '✗ Error: ' + e.message;
                document.getElementById('status').style.color = 'red';
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: null
                }}, '*');
            }}
        </script>
    </body>
    </html>
    """

    # Return the component value (will be the API key or None)
    return components.html(html_code, height=30)

def save_key_to_browser(api_key):
    """Save API key to browser localStorage"""

    storage_key = _get_storage_key()

    # JavaScript to save the key
    html_code = f"""
    <script>
        const STORAGE_KEY = '{storage_key}';
        const apiKey = `{api_key}`;

        try {{
            localStorage.setItem(STORAGE_KEY, btoa(apiKey));
            console.log('✅ API key saved successfully');
        }} catch(e) {{
            console.error('❌ Failed to save API key:', e);
        }}
    </script>
    """

    components.html(html_code, height=0)

def clear_key_from_browser():
    """Clear API key from browser localStorage"""

    storage_key = _get_storage_key()

    html_code = f"""
    <script>
        const STORAGE_KEY = '{storage_key}';

        try {{
            localStorage.removeItem(STORAGE_KEY);
            console.log('✅ API key cleared successfully');
        }} catch(e) {{
            console.error('❌ Failed to clear API key:', e);
        }}
    </script>
    """

    components.html(html_code, height=0)

def render_api_key_input_with_storage():
    """
    Render API key input with browser localStorage persistence

    Two modes:
    1. Admin mode: Use shared API key from Streamlit secrets (for deployment)
    2. User mode: Each user provides their own key (persists in browser localStorage)
    """

    st.markdown("**🔑 API Configuration**")

    # Inject localStorage helper functions
    inject_localstorage_script()

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

    # Mode 2: No admin key - each user provides their own with localStorage
    else:
        # Initialize session state
        if 'user_openai_api_key' not in st.session_state:
            st.session_state.user_openai_api_key = None

        if 'api_key_save_requested' not in st.session_state:
            st.session_state.api_key_save_requested = False

        if 'api_key_load_attempted' not in st.session_state:
            st.session_state.api_key_load_attempted = False

        # Try to auto-load from browser localStorage on first run
        if not st.session_state.api_key_load_attempted and not st.session_state.user_openai_api_key:
            st.caption("🔍 Checking browser storage for saved API key...")
            loaded_key = load_key_from_browser()

            if loaded_key and isinstance(loaded_key, str) and loaded_key.startswith('sk-'):
                st.session_state.user_openai_api_key = loaded_key
                st.session_state.api_key_save_requested = True
                st.session_state.api_key_load_attempted = True
                st.success("✅ Loaded your saved API key from browser!")
                st.rerun()
            else:
                st.session_state.api_key_load_attempted = True

        current_key = st.session_state.user_openai_api_key

        # Show input field
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=current_key if current_key else "",
            placeholder="sk-...",
            help="Enter your OpenAI API key - it will be saved in your browser and persist across sessions",
            key="api_key_input"
        )

        # Handle API key input
        if api_key_input:
            # Update session state if key changed
            if api_key_input != current_key:
                st.session_state.user_openai_api_key = api_key_input
                st.session_state.api_key_save_requested = False

            # Show save button if key is entered but not yet saved to browser
            col1, col2 = st.columns([3, 1])

            with col1:
                if not st.session_state.api_key_save_requested:
                    if st.button("💾 Save to Browser", type="primary", use_container_width=True, help="Save API key in browser localStorage"):
                        save_key_to_browser(api_key_input)
                        st.session_state.api_key_save_requested = True
                        st.success("✅ API Key saved in your browser! It will persist even after closing the tab.")
                        st.rerun()
                else:
                    st.success("✅ API Key saved in browser")

            with col2:
                if st.button("🗑️", help="Clear API key from browser"):
                    clear_key_from_browser()
                    st.session_state.user_openai_api_key = None
                    st.session_state.api_key_save_requested = False
                    st.session_state.api_key_load_attempted = False
                    st.rerun()

        else:
            st.warning("⚠️ Please enter your OpenAI API key to continue")
            st.caption("💡 Get your API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)")

            # Manual reload button
            if st.button("🔄 Reload from Browser Storage", help="Try to load previously saved API key"):
                st.session_state.api_key_load_attempted = False
                st.rerun()

        # Help section
        with st.expander("ℹ️ About API Keys & Browser Storage"):
            st.markdown("""
            **Personal API Key with Browser Storage**

            - 🔐 Your API key is encrypted and stored in your browser's localStorage
            - 💾 Persists across browser sessions - no need to re-enter!
            - 🔒 Only accessible from this browser on this device
            - 💰 You control your own OpenAI usage and costs
            - 🌐 Each browser/device needs the key saved separately

            **Security Note:**
            - localStorage is browser-specific and reasonably secure
            - For maximum security, use the admin-configured shared key mode
            - Never share your API key with others

            **To avoid manual entry entirely:**
            The app admin can configure a shared API key in Streamlit secrets.
            See `.streamlit/README.md` for instructions.
            """)

        return st.session_state.user_openai_api_key
