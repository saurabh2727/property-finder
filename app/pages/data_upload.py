import streamlit as st
import pandas as pd
from utils.document_processor import DocumentProcessor
from utils.htag_processor import HtAGProcessor
from utils.session_state import update_workflow_step, save_suburb_data, backup_session_data, render_workflow_progress
from components.sample_files import render_sample_files_section
from styles.global_styles import get_global_css, COLORS
from components.property_card import render_hero_section
import plotly.express as px
import plotly.graph_objects as go

def render_data_upload_page():
    """Render the data upload and validation page"""

    # Inject global CSS
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Hero Section
    render_hero_section(
        title="📊 Data Upload & Integration",
        subtitle="Import suburb market data from multiple sources"
    )

    # Progress indicator
    render_workflow_progress(current_step=2)

    st.markdown("---")

    # Check prerequisites
    if not st.session_state.get('profile_generated', False):
        st.warning("⚠️ Please complete customer profiling first!")
        if st.button("← Go to Customer Profile"):
            st.session_state.current_page = 'customer_profile'
            st.rerun()
        return

    # Check if data already uploaded
    if st.session_state.get('data_uploaded', False) and st.session_state.get('suburb_data') is not None:
        display_uploaded_data()
    else:
        upload_new_data()

def upload_new_data():
    """Handle new data upload"""

    # Sample files section - foldable
    with st.expander("📥 Sample Files", expanded=False):
        render_sample_files_section()

    # Data source information
    with st.expander("📋 Supported Data Sources", expanded=False):
        st.markdown("""
        **Compatible Data Sources:**
        - **HtAG**: Real estate market data platform
        - **DSR (Data Services & Research)**: Property analytics
        - **Suburb Finder**: Demographic and market insights
        - **Price Finder**: Property valuation data
        - **CoreLogic**: Comprehensive property data
        - **Custom CSV/Excel**: Your own formatted data

        **Required Fields:**
        - Suburb, State, Region
        - Median Price, Rental Yield
        - Distance to CBD, Population
        - Supply & demand metrics
        - Performance indicators
        """)

    # File upload section - foldable
    with st.expander("📤 Upload Data File", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose your suburb data file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV or Excel file containing suburb market data"
        )

        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")

            # Process file button
            if st.button("📊 Process & Validate Data", type="primary"):
                process_uploaded_data(uploaded_file)

    # Alternative data entry options
    st.markdown("---")
    st.markdown("### Alternative Data Sources")

    # Check if converted data exists
    from pathlib import Path
    base_dir = Path(__file__).parent.parent.parent
    converted_data_path = base_dir / "data" / "processed" / "htag_converted.csv"
    has_converted_data = converted_data_path.exists()

    # Show buttons based on what's available
    if has_converted_data:
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🌐 Connect to API", use_container_width=True):
                show_api_connection_form()

        with col2:
            if st.button("✏️ Manual Entry", use_container_width=True):
                show_manual_data_entry()

        with col3:
            if st.button("⚡ Load Converted Data", use_container_width=True):
                load_converted_data()
    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🌐 Connect to API", use_container_width=True):
                show_api_connection_form()

        with col2:
            if st.button("✏️ Manual Entry", use_container_width=True):
                show_manual_data_entry()

