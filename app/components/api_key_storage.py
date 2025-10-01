"""
API Key management for Property Finder app
Supports both admin-configured keys (Streamlit secrets) and user-provided keys
with browser localStorage persistence
"""
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

def _get_storage_key():
    """Generate a consistent key for localStorage"""
    return "property_finder_openai_api_key"

def test_api_key(api_key):
    """
    Test if the API key is valid by making a simple API call
    Returns (success: bool, message: str)
    """
    if not api_key or not api_key.strip():
        return False, "API key is empty"

    if not api_key.startswith('sk-'):
        return False, "Invalid API key format (should start with 'sk-')"

    try:
        # Create OpenAI client with the provided key
        client = OpenAI(api_key=api_key)

        # Make a minimal test call to verify the key works
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )

        return True, "✅ API key is valid!"

    except Exception as e:
        error_msg = str(e)

        # Parse common error types
        if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
            return False, "❌ Invalid API key - please check and try again"
        elif "rate_limit" in error_msg:
            return False, "⚠️ Rate limit reached, but key appears valid"
        elif "insufficient_quota" in error_msg:
            return False, "⚠️ No quota remaining, but key is valid"
        else:
            return False, f"❌ Error testing key: {error_msg[:100]}"

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

    # Initialize modal state
    if 'show_api_config_modal' not in st.session_state:
        st.session_state.show_api_config_modal = False

    # Try to load from Streamlit secrets first (admin key for shared use)
    admin_key_configured = False
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            admin_key_configured = True
            if 'user_openai_api_key' not in st.session_state:
                st.session_state.user_openai_api_key = st.secrets['OPENAI_API_KEY']
    except:
        pass

    # Determine status for button display
    if admin_key_configured:
        status_color = "#10b981"
        status_icon = "✓"
        status_text = "Configured"
    elif st.session_state.get('user_openai_api_key'):
        if st.session_state.get('api_key_save_requested', False):
            status_color = "#3b82f6"
            status_icon = "✓"
            status_text = "Saved"
        else:
            status_color = "#f59e0b"
            status_icon = "●"
            status_text = "Active"
    else:
        status_color = "#ef4444"
        status_icon = "!"
        status_text = "Required"

    # Compact button to open modal
    if st.button(f"{status_icon} **API Configuration** • {status_text}", use_container_width=True, help="Configure OpenAI API Key", type="secondary" if status_text == "Required" else "tertiary"):
        st.session_state.show_api_config_modal = True
        st.rerun()

    # Modal dialog using Streamlit's dialog
    @st.dialog("🔑 API Configuration", width="large")
    def show_api_config_dialog():
        """Display API configuration in a dialog"""

        # Mode 1: Admin key configured
        if admin_key_configured:
            st.success("✅ API Key Configured (Shared)")
            st.info("""
            **Using Shared API Key**

            - ✓ Ready to use - No setup required
            - ✓ Works immediately
            - ⚠️ Usage costs shared across all users
            """)

            if st.button("Close", use_container_width=True):
                st.session_state.show_api_config_modal = False
                st.rerun()
            return

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
            with st.spinner("🔍 Checking browser storage..."):
                loaded_key = load_key_from_browser()

            if loaded_key and isinstance(loaded_key, str) and loaded_key.startswith('sk-'):
                st.session_state.user_openai_api_key = loaded_key
                st.session_state.api_key_save_requested = True
                st.session_state.api_key_load_attempted = True
                st.markdown("""
                <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="color: #065f46; font-weight: 500; font-size: 0.9rem;">
                        ✅ API key loaded from browser storage
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.rerun()
            else:
                st.session_state.api_key_load_attempted = True

        current_key = st.session_state.user_openai_api_key

        # Show input field with better label
        st.markdown("""
        <div style="margin-bottom: 0.5rem;">
            <label style="font-size: 0.875rem; font-weight: 500; color: #374151;">
                OpenAI API Key
            </label>
        </div>
        """, unsafe_allow_html=True)

        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=current_key if current_key else "",
            placeholder="sk-proj-...",
            help="Your API key will be saved in browser localStorage",
            key="api_key_input",
            label_visibility="collapsed"
        )

        # Handle API key input
        if api_key_input:
            # Update session state if key changed
            if api_key_input != current_key:
                st.session_state.user_openai_api_key = api_key_input
                st.session_state.api_key_save_requested = False
                st.session_state.api_key_tested = False

            # Initialize test status
            if 'api_key_tested' not in st.session_state:
                st.session_state.api_key_tested = False

            # Status indicators
            if st.session_state.api_key_tested or st.session_state.api_key_save_requested:
                status_html = '<div style="display: flex; gap: 0.5rem; margin: 0.75rem 0; flex-wrap: wrap;">'

                if st.session_state.api_key_tested:
                    status_html += '''
                    <div style="background: #d1fae5; color: #065f46; padding: 0.375rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; display: flex; align-items: center; gap: 0.25rem;">
                        <span>✓</span>
                        <span>API key is valid</span>
                    </div>
                    '''

                if st.session_state.api_key_save_requested:
                    status_html += '''
                    <div style="background: #dbeafe; color: #1e40af; padding: 0.375rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; display: flex; align-items: center; gap: 0.25rem;">
                        <span>✓</span>
                        <span>Saved in browser</span>
                    </div>
                    '''

                status_html += '</div>'
                st.markdown(status_html, unsafe_allow_html=True)

            # Action buttons with improved styling
            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                # Test button with icon
                test_button_label = "🧪 Test API Key" if not st.session_state.api_key_tested else "🧪 Test Again"
                if st.button(test_button_label, use_container_width=True, help="Verify that your API key works", key="test_btn"):
                    with st.spinner("🔄 Testing API key..."):
                        success, message = test_api_key(api_key_input)
                        if success:
                            st.session_state.api_key_tested = True
                            st.balloons()
                            st.success(message)
                        else:
                            st.session_state.api_key_tested = False
                            st.error(message)

            with col2:
                # Save button
                if not st.session_state.api_key_save_requested:
                    if st.button("💾 Save to Browser", type="primary", use_container_width=True, help="Save API key in browser localStorage", key="save_btn"):
                        save_key_to_browser(api_key_input)
                        st.session_state.api_key_save_requested = True
                        st.success("✅ Saved! Your key will auto-load next time.")
                        st.rerun()
                else:
                    st.markdown("""
                    <div style="background: #dbeafe; border: 1px solid #60a5fa; color: #1e40af; padding: 0.5rem; border-radius: 6px; text-align: center; font-size: 0.875rem; font-weight: 500;">
                        ✓ Saved
                    </div>
                    """, unsafe_allow_html=True)

            with col3:
                if st.button("🗑️", help="Clear API key from browser", use_container_width=True, key="clear_btn"):
                    clear_key_from_browser()
                    st.session_state.user_openai_api_key = None
                    st.session_state.api_key_save_requested = False
                    st.session_state.api_key_load_attempted = False
                    st.session_state.api_key_tested = False
                    st.rerun()

        else:
            # No API key entered - show helpful prompt
            st.markdown("""
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #92400e; font-weight: 600; margin-bottom: 0.5rem;">
                    <span>⚠️</span>
                    <span>API Key Required</span>
                </div>
                <div style="color: #78350f; font-size: 0.875rem; line-height: 1.5;">
                    Please enter your OpenAI API key above to continue.
                    <br>
                    <a href="https://platform.openai.com/api-keys" target="_blank" style="color: #b45309; text-decoration: underline;">
                        Get your API key from OpenAI →
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Manual reload button
            if st.button("🔄 Check Browser Storage", help="Try to load previously saved API key", use_container_width=True):
                st.session_state.api_key_load_attempted = False
                st.rerun()

        # Help section with improved design
        with st.expander("💡 How to Setup & Use", expanded=False):
            st.markdown("""
            <div style="padding: 0.5rem;">
                <h4 style="margin-top: 0; color: #374151; font-size: 1rem;">Quick Start Guide</h4>

                <div style="background: #f3f4f6; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <div style="display: flex; gap: 1rem; margin-bottom: 0.75rem;">
                        <div style="background: #667eea; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; flex-shrink: 0;">1</div>
                        <div style="color: #374151;">
                            <strong>Enter your API key</strong> in the field above
                        </div>
                    </div>
                    <div style="display: flex; gap: 1rem; margin-bottom: 0.75rem;">
                        <div style="background: #667eea; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; flex-shrink: 0;">2</div>
                        <div style="color: #374151;">
                            <strong>Test it</strong> by clicking "🧪 Test API Key"
                        </div>
                    </div>
                    <div style="display: flex; gap: 1rem; margin-bottom: 0.75rem;">
                        <div style="background: #667eea; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; flex-shrink: 0;">3</div>
                        <div style="color: #374151;">
                            <strong>Save it</strong> by clicking "💾 Save to Browser"
                        </div>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <div style="background: #10b981; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; flex-shrink: 0;">✓</div>
                        <div style="color: #374151;">
                            <strong>Done!</strong> Your key will auto-load next time
                        </div>
                    </div>
                </div>

                <h4 style="color: #374151; font-size: 0.95rem; margin-top: 1.5rem;">Features</h4>
                <div style="color: #6b7280; font-size: 0.875rem; line-height: 1.7;">
                    ✓ <strong>Browser Storage:</strong> Key saved in localStorage<br>
                    ✓ <strong>Auto-Load:</strong> No need to re-enter each visit<br>
                    ✓ <strong>Validation:</strong> Test feature confirms key works<br>
                    ✓ <strong>Secure:</strong> Only accessible from your browser<br>
                    ✓ <strong>Private:</strong> You control your own costs<br>
                </div>

                <div style="background: #eff6ff; border-left: 3px solid #3b82f6; padding: 0.75rem; border-radius: 4px; margin-top: 1.5rem;">
                    <div style="color: #1e40af; font-size: 0.85rem; font-weight: 500;">
                        ℹ️ Admin Alternative
                    </div>
                    <div style="color: #1e3a8a; font-size: 0.8rem; margin-top: 0.25rem;">
                        Admins can configure a shared API key in Streamlit secrets to skip manual entry.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        return st.session_state.user_openai_api_key
