import streamlit as st
from utils.document_processor import DocumentProcessor
from services.openai_service import OpenAIService
from utils.session_state import update_workflow_step, save_customer_profile, backup_session_data
import json

def render_clean_customer_profile_page():
    """Render a clean customer profiling page"""

    st.title("Customer Profiling")
    st.markdown("**Analyze customer requirements and investment preferences**")

    # Progress indicator
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin: 1rem 0; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #3b82f6;">1. Customer Profile</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Current Step</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #d1d5db;">2. Data Import</div>
            <div style="font-size: 0.85rem; color: #9ca3af;">Next</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #d1d5db;">3. Analysis</div>
            <div style="font-size: 0.85rem; color: #9ca3af;">Pending</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #d1d5db;">4. Review</div>
            <div style="font-size: 0.85rem; color: #9ca3af;">Pending</div>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-weight: 600; color: #d1d5db;">5. Report</div>
            <div style="font-size: 0.85rem; color: #9ca3af;">Pending</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Check if profile already exists
    if st.session_state.get('profile_generated', False):
        display_existing_profile()
    else:
        collect_customer_profile()

def collect_customer_profile():
    """Collect customer profile information"""

    st.subheader("Upload Customer Discovery Document")

    st.info("""
    **Instructions:**
    Upload the completed customer discovery questionnaire. Supported formats: DOCX, PDF, TXT.
    The AI will analyze the document and extract key investment requirements and preferences.
    """)

    # File upload section
    uploaded_file = st.file_uploader(
        "Choose customer discovery document",
        type=['docx', 'pdf', 'txt'],
        help="Upload the completed customer questionnaire document"
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")

            # Process document button
            if st.button("Analyze Document with AI", type="primary"):
                analyze_customer_document(uploaded_file)

        # Quick options
        st.markdown("### Quick Options")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("📋 Enter Profile Manually", use_container_width=True):
                show_manual_profile_form()

        with col_b:
            if st.button("⚡ Load Sample Profile", use_container_width=True):
                load_sample_profile()

    with col2:
        st.markdown("### Key Information Required")
        st.markdown("""
        **Financial Profile:**
        - Annual household income
        - Available equity for investment
        - Current debt commitments
        - Cash available for deposit

        **Investment Goals:**
        - Primary investment purpose
        - Expected rental yield
        - Investment timeline
        - Risk tolerance level

        **Property Preferences:**
        - Preferred locations/suburbs
        - Property type preference
        - Budget range
        - Special requirements
        """)

def analyze_customer_document(uploaded_file):
    """Analyze uploaded customer document using AI"""

    with st.spinner("Analyzing customer document..."):
        try:
            # Extract text from document
            document_content = DocumentProcessor.process_document(uploaded_file)

            if not document_content:
                st.error("Could not extract content from the document. Please try a different file or enter information manually.")
                return

            # Show extracted content for review
            with st.expander("View Extracted Document Content"):
                st.text_area("Document Content", document_content, height=200, disabled=True)

            # Check API key before proceeding
            if not st.session_state.get('user_openai_api_key'):
                st.error("⚠️ Please enter your OpenAI API key in the sidebar before proceeding.")
                return

            # Analyze with AI
            openai_service = OpenAIService()
            customer_profile = openai_service.analyze_customer_profile(document_content)

            if customer_profile:
                save_customer_profile(customer_profile)
                update_workflow_step(2)

                st.success("Customer profile generated successfully")
                st.rerun()
            else:
                st.error("Failed to generate customer profile. Please try manual entry.")

        except Exception as e:
            st.error(f"Error analyzing document: {str(e)}")

def show_manual_profile_form():
    """Show manual profile entry form"""

    st.markdown("### Manual Customer Profile Entry")

    with st.form("manual_profile_form"):
        st.subheader("Financial Profile")

        col1, col2 = st.columns(2)
        with col1:
            annual_income = st.text_input("Annual Income", placeholder="e.g., $150,000")
            available_equity = st.text_input("Available Equity", placeholder="e.g., $200,000")
            cash_available = st.text_input("Cash Available", placeholder="e.g., $50,000")

        with col2:
            loan_capacity = st.text_input("Loan Capacity", placeholder="e.g., $800,000")
            current_debt = st.text_input("Current Debt", placeholder="e.g., $300,000")

        st.subheader("Investment Goals")

        col1, col2 = st.columns(2)
        with col1:
            primary_purpose = st.selectbox(
                "Primary Purpose",
                ["Capital Growth", "Rental Income", "Both", "Tax Benefits"]
            )
            investment_timeline = st.selectbox(
                "Investment Timeline",
                ["Short-term (1-3 years)", "Medium-term (3-7 years)", "Long-term (7+ years)"]
            )
            risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])

        with col2:
            target_yield = st.number_input("Target Rental Yield (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
            growth_expectation = st.number_input("Expected Growth Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)

        st.subheader("Property Preferences")

        col1, col2 = st.columns(2)
        with col1:
            preferred_suburbs = st.text_area("Preferred Suburbs", placeholder="Enter suburbs separated by commas")
            property_types = st.multiselect(
                "Property Types",
                ["House", "Unit/Apartment", "Townhouse", "Villa", "Land"]
            )

        with col2:
            min_price = st.number_input("Minimum Price ($)", min_value=0, value=400000, step=10000)
            max_price = st.number_input("Maximum Price ($)", min_value=0, value=800000, step=10000)
            bedroom_range = st.selectbox("Bedroom Range", ["1-2", "2-3", "3-4", "4+", "No preference"])

        st.subheader("Location Priorities")

        col1, col2 = st.columns(2)
        with col1:
            proximity_to_cbd = st.selectbox("Proximity to CBD", ["High", "Medium", "Low"])
            school_quality = st.selectbox("School Quality", ["High", "Medium", "Low"])

        with col2:
            transport_access = st.selectbox("Transport Access", ["High", "Medium", "Low"])
            shopping_amenities = st.selectbox("Shopping Amenities", ["High", "Medium", "Low"])

        experience_level = st.selectbox(
            "Investment Experience",
            ["First-time Investor", "Some Experience", "Experienced", "Portfolio Builder"]
        )

        buying_readiness = st.selectbox(
            "Buying Readiness",
            ["Ready to Buy", "Researching", "Planning", "Not Sure"]
        )

        additional_notes = st.text_area("Additional Notes", placeholder="Any special requirements or circumstances...")

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            # Create profile structure
            profile = {
                "financial_profile": {
                    "annual_income": annual_income,
                    "available_equity": available_equity,
                    "loan_capacity": loan_capacity,
                    "current_debt": current_debt,
                    "cash_available": cash_available
                },
                "investment_goals": {
                    "primary_purpose": primary_purpose,
                    "investment_timeline": investment_timeline,
                    "target_yield": str(target_yield),
                    "growth_expectation": str(growth_expectation),
                    "risk_tolerance": risk_tolerance
                },
                "property_preferences": {
                    "preferred_suburbs": preferred_suburbs.split(',') if preferred_suburbs else [],
                    "property_types": property_types,
                    "bedroom_range": bedroom_range,
                    "price_range": {"min": str(min_price), "max": str(max_price)},
                    "special_features": []
                },
                "lifestyle_factors": {
                    "proximity_to_cbd": proximity_to_cbd,
                    "school_quality": school_quality,
                    "transport_access": transport_access,
                    "shopping_amenities": shopping_amenities,
                    "future_development": "Medium"
                },
                "experience_level": experience_level,
                "buying_readiness": buying_readiness,
                "additional_notes": additional_notes
            }

            save_customer_profile(profile)
            update_workflow_step(2)

            st.success("Customer profile saved successfully")
            st.rerun()

def display_existing_profile():
    """Display existing customer profile with edit options"""

    st.success("Customer profile has been generated")

    profile = st.session_state.customer_profile

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Edit Profile", use_container_width=True):
            st.session_state.profile_generated = False
            st.rerun()

    with col2:
        if st.button("Continue to Data Import", type="primary", use_container_width=True):
            st.session_state.current_page = 'data_upload'
            update_workflow_step(2)
            st.rerun()

    with col3:
        if st.button("Export Profile", use_container_width=True):
            export_profile_json(profile)

    st.markdown("---")

    # Display profile information in clean cards
    st.subheader("Generated Customer Profile")

    # Financial Profile
    with st.expander("Financial Profile", expanded=True):
        financial = profile.get("financial_profile", {})
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Annual Income:** {financial.get('annual_income', 'Not specified')}")
            st.write(f"**Available Equity:** {financial.get('available_equity', 'Not specified')}")
            st.write(f"**Cash Available:** {financial.get('cash_available', 'Not specified')}")
        with col2:
            st.write(f"**Loan Capacity:** {financial.get('loan_capacity', 'Not specified')}")
            st.write(f"**Current Debt:** {financial.get('current_debt', 'Not specified')}")

    # Investment Goals
    with st.expander("Investment Goals"):
        goals = profile.get("investment_goals", {})
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Primary Purpose:** {goals.get('primary_purpose', 'Not specified')}")
            st.write(f"**Timeline:** {goals.get('investment_timeline', 'Not specified')}")
            st.write(f"**Risk Tolerance:** {goals.get('risk_tolerance', 'Not specified')}")
        with col2:
            st.write(f"**Target Yield:** {goals.get('target_yield', 'Not specified')}")
            st.write(f"**Growth Expectation:** {goals.get('growth_expectation', 'Not specified')}")

    # Property Preferences
    with st.expander("Property Preferences"):
        prefs = profile.get("property_preferences", {})
        col1, col2 = st.columns(2)
        with col1:
            suburbs = prefs.get('preferred_suburbs', [])
            st.write(f"**Preferred Suburbs:** {', '.join(suburbs) if suburbs else 'Not specified'}")
            st.write(f"**Property Types:** {', '.join(prefs.get('property_types', []))}")
        with col2:
            price_range = prefs.get('price_range', {})
            st.write(f"**Price Range:** ${price_range.get('min', 'Not specified')} - ${price_range.get('max', 'Not specified')}")
            st.write(f"**Bedroom Range:** {prefs.get('bedroom_range', 'Not specified')}")

    # Location Priorities
    with st.expander("Location Priorities"):
        lifestyle = profile.get("lifestyle_factors", {})
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**CBD Proximity:** {lifestyle.get('proximity_to_cbd', 'Not specified')}")
            st.write(f"**School Quality:** {lifestyle.get('school_quality', 'Not specified')}")
        with col2:
            st.write(f"**Transport Access:** {lifestyle.get('transport_access', 'Not specified')}")
            st.write(f"**Shopping Amenities:** {lifestyle.get('shopping_amenities', 'Not specified')}")

    # Additional Information
    with st.expander("Additional Information"):
        st.write(f"**Experience Level:** {profile.get('experience_level', 'Not specified')}")
        st.write(f"**Buying Readiness:** {profile.get('buying_readiness', 'Not specified')}")
        notes = profile.get('additional_notes', 'Not specified')
        if notes and notes != 'Not specified':
            st.write(f"**Additional Notes:** {notes}")

def load_sample_profile():
    """Load sample customer profile for testing"""

    try:
        import os
        from pathlib import Path

        # Get the path to sample profile
        base_dir = Path(__file__).parent.parent.parent
        sample_profile_path = base_dir / "data" / "raw" / "sample_customer_profile.json"

        if sample_profile_path.exists():
            with open(sample_profile_path, 'r') as f:
                sample_profile = json.load(f)

            # Store in session state with backup
            save_customer_profile(sample_profile)
            update_workflow_step(2)

            st.success("⚡ Sample customer profile loaded successfully!")
            st.info("🎯 **Profile:** Sarah Johnson - First-time investor looking for 2-3 bedroom apartment in Sydney northwest ($650K-$850K budget)")
            st.rerun()

        else:
            st.error(f"Sample profile file not found at: {sample_profile_path}")

    except Exception as e:
        st.error(f"Error loading sample profile: {str(e)}")

def export_profile_json(profile):
    """Export customer profile as JSON"""
    json_str = json.dumps(profile, indent=2)
    st.download_button(
        label="Download Profile JSON",
        data=json_str,
        file_name="customer_profile.json",
        mime="application/json"
    )