def process_uploaded_data(uploaded_file):
    """Process and validate uploaded data file with automatic HtAG detection"""

    with st.spinner("🔄 Processing data file..."):
        try:
            # Load the data
            df = DocumentProcessor.load_data_file(uploaded_file)

            if df is None:
                st.error("Failed to load data file. Please check the format and try again.")
                return

            st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")

            # Initialize HtAG processor
            htag_processor = HtAGProcessor()

            # Step 1: Detect if this is HtAG format
            st.markdown("### 🔍 Data Format Detection")
            detection_result = htag_processor.detect_htag_format(df)

            col1, col2 = st.columns(2)

            with col1:
                if detection_result['is_htag']:
                    st.success(f"✅ **HtAG Format Detected** (Confidence: {detection_result['confidence']:.1%})")
                    st.write("**Column Mappings Found:**")
                    for standard, original in detection_result['column_mappings'].items():
                        st.write(f"  • {standard.replace('_', ' ').title()}: `{original}`")
                else:
                    st.info("ℹ️ **Standard Format Detected** - Processing as regular CSV")

            with col2:
                if detection_result['issues']:
                    st.warning("**Issues Detected:**")
                    for issue in detection_result['issues']:
                        st.write(f"  • {issue}")

            # Step 2: Process based on format
            if detection_result['is_htag']:
                st.markdown("### ⚙️ HtAG Data Processing")

                # Show user what will be processed
                with st.expander("🔍 Preview: Column Mapping", expanded=False):
                    mapping_df = pd.DataFrame([
                        {'HtAG Column': orig, 'Standard Column': std.replace('_', ' ').title()}
                        for std, orig in detection_result['column_mappings'].items()
                    ])
                    st.dataframe(mapping_df, use_container_width=True)

                # Show raw data sample
                with st.expander("📊 Raw Data Sample (Before Processing)", expanded=False):
                    st.write("**Raw column data types:**")
                    for col in df.columns:
                        sample_val = df[col].iloc[0] if len(df) > 0 else 'N/A'
                        st.write(f"  • {col}: {df[col].dtype} (sample: {sample_val})")
                    st.dataframe(df.head(3), use_container_width=True)

                # Process HtAG data
                processed_df = htag_processor.process_htag_data(df, detection_result)

                if processed_df is not None:
                    df = processed_df
                    st.success(f"✅ HtAG data processed successfully: {len(df)} suburbs")

                    # Show processed data sample
                    with st.expander("📊 Processed Data Sample (After Processing)", expanded=False):
                        st.write("**Processed column data types:**")
                        for col in df.columns:
                            sample_val = df[col].iloc[0] if len(df) > 0 else 'N/A'
                            st.write(f"  • {col}: {df[col].dtype} (sample: {sample_val})")
                        st.dataframe(df.head(3), use_container_width=True)
                else:
                    st.error("❌ HtAG processing failed, trying standard validation...")

            # Step 3: Standard validation
            st.markdown("### 📋 Data Validation")
            validation_results = DocumentProcessor.validate_suburb_data(df)

            # Display validation results
            display_validation_results(validation_results, df)

            # Step 4: Final processing decision
            can_proceed = validation_results["is_valid"] or len(validation_results["missing_critical_fields"]) <= 2

            # Debug information for processing decision
            with st.expander("🔍 Processing Decision Details", expanded=False):
                st.write("**Validation Results:**")
                st.write(f"  • Is Valid: {validation_results['is_valid']}")
                st.write(f"  • Missing Critical Fields: {len(validation_results['missing_critical_fields'])} (≤ 2 allowed)")
                st.write(f"  • Data Quality Issues: {len(validation_results['data_quality_issues'])}")
                st.write(f"  • Can Proceed: {can_proceed}")

                if validation_results['missing_critical_fields']:
                    st.write(f"  • Missing Fields: {validation_results['missing_critical_fields']}")
                if validation_results['data_quality_issues']:
                    st.write("  • Quality Issues:")
                    for issue in validation_results['data_quality_issues']:
                        st.write(f"    - {issue}")

            if can_proceed:
                # Clean the data
                df_cleaned = DocumentProcessor.clean_suburb_data(df)

                # Store in session state with backup
                save_suburb_data(df_cleaned)
                update_workflow_step(3)

                # Show final success
                st.markdown("### 🎉 Processing Complete")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Suburbs", len(df_cleaned))
                with col2:
                    numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
                    st.metric("Numeric Columns", len(numeric_cols))
                with col3:
                    completeness = (1 - df_cleaned.isnull().sum().sum() / (len(df_cleaned) * len(df_cleaned.columns))) * 100
                    st.metric("Data Completeness", f"{completeness:.1f}%")

                st.success("✅ Data uploaded and validated successfully!")
                st.rerun()
            else:
                st.error("❌ Data validation failed. Please review the issues above and upload a corrected file.")

        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

