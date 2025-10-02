"""
API Key Configuration with Modal Dialog
Clean, compact interface with popup configuration window
"""
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

def _get_storage_key():
    """Generate a consistent key for localStorage"""
    return "property_finder_openai_api_key"

def save_key_to_browser(api_key):
    """Save API key to browser localStorage"""
    storage_key = _get_storage_key()

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

def load_key_from_browser():
    """Load API key from browser localStorage"""
    storage_key = _get_storage_key()

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;">
        <script>
            const STORAGE_KEY = '{storage_key}';

            try {{
                const encoded = localStorage.getItem(STORAGE_KEY);
                if (encoded && encoded !== 'null' && encoded !== 'undefined') {{
                    const apiKey = atob(encoded);
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: apiKey
                    }}, '*');
                }} else {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: null
                    }}, '*');
                }}
            }} catch(e) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: null
                }}, '*');
            }}
        </script>
    </body>
    </html>
    """
    return components.html(html_code, height=0)

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

def test_api_key(api_key):
    """Test if the API key is valid"""
    if not api_key or not api_key.strip():
        return False, "API key is empty"

    if not api_key.startswith('sk-'):
        return False, "Invalid API key format (should start with 'sk-')"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True, "✅ API key is valid!"
    except Exception as e:
        error_msg = str(e)
        if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
            return False, "❌ Invalid API key - please check and try again"
        elif "rate_limit" in error_msg:
            return False, "⚠️ Rate limit reached, but key appears valid"
        elif "insufficient_quota" in error_msg:
            return False, "⚠️ No quota remaining, but key is valid"
        else:
            return False, f"❌ Error testing key: {error_msg[:100]}"

def render_api_key_button_and_modal():
    """
    Renders a compact button that opens a modal for API configuration
    """

    # Initialize session state
    if 'user_openai_api_key' not in st.session_state:
        st.session_state.user_openai_api_key = None
    if 'api_key_tested' not in st.session_state:
        st.session_state.api_key_tested = False
    if 'api_key_load_attempted' not in st.session_state:
        st.session_state.api_key_load_attempted = False

    # Check for admin key
    admin_key_configured = False
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            admin_key_configured = True
            if not st.session_state.user_openai_api_key:
                st.session_state.user_openai_api_key = st.secrets['OPENAI_API_KEY']
    except:
        pass

    # Try to auto-load from browser on first run (only if no admin key)
    if not admin_key_configured and not st.session_state.api_key_load_attempted:
        loaded_key = load_key_from_browser()
        if loaded_key and isinstance(loaded_key, str) and loaded_key.startswith('sk-'):
            st.session_state.user_openai_api_key = loaded_key
        st.session_state.api_key_load_attempted = True

    # Determine status
    if admin_key_configured:
        status = "✅ Configured"
        button_type = "tertiary"
    elif st.session_state.user_openai_api_key:
        status = "✓ Active"
        button_type = "tertiary"
    else:
        status = "⚠️ Required"
        button_type = "secondary"

    # Compact button
    if st.button(f"🔑 API Config • {status}", use_container_width=True, type=button_type):
        show_api_config_modal(admin_key_configured)

    return st.session_state.user_openai_api_key

@st.dialog("🔑 API Configuration")
def show_api_config_modal(admin_key_configured):
    """Display API configuration modal"""

    if admin_key_configured:
        # Admin mode
        st.success("✅ **API Key Configured (Shared)**")
        st.info("""
        **Using Shared API Key**

        - ✓ Ready to use - No setup required
        - ✓ Works immediately
        - ⚠️ Usage costs shared across all users
        """)
        return

    # User mode - Personal API key
    st.markdown("### Your API Key")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.user_openai_api_key or "",
        placeholder="sk-proj-...",
        help="Enter your OpenAI API key - it will be saved in your browser",
        key="modal_api_key_input"
    )

    if api_key:
        # Update session state
        if api_key != st.session_state.user_openai_api_key:
            st.session_state.user_openai_api_key = api_key
            # Auto-save to browser when key changes
            save_key_to_browser(api_key)

        # Status badges
        col_status1, col_status2 = st.columns(2)
        with col_status1:
            if st.session_state.api_key_tested:
                st.success("✓ Validated")
        with col_status2:
            st.info("💾 Saved in browser")

        st.divider()

        # Action buttons
        col1, col2, col3 = st.columns([3, 3, 2])

        with col1:
            if st.button("🧪 Test Key", use_container_width=True):
                with st.spinner("Testing..."):
                    success, message = test_api_key(api_key)
                    if success:
                        st.session_state.api_key_tested = True
                        st.balloons()
                        st.success(message)
                    else:
                        st.session_state.api_key_tested = False
                        st.error(message)

        with col2:
            if st.button("✓ Done", type="primary", use_container_width=True):
                # Ensure saved before closing
                save_key_to_browser(api_key)
                st.rerun()

        with col3:
            if st.button("Clear", use_container_width=True):
                clear_key_from_browser()
                st.session_state.user_openai_api_key = None
                st.session_state.api_key_tested = False
                st.session_state.api_key_load_attempted = False
                st.rerun()

        # Help section
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            **How to use:**
            1. Enter your API key above (auto-saves to browser)
            2. Click "🧪 Test Key" to verify
            3. Click "✓ Done" when ready

            **Get your API key:**
            [OpenAI Platform →](https://platform.openai.com/api-keys)

            **Note:** Your key is automatically saved in your browser's localStorage and will persist across sessions. No need to re-enter on refresh!
            """)
    else:
        st.warning("⚠️ Please enter your OpenAI API key")
        st.markdown("[Get your API key from OpenAI →](https://platform.openai.com/api-keys)")

        # Show load button in case user has a saved key
        if st.button("🔄 Check for Saved Key", use_container_width=True):
            st.session_state.api_key_load_attempted = False
            st.rerun()
