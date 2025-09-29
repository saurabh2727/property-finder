import streamlit as st
from utils.session_state import get_workflow_progress

def render_clean_sidebar():
    """Render a clean, professional sidebar with minimal design"""

    with st.sidebar:
        # Hide the collapse button completely
        st.markdown("""
        <style>
        /* Try all possible collapse button selectors */
        button[kind="header"],
        button[kind="headerNoPadding"],
        .css-1rs6os,
        .css-1v0mbdj,
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapse"],
        [title*="collapse"],
        [title*="Collapse"],
        .e8zbici0,
        .css-14xtw13,
        .st-emotion-cache-1rs6os,
        .st-emotion-cache-1v0mbdj {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            pointer-events: none !important;
        }

        /* Hide any button that contains << symbol */
        button:contains("<<"),
        *:contains("<<") {
            display: none !important;
        }
        </style>

        <script>
        // JavaScript fallback to remove the button
        function removeCollapseButton() {
            // Find all possible collapse buttons and remove them
            const selectors = [
                'button[kind="header"]',
                'button[kind="headerNoPadding"]',
                '.css-1rs6os',
                '.css-1v0mbdj',
                '[data-testid="collapsedControl"]',
                '[data-testid="stSidebarCollapse"]',
                'button[title*="collapse"]',
                'button[title*="Collapse"]'
            ];

            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.remove());
            });

            // Also remove any button containing << text
            const allButtons = document.querySelectorAll('button');
            allButtons.forEach(button => {
                if (button.textContent.includes('<<') || button.innerHTML.includes('<<')) {
                    button.remove();
                }
            });
        }

        // Run immediately and periodically
        removeCollapseButton();
        setInterval(removeCollapseButton, 1000);

        // Run when DOM changes
        const observer = new MutationObserver(removeCollapseButton);
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        """, unsafe_allow_html=True)

        # Logo/Title area
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 1rem;">
            <h2 style="color: #1f2937; margin: 0; font-weight: 600;">Property Insight</h2>
            <p style="color: #6b7280; margin: 0; font-size: 0.9rem;">Investment Analysis Platform</p>
        </div>
        """, unsafe_allow_html=True)

        # Progress indicator
        progress = get_workflow_progress()
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-size: 0.8rem; color: #6b7280;">Progress</span>
                <span style="font-size: 0.8rem; color: #6b7280;">{progress:.0f}%</span>
            </div>
            <div style="background: #e5e7eb; border-radius: 4px; height: 6px;">
                <div style="background: #3b82f6; height: 6px; border-radius: 4px; width: {progress}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation menu
        st.markdown("**Navigation**")

        # Clean button styles
        button_style = """
        <style>
        .nav-button {
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            margin: 0.25rem 0;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
            width: 100%;
            color: #374151;
            font-weight: 500;
        }
        .nav-button:hover {
            background: #f3f4f6;
            border-color: #3b82f6;
        }
        .nav-button.active {
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
        }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)

        # Navigation buttons with cleaner approach
        current_page = st.session_state.get('current_page', 'home')

        nav_items = [
            ('home', 'Dashboard'),
            ('customer_profile', 'Customer Profile'),
            ('data_upload', 'Data Import'),
            ('suburb_analysis', 'Market Analysis'),
            ('recommendations', 'Recommendations'),
            ('agent_review', 'Agent Review'),
            ('reports', 'Reports'),
            ('ai_chat', 'AI Assistant'),
            ('user_guide', 'User Guide')
        ]

        for page_key, page_name in nav_items:
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()

        # Workflow status - minimal design
        st.markdown("---")
        st.markdown("**Workflow Status**")

        steps = [
            ("Customer Profile", st.session_state.get('profile_generated', False)),
            ("Data Import", st.session_state.get('data_uploaded', False)),
            ("Analysis Complete", st.session_state.get('analysis_complete', False)),
            ("Recommendations", st.session_state.get('recommendations') is not None),
            ("Final Report", st.session_state.get('final_report') is not None)
        ]

        for step_name, is_complete in steps:
            status_color = "#10b981" if is_complete else "#d1d5db"
            status_text = "Complete" if is_complete else "Pending"

            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: {status_color}; margin-right: 0.5rem;"></div>
                <span style="font-size: 0.85rem; color: #374151;">{step_name}</span>
                <span style="font-size: 0.75rem; color: #6b7280; margin-left: auto;">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

        # Help section - minimal
        st.markdown("---")

        with st.expander("Help & Support"):
            st.markdown("""
            **Quick Start:**
            1. Upload customer profile
            2. Import market data
            3. Run analysis
            4. Review recommendations
            5. Generate reports

            **Support:** support@propertyinsight.com
            """)

        # Reset functionality
        st.markdown("---")
        if st.button("Reset Session", help="Clear all data and start fresh"):
            for key in list(st.session_state.keys()):
                if key not in ['current_page']:
                    del st.session_state[key]
            st.session_state.workflow_step = 1
            st.rerun()