def display_validation_results(validation_results, df):
    """Display data validation results"""

    st.subheader("📋 Data Validation Results")

    # Overall status
    if validation_results["is_valid"]:
        st.success("✅ Data validation passed!")
    else:
        st.warning("⚠️ Data validation issues found")

    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", validation_results["row_count"])
    with col2:
        st.metric("Total Columns", validation_results["column_count"])
    with col3:
        missing_fields_count = len(validation_results["missing_critical_fields"])
        st.metric("Missing Fields", missing_fields_count)
    with col4:
        quality_issues_count = len(validation_results["data_quality_issues"])
        st.metric("Quality Issues", quality_issues_count)

    # Missing fields
    if validation_results["missing_critical_fields"]:
        st.warning("**Missing Critical Fields:**")
        for field in validation_results["missing_critical_fields"]:
            st.write(f"- {field}")

    # Data quality issues
    if validation_results["data_quality_issues"]:
        st.error("**Data Quality Issues:**")
        for issue in validation_results["data_quality_issues"]:
            st.write(f"- {issue}")

    # Suggestions
    if validation_results["suggestions"]:
        st.info("**Suggestions:**")
        for suggestion in validation_results["suggestions"]:
            st.write(f"- {suggestion}")

    # Preview data
    with st.expander("👀 Data Preview", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)

    # Column analysis
    with st.expander("📊 Column Analysis"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Available Columns")
            for i, col in enumerate(df.columns):
                st.write(f"{i+1}. {col}")

        with col2:
            st.subheader("Data Types")
            dtype_info = df.dtypes.astype(str).to_dict()
            for col, dtype in dtype_info.items():
                st.write(f"**{col}:** {dtype}")

def show_api_connection_form():
    """Show API connection form for external data sources"""

    st.subheader("🌐 API Data Connection")

    with st.form("api_connection_form"):
        api_source = st.selectbox(
            "Select Data Source",
            ["CoreLogic", "Domain", "Realestate.com.au", "Custom API"]
        )

        api_url = st.text_input("API Endpoint URL")
        api_key = st.text_input("API Key", type="password")

        # Additional parameters
        st.subheader("Query Parameters")
        state_filter = st.multiselect("States", ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"])
        max_records = st.number_input("Maximum Records", min_value=100, max_value=10000, value=1000)

        submitted = st.form_submit_button("🔗 Connect & Fetch Data")

        if submitted:
            st.info("🚧 API integration feature coming soon! Please use file upload for now.")

def show_manual_data_entry():
    """Show manual data entry interface"""

    st.subheader("✏️ Manual Data Entry")

    st.info("Enter suburb data manually. This is useful for small datasets or specific suburbs.")

    # Initialize session state for manual entries
    if 'manual_suburbs' not in st.session_state:
        st.session_state.manual_suburbs = []

    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)

        with col1:
            suburb = st.text_input("Suburb Name")
            state = st.selectbox("State", ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"])
            median_price = st.number_input("Median Price ($)", min_value=0, value=500000, step=10000)

        with col2:
            rental_yield = st.number_input("Rental Yield (%)", min_value=0.0, max_value=20.0, value=4.0, step=0.1)
            distance_cbd = st.number_input("Distance to CBD (km)", min_value=0, value=20)
            population = st.number_input("Population", min_value=0, value=15000)

        submitted = st.form_submit_button("➕ Add Suburb")

        if submitted and suburb:
            new_entry = {
                'Suburb': suburb,
                'State': state,
                'Median Price': median_price,
                'Rental Yield on Houses': rental_yield,
                'Distance (km) to CBD': distance_cbd,
                'Population': population
            }
            st.session_state.manual_suburbs.append(new_entry)
            st.success(f"Added {suburb}, {state}")

    # Display entered suburbs
    if st.session_state.manual_suburbs:
        st.subheader("Entered Suburbs")
        df_manual = pd.DataFrame(st.session_state.manual_suburbs)
        st.dataframe(df_manual, use_container_width=True)

        if st.button("💾 Save Manual Data"):
            save_suburb_data(df_manual)
            update_workflow_step(3)
            st.success("Manual data saved successfully!")
            st.rerun()

def load_sample_data():
    """Load sample data for demonstration"""

    sample_data = pd.DataFrame({
        'Suburb': ['Bondi', 'Parramatta', 'Richmond', 'Southbank', 'Fremantle', 'Glenelg'],
        'State': ['NSW', 'NSW', 'VIC', 'VIC', 'WA', 'SA'],
        'Region': ['Eastern Suburbs', 'Greater Western Sydney', 'Inner Melbourne', 'Inner Melbourne', 'Perth Metro', 'Adelaide Metro'],
        'Median Price': [1200000, 850000, 750000, 650000, 580000, 720000],
        'Rental Yield on Houses': [3.2, 4.5, 4.8, 4.1, 5.2, 4.3],
        'Distance (km) to CBD': [8, 25, 12, 2, 19, 11],
        'Population': [12500, 25000, 18000, 15000, 28000, 16500],
        'Vacancy Rate': [2.1, 3.2, 2.8, 3.5, 2.0, 2.9],
        'Sales Days on Market': [35, 28, 42, 38, 25, 33],
        '10 yr Avg. Annual Growth': [6.2, 5.8, 7.1, 8.2, 4.9, 5.5]
    })

    save_suburb_data(sample_data)
    update_workflow_step(3)

    st.success("✅ Sample data loaded successfully!")
    st.rerun()

def load_converted_data():
    """Load the pre-converted HtAG data"""

    try:
        from pathlib import Path

        # Get the path to converted data
        base_dir = Path(__file__).parent.parent.parent
        converted_data_path = base_dir / "data" / "processed" / "htag_converted.csv"

        if converted_data_path.exists():
            converted_data = pd.read_csv(converted_data_path)

            # Store in session state with backup
            save_suburb_data(converted_data)
            update_workflow_step(3)

            st.success("⚡ Converted HtAG data loaded successfully!")
            st.info(f"📊 **Data:** {len(converted_data)} suburbs with complete property metrics")
            st.rerun()

        else:
            st.error(f"Converted data file not found at: {converted_data_path}")
            st.info("💡 **Tip:** Run the converter script first or upload your HtAG data file")

    except Exception as e:
        st.error(f"Error loading converted data: {str(e)}")

def display_uploaded_data():
    """Display uploaded data with analysis options"""

    st.success("✅ Suburb data has been uploaded!")

    df = st.session_state.suburb_data

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Upload New Data", use_container_width=True):
            st.session_state.data_uploaded = False
            st.session_state.suburb_data = None
            st.rerun()

    with col2:
        if st.button("➡️ Continue to Analysis & Recommendations", type="primary", use_container_width=True):
            st.session_state.current_page = 'recommendations'
            update_workflow_step(3)
            st.rerun()

    with col3:
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📥 Download Data",
            csv_data,
            "suburb_data.csv",
            "text/csv",
            use_container_width=True
        )

    st.markdown("---")

    # Data overview
    st.subheader("📊 Data Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Suburbs", len(df))
    with col2:
        states = df['State'].nunique() if 'State' in df.columns else 0
        st.metric("States Covered", states)
    with col3:
        if 'Median Price' in df.columns:
            avg_price = df['Median Price'].mean()
            st.metric("Avg Median Price", f"${avg_price:,.0f}")
        else:
            st.metric("Avg Median Price", "N/A")
    with col4:
        if 'Rental Yield on Houses' in df.columns:
            avg_yield = df['Rental Yield on Houses'].mean()
            st.metric("Avg Rental Yield", f"{avg_yield:.1f}%")
        else:
            st.metric("Avg Rental Yield", "N/A")

    # Visualizations
    st.subheader("📈 Data Visualizations")

    tab1, tab2, tab3 = st.tabs(["Price Distribution", "Yield Analysis", "Geographic Spread"])

    with tab1:
        if 'Median Price' in df.columns and 'State' in df.columns:
            fig = px.box(df, x='State', y='Median Price', title="Median Price Distribution by State")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Price distribution chart requires 'Median Price' and 'State' columns")

    with tab2:
        if 'Rental Yield on Houses' in df.columns and 'Median Price' in df.columns:
            fig = px.scatter(df, x='Median Price', y='Rental Yield on Houses',
                           hover_data=['Suburb'] if 'Suburb' in df.columns else None,
                           title="Rental Yield vs Median Price")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Yield analysis requires 'Rental Yield on Houses' and 'Median Price' columns")

    with tab3:
        if 'State' in df.columns:
            state_counts = df['State'].value_counts()
            fig = px.pie(values=state_counts.values, names=state_counts.index,
                        title="Suburb Distribution by State")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Geographic spread chart requires 'State' column")

    # Data table
    with st.expander("🔍 View Full Dataset", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)