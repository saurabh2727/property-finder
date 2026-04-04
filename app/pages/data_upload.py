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
                st.session_state.active_alt_form = 'api'
                st.rerun()

        with col2:
            if st.button("✏️ Manual Entry", use_container_width=True):
                st.session_state.active_alt_form = 'manual'
                st.rerun()

        with col3:
            if st.button("⚡ Load Converted Data", use_container_width=True):
                load_converted_data()
    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🌐 Connect to API", use_container_width=True):
                st.session_state.active_alt_form = 'api'
                st.rerun()

        with col2:
            if st.button("✏️ Manual Entry", use_container_width=True):
                st.session_state.active_alt_form = 'manual'
                st.rerun()

    # Render the active form persistently (survives button clicks inside)
    active_form = st.session_state.get('active_alt_form')
    if active_form == 'api':
        show_api_connection_form()
    elif active_form == 'manual':
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
    """Fetch suburb data from free Australian government APIs — all data categories."""
    import concurrent.futures
    from utils.data_cache import DataCache
    from services.data_fetcher.sa2_concordance import SA2Concordance
    from services.data_fetcher.abs_seifa_fetcher import ABSSEIFAFetcher
    from services.data_fetcher.abs_erp_fetcher import ABSERPFetcher
    from services.data_fetcher.abs_building_approvals_fetcher import ABSBuildingApprovalsFetcher
    from services.data_fetcher.abs_census_fetcher import ABSCensusFetcher
    from services.data_fetcher.nsw_sales_fetcher import NSWSalesFetcher
    from services.data_fetcher.vic_sales_fetcher import VICSalesFetcher
    from services.data_fetcher.qld_sales_fetcher import QLDSalesFetcher
    from services.data_fetcher.rental_data_fetcher import RentalDataFetcher
    from services.data_fetcher.acara_schools_fetcher import ACARASchoolsFetcher
    from services.data_fetcher.domain_fetcher import DomainListingsFetcher, DomainRentalAVMFetcher
    from services.data_fetcher.amenities_fetcher import AmenitiesFetcher
    from services.data_fetcher.transport_fetcher import TransportFetcher
    from services.data_fetcher.healthcare_fetcher import HealthcareFetcher
    from services.data_fetcher.crime_fetcher import CrimeFetcher
    from services.data_fetcher.employment_fetcher import EmploymentFetcher
    from services.data_fetcher.flood_risk_fetcher import FloodRiskFetcher
    from services.data_fetcher.walkability_fetcher import WalkabilityFetcher
    from services.data_fetcher.data_merger import DataMerger
    from utils.session_state import save_raw_dataset, set_fetch_status, save_suburb_data, update_workflow_step

    st.subheader("🌐 Connect to Data Sources")
    st.caption("Free Australian government + OpenStreetMap sources. Data is cached locally — subsequent loads are instant.")

    cache = DataCache()

    # ── Build suburb list from existing session data (used by OSM fetchers) ──
    suburb_list = []
    existing_df = st.session_state.get('suburb_data')
    if existing_df is not None:
        sc = "Suburb" if "Suburb" in existing_df.columns else "suburb"
        stc = "State" if "State" in existing_df.columns else "state"
        if sc in existing_df.columns and stc in existing_df.columns:
            suburb_list = (
                existing_df[[sc, stc]].dropna()
                .rename(columns={sc: "suburb", stc: "state"})
                .drop_duplicates()
                .to_dict("records")
            )

    osm_note = (
        f"Queries OpenStreetMap per suburb. {len(suburb_list)} suburbs loaded from current dataset. "
        "First fetch is slow (~1–2s/suburb) but cached for 30 days."
        if suburb_list else
        "Upload or load a suburb dataset first so OSM fetchers know which suburbs to query."
    )

    # ── Category status panel ────────────────────────────────────────────────
    cached_keys = {c["key"]: c for c in cache.list_cached()}

    def _status_badge(key):
        """Return (icon, label, colour_hint) for a cache key."""
        info = cached_keys.get(key)
        if info is None:
            return "⬜", "Not fetched", "grey"
        if info["fresh"] and info["row_count"] and int(str(info["row_count"]).replace("?", "0") or 0) > 0:
            return "🟢", f"{info['row_count']:,} rows  ·  {info['fetched_at']}", "green"
        if not info["fresh"]:
            return "🟡", f"Stale  ·  {info['row_count']} rows  ·  {info['fetched_at']}", "orange"
        return "🔴", "Empty (0 rows)", "red"

    # Define all categories with their source keys and metadata
    ALL_CATEGORIES = [
        {
            "label": "🏠 Demographics & Socioeconomic",
            "sources": [
                ("seifa",              "ABS SEIFA 2021",            "IRSD, IRSAD, IEO, IER deciles per SA2",                       True,  False),
                ("erp",                "ABS Population (ERP)",      "Estimated Resident Population + 5yr growth rate",             True,  False),
                ("census",             "ABS Census 2021",           "Household income, tenure, dwelling types per SA2",            False, True),
            ],
        },
        {
            "label": "📈 Property Market",
            "sources": [
                ("nsw_sales",          "NSW Property Sales",        "Median sale prices from NSW Valuer General",                  False, False),
                ("vic_sales",          "VIC Property Sales",        "Median sale prices from VIC Consumer Affairs",                False, False),
                ("qld_sales",          "QLD Property Sales",        "Median sale prices from QLD Titles Registry",                 False, False),
                ("rental",             "Rental Data (NSW & VIC)",   "Median weekly rent from state bond boards",                   False, False),
                ("domain_listings",    "Domain Listings",           "Active listings, median list price (API key required)",       False, False),
                ("domain_rental_avm",  "Domain Rental AVM",         "Rental estimates per suburb (API key required)",              False, False),
            ],
        },
        {
            "label": "🏫 Education",
            "sources": [
                ("acara_schools",      "ACARA My School (ICSEA)",   "School quality score, ICSEA median, school count per suburb", True,  False),
            ],
        },
        {
            "label": "🚌 Infrastructure & Transport",
            "sources": [
                ("transport",          "Public Transport (OSM)",    "Train stations, bus stops, tram stops per suburb",            True,  False),
                ("building_approvals", "ABS Building Approvals",    "New dwelling approvals — housing supply indicator",           True,  False),
            ],
        },
        {
            "label": "☕ Lifestyle & Amenities",
            "sources": [
                ("amenities",          "Amenities (OSM)",           "Cafes, restaurants, supermarkets, parks, gyms per suburb",    True,  False),
                ("walkability",        "Walkability (OSM)",         "Walk Score (0–100) and bike infrastructure score",            True,  False),
            ],
        },
        {
            "label": "🏥 Healthcare",
            "sources": [
                ("healthcare",         "Healthcare (OSM + AIHW)",   "Hospitals, GP clinics, pharmacies per suburb",                True,  False),
            ],
        },
        {
            "label": "🔒 Safety & Crime",
            "sources": [
                ("crime",              "Crime (BOCSAR / VIC)",      "Offence rate per 1,000 population (NSW & VIC LGA level)",     True,  False),
            ],
        },
        {
            "label": "💼 Employment",
            "sources": [
                ("employment",         "Employment (ABS Census)",   "Unemployment rate + labour force participation per SA2",      True,  False),
            ],
        },
        {
            "label": "🌊 Natural Hazard Risk",
            "sources": [
                ("flood_risk",         "Flood & Bushfire Risk",     "Flood risk score + bushfire risk score per suburb/SA2",       True,  False),
            ],
        },
    ]

    # ── Render category panels with status + checkboxes ──────────────────────
    st.markdown("### Select Data Sources")
    st.caption("🟢 Fresh  ·  🟡 Stale  ·  🔴 Empty  ·  ⬜ Not fetched  — status updates after each fetch")

    selections = {}  # key → bool
    KEY_TO_NAME = {key: name for cat in ALL_CATEGORIES for (key, name, *_) in cat["sources"]}

    # Only expand categories that have at least one source with data or that are "core"
    CORE_CATEGORIES = {"🏠 Demographics & Socioeconomic", "📈 Property Market", "🏫 Education"}
    OSM_SOURCES = {"amenities", "transport", "healthcare", "walkability"}
    ALWAYS_EMPTY = {"building_approvals"}  # stub fetchers — expected to return 0 rows

    # Official source URLs for each data source key
    KEY_TO_URL = {
        "seifa":              "https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/latest-release",
        "erp":                "https://www.abs.gov.au/statistics/people/population/regional-population/latest-release",
        "census":             "https://www.abs.gov.au/census/find-census-data/datapacks",
        "building_approvals": "https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/latest-release",
        "nsw_sales":          "https://www.valuergeneral.nsw.gov.au/land_values/summary_reports",
        "vic_sales":          "https://www.consumer.vic.gov.au/housing/buying-and-selling-property/buying-property/researching-a-property/recent-sales-data",
        "qld_sales":          "https://www.titles.qld.gov.au/property-data/property-sales-data",
        "rental":             "https://www.fairtrading.nsw.gov.au/housing-and-property/renting/rental-bond-data",
        "acara_schools":      "https://dataandreporting.blob.core.windows.net/anrdataportal/Data-Access-Program/School%20Profile%202025.xlsx",
        "domain_listings":    "https://developer.domain.com.au/",
        "domain_rental_avm":  "https://developer.domain.com.au/",
        "amenities":          "https://www.openstreetmap.org/",
        "transport":          "https://www.openstreetmap.org/",
        "healthcare":         "https://www.openstreetmap.org/",
        "crime":              "https://bocsar.nsw.gov.au/pages/bocsar/crime-statistics.html",
        "employment":         "https://www.abs.gov.au/census/find-census-data/datapacks",
        "flood_risk":         "https://www.ga.gov.au/scientific-topics/hazards/flood",
        "walkability":        "https://www.openstreetmap.org/",
    }

    # Map category key → schema source constant for column lookup
    from services.data_fetcher.column_schema import (
        columns_for_source as _cols_for_source,
        SOURCE_SEIFA, SOURCE_ERP, SOURCE_BUILDING, SOURCE_CENSUS,
        SOURCE_NSW_SALES, SOURCE_VIC_SALES, SOURCE_QLD_SALES, SOURCE_RENTAL_GOV,
        SOURCE_ACARA, SOURCE_DOMAIN_LISTINGS, SOURCE_DOMAIN_RENTAL,
        SOURCE_AMENITIES, SOURCE_TRANSPORT, SOURCE_HEALTHCARE,
        SOURCE_CRIME, SOURCE_EMPLOYMENT, SOURCE_FLOOD_RISK, SOURCE_WALKABILITY,
    )
    KEY_TO_SCHEMA_SOURCE = {
        "seifa":              SOURCE_SEIFA,
        "erp":                SOURCE_ERP,
        "building_approvals": SOURCE_BUILDING,
        "census":             SOURCE_CENSUS,
        "nsw_sales":          SOURCE_NSW_SALES,
        "vic_sales":          SOURCE_VIC_SALES,
        "qld_sales":          SOURCE_QLD_SALES,
        "rental":             SOURCE_RENTAL_GOV,
        "acara_schools":      SOURCE_ACARA,
        "domain_listings":    SOURCE_DOMAIN_LISTINGS,
        "domain_rental_avm":  SOURCE_DOMAIN_RENTAL,
        "amenities":          SOURCE_AMENITIES,
        "transport":          SOURCE_TRANSPORT,
        "healthcare":         SOURCE_HEALTHCARE,
        "crime":              SOURCE_CRIME,
        "employment":         SOURCE_EMPLOYMENT,
        "flood_risk":         SOURCE_FLOOD_RISK,
        "walkability":        SOURCE_WALKABILITY,
    }
    # Identity/join keys to exclude from the "provides" list
    _JOIN_COLS = {"Suburb", "State", "suburb", "state", "sa2_code", "Region"}

    for cat in ALL_CATEGORIES:
        # Auto-expand if it's a core category or has fresh data
        has_fresh = any(
            cached_keys.get(key, {}).get("fresh") and int(str(cached_keys.get(key, {}).get("row_count", 0) or 0)) > 0
            for (key, *_) in cat["sources"]
        )
        expand = cat["label"] in CORE_CATEGORIES or has_fresh

        with st.expander(cat["label"], expanded=expand):
            for (key, name, desc, default, needs_manual) in cat["sources"]:
                icon, badge_text, _ = _status_badge(key)
                col_check, col_status, col_cols = st.columns([2, 3, 3])
                with col_check:
                    disabled = (key in OSM_SOURCES and not suburb_list)
                    selections[key] = st.checkbox(
                        name,
                        value=default and not needs_manual and key not in ALWAYS_EMPTY,
                        key=f"src_{key}",
                        disabled=disabled,
                        help=(
                            f"{desc}"
                            + ("\n\n⚠️ Upload a suburb dataset first to enable this source." if disabled else "")
                            + ("\n\n⚙️ This source is a stub — always returns 0 rows by design." if key in ALWAYS_EMPTY else "")
                        ),
                    )
                with col_status:
                    extra = ""
                    if key in ALWAYS_EMPTY:
                        extra = "  <small style='color:#888'>⚙️ stub — no API available</small>"
                    elif key in OSM_SOURCES and not suburb_list:
                        extra = "  <small style='color:#e07b00'>⚠️ needs base dataset</small>"
                    elif needs_manual:
                        extra = "  <small style='color:#e07b00'>⚠️ manual download required</small>"
                    url = KEY_TO_URL.get(key, "")
                    source_link = (
                        f"<a href='{url}' target='_blank' style='color:#4a8fd4;font-size:11px;'>"
                        f"↗ Official source</a>"
                        if url else ""
                    )
                    st.markdown(
                        f"<small style='color:#555'>{desc}</small><br>"
                        f"<small>{icon} {badge_text}{extra}</small><br>"
                        f"{source_link}",
                        unsafe_allow_html=True,
                    )
                with col_cols:
                    schema_src = KEY_TO_SCHEMA_SOURCE.get(key)
                    if schema_src:
                        provided = [c for c in _cols_for_source(schema_src) if c not in _JOIN_COLS]
                        if provided:
                            visible = provided[:6]
                            hidden = provided[6:]
                            cols_text = ", ".join(f"<code style='font-size:10px'>{c}</code>" for c in visible)
                            st.markdown(
                                f"<small style='color:#888;font-size:11px'>📋 Provides:</small><br>{cols_text}",
                                unsafe_allow_html=True,
                            )
                            if hidden:
                                with st.popover(f"+{len(hidden)} more"):
                                    st.markdown(
                                        "**All columns provided by this source:**\n\n" +
                                        "\n".join(f"- `{c}`" for c in provided)
                                    )
                        else:
                            st.markdown("<small style='color:#aaa'>—</small>", unsafe_allow_html=True)
                    else:
                        st.markdown("<small style='color:#aaa'>—</small>", unsafe_allow_html=True)

    # ── Domain API key ────────────────────────────────────────────────────────
    use_domain = selections.get("domain_listings") or selections.get("domain_rental_avm")
    domain_key = None
    if use_domain:
        st.markdown("---")
        domain_key = st.text_input(
            "Domain API Key",
            type="password",
            value=st.session_state.get('domain_api_key', '') or '',
            help="Register free at developer.domain.com.au — 500 listing calls/day",
        )
        if domain_key:
            st.session_state.domain_api_key = domain_key
        else:
            st.warning("Domain API key required for Domain sources.")

    # ── ABS Census manual download warning ───────────────────────────────────
    if selections.get("census"):
        from pathlib import Path as _Path
        zip_path = _Path(__file__).parent.parent.parent / "data" / "raw" / "abs_census_2021_gcp_sa2.zip"
        if not zip_path.exists():
            st.warning(
                f"Census DataPack not found at `{zip_path}`.\n\n"
                "**To download:**\n"
                "1. Go to abs.gov.au → Census → DataPacks\n"
                "2. Select: 2021 → General Community Profile → SA2 → All of Australia\n"
                f"3. Save ZIP as: `{zip_path}`"
            )

    # ── OSM note ─────────────────────────────────────────────────────────────
    osm_selected = any(selections.get(k) for k in ("amenities", "transport", "healthcare", "walkability"))
    if osm_selected:
        st.info(f"**OpenStreetMap sources:** {osm_note}")

    st.markdown("---")
    force_refresh = st.checkbox("Force refresh (ignore cache)", value=False)

    # ── Fetch button ──────────────────────────────────────────────────────────
    selected_keys = {k for k, v in selections.items() if v}
    # Remove domain sources if no key
    if not domain_key:
        selected_keys.discard("domain_listings")
        selected_keys.discard("domain_rental_avm")

    if st.button("🚀 Fetch Selected Sources", type="primary", disabled=not selected_keys):
        if not selected_keys:
            st.warning("Please select at least one data source.")
            return

        def _fetch_domain_rental(c, api_key, suburbs):
            listings_fetcher = DomainListingsFetcher(c, api_key, suburbs[:20])
            listings_df = listings_fetcher._fetch_listings_for_suburbs(suburbs[:20])
            if listings_df.empty:
                return pd.DataFrame()
            rental_fetcher = DomainRentalAVMFetcher(c, api_key)
            return rental_fetcher.fetch_rental_estimates_for_suburbs(listings_df)

        fetcher_map = {
            "seifa":             lambda: ABSSEIFAFetcher(cache).fetch(force_refresh),
            "erp":               lambda: ABSERPFetcher(cache).fetch(force_refresh),
            "building_approvals":lambda: ABSBuildingApprovalsFetcher(cache).fetch(force_refresh),
            "census":            lambda: ABSCensusFetcher(cache).fetch(force_refresh),
            "nsw_sales":         lambda: NSWSalesFetcher(cache).fetch(force_refresh),
            "vic_sales":         lambda: VICSalesFetcher(cache).fetch(force_refresh),
            "qld_sales":         lambda: QLDSalesFetcher(cache).fetch(force_refresh),
            "rental":            lambda: RentalDataFetcher(cache).fetch(force_refresh),
            "acara_schools":     lambda: ACARASchoolsFetcher(cache).fetch(force_refresh),
            "domain_listings":   lambda: DomainListingsFetcher(cache, domain_key, suburb_list).fetch(force_refresh),
            "domain_rental_avm": lambda: _fetch_domain_rental(cache, domain_key, suburb_list),
            "amenities":         lambda: AmenitiesFetcher(cache, suburb_list).fetch(force_refresh),
            "transport":         lambda: TransportFetcher(cache, suburb_list).fetch(force_refresh),
            "healthcare":        lambda: HealthcareFetcher(cache, suburb_list).fetch(force_refresh),
            "crime":             lambda: CrimeFetcher(cache).fetch(force_refresh),
            "employment":        lambda: EmploymentFetcher(cache).fetch(force_refresh),
            "flood_risk":        lambda: FloodRiskFetcher(cache).fetch(force_refresh),
            "walkability":       lambda: WalkabilityFetcher(cache, suburb_list).fetch(force_refresh),
        }

        results = {}
        errors = {}
        progress = st.progress(0, text="Starting…")
        total = len(selected_keys)
        live_status = st.empty()

        def run_fetcher(key):
            set_fetch_status(key, "fetching")
            try:
                df = fetcher_map[key]()
                save_raw_dataset(key, df)
                return key, df, None
            except Exception as e:
                set_fetch_status(key, "failed")
                return key, pd.DataFrame(), str(e)

        # OSM fetchers run sequentially (rate limits); all others run in parallel
        osm_keys = {"amenities", "transport", "healthcare", "walkability"} & selected_keys
        parallel_keys = selected_keys - osm_keys
        completed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(run_fetcher, k): k for k in parallel_keys}
            for future in concurrent.futures.as_completed(futures):
                key, df, error = future.result()
                completed += 1
                progress.progress(completed / total, text=f"Fetched {completed}/{total}…")
                if error:
                    errors[key] = error
                else:
                    results[key] = df

        for key in osm_keys:
            live_status.info(f"🗺️ Querying OpenStreetMap for **{KEY_TO_NAME.get(key, key)}**…")
            key2, df, error = run_fetcher(key)
            completed += 1
            progress.progress(completed / total, text=f"Fetched {completed}/{total}…")
            if error:
                errors[key] = error
            else:
                results[key] = df

        live_status.empty()
        progress.empty()
        st.session_state.raw_fetched_datasets.update(results)
        if results or errors:
            st.session_state._api_fetch_results = results
            st.session_state._api_fetch_errors = errors

        # ── Grouped results summary ───────────────────────────────────────────
        st.markdown("#### Fetch Results")
        for cat in ALL_CATEGORIES:
            cat_keys = [key for (key, *_) in cat["sources"] if key in selected_keys]
            if not cat_keys:
                continue
            st.markdown(f"**{cat['label']}**")
            for key in cat_keys:
                friendly = KEY_TO_NAME.get(key, key)
                if key in errors:
                    st.error(f"❌ **{friendly}** — {errors[key]}")
                elif key in results:
                    n = len(results[key])
                    if n > 0:
                        st.success(f"✅ **{friendly}** — {n:,} rows")
                    elif key in ALWAYS_EMPTY:
                        st.info(f"⚙️ **{friendly}** — stub (no public API available, skipped in merge)")
                    elif key in OSM_SOURCES and not suburb_list:
                        st.warning(f"⚠️ **{friendly}** — skipped: no base suburb dataset loaded. Upload a CSV first, then re-fetch.")
                    elif key in OSM_SOURCES:
                        st.warning(f"⚠️ **{friendly}** — 0 rows: OpenStreetMap queries returned no results")
                    else:
                        st.warning(f"⚠️ **{friendly}** — 0 rows: source unavailable or URL has changed")
            st.markdown("")  # spacing between categories

        succeeded = sum(1 for k, df in results.items() if len(df) > 0 and k not in ALWAYS_EMPTY)
        failed = len(errors) + sum(1 for k, df in results.items() if len(df) == 0 and k not in ALWAYS_EMPTY)
        st.markdown(f"**Summary:** {succeeded} sources with data · {failed} empty/failed · {len(ALWAYS_EMPTY & selected_keys)} stubs skipped")

    # ── Merge section ─────────────────────────────────────────────────────────
    # Combine ALL previously fetched datasets (accumulated across multiple fetch runs)
    # with the results from this fetch run, so nothing is lost between button presses.
    fetch_results = {
        **st.session_state.get('raw_fetched_datasets', {}),
        **st.session_state.get('_api_fetch_results', {}),
    }
    if fetch_results:
        st.markdown("---")
        st.markdown("### Merge into Suburb Dataset")

        base_df = st.session_state.get('suburb_data')
        if base_df is not None:
            st.info(f"Base dataset: **{len(base_df)} suburbs** — API data will be joined as enrichment columns.")
        else:
            st.info("No base dataset loaded. The merger will attempt to build one from ABS ERP data.")

        # Show merge preview grouped by category with friendly names
        merge_rows = []
        for cat in ALL_CATEGORIES:
            for (key, name, desc, *_) in cat["sources"]:
                if key not in fetch_results:
                    continue
                df = fetch_results[key]
                n = len(df)
                merge_rows.append({
                    "Category": cat["label"],
                    "Source": name,
                    "Rows": f"{n:,}" if n else "—",
                    "Will merge": "✅ Yes" if n > 0 else ("⚙️ Stub" if key in ALWAYS_EMPTY else "⚠️ Skip"),
                })
        if merge_rows:
            st.dataframe(pd.DataFrame(merge_rows), use_container_width=True, hide_index=True)

        from services.data_fetcher.sa2_concordance import SA2Concordance
        from services.data_fetcher.data_merger import DataMerger

        if st.button("🔗 Merge & Save Dataset", type="primary"):
            with st.spinner("Merging all datasets…"):
                concordance = SA2Concordance(cache)
                concordance.load()
                merger = DataMerger(concordance)
                enriched = merger.merge(base_df, fetch_results)
                validation = merger.validate_enriched(enriched)

                save_suburb_data(enriched)
                st.session_state.data_source_mode = "api" if base_df is None else "hybrid"
                del st.session_state['_api_fetch_results']

            st.success(f"✅ Dataset ready — **{len(enriched)} suburbs**, **{len(enriched.columns)} columns**")

            # Coverage by category
            with st.expander("📊 Enrichment Coverage by Category", expanded=True):
                cov = validation.get("column_coverage", {})
                for cat in ALL_CATEGORIES:
                    cat_cols = []
                    for (key, name, desc, _, _) in cat["sources"]:
                        from services.data_fetcher.column_schema import columns_for_source
                        cat_cols += [(c, cov.get(c, "—")) for c in columns_for_source(key) if c in cov]
                    if cat_cols:
                        st.markdown(f"**{cat['label']}**")
                        cov_df = pd.DataFrame(cat_cols, columns=["Column", "Coverage"])
                        st.dataframe(cov_df, use_container_width=True, hide_index=True)

                for w in validation.get("warnings", []):
                    st.warning(w)

            with st.expander("Preview (first 10 rows)", expanded=False):
                st.dataframe(enriched.head(10), use_container_width=True)

            update_workflow_step(3)
            if st.button("Continue to Recommendations →"):
                st.session_state.current_page = 'recommendations'
                st.rerun()

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
        if 'State' in df.columns:
            real_states = df['State'].replace('N/A', pd.NA).dropna().nunique()
            st.metric("States Covered", real_states if real_states > 0 else "N/A")
        else:
            st.metric("States Covered", "N/A")
    with col3:
        if 'Median Price' in df.columns:
            avg_price = df['Median Price'].dropna()
            st.metric("Avg Median Price", f"${avg_price.mean():,.0f}" if len(avg_price) > 0 else "N/A")
        else:
            st.metric("Avg Median Price", "N/A")
    with col4:
        if 'Rental Yield on Houses' in df.columns:
            avg_yield = df['Rental Yield on Houses'].dropna()
            st.metric("Avg Rental Yield", f"{avg_yield.mean():.1f}%" if len(avg_yield) > 0 else "N/A")
        else:
            st.metric("Avg Rental Yield", "N/A")

    # Warn if price data is missing (API-only dataset)
    has_price = 'Median Price' in df.columns and df['Median Price'].notna().any()
    has_yield = 'Rental Yield on Houses' in df.columns and df['Rental Yield on Houses'].notna().any()
    has_state = 'State' in df.columns and df['State'].replace('N/A', pd.NA).notna().any()

    if not has_price:
        st.warning(
            "**No property price data** — ABS demographic sources don't include median prices. "
            "To add prices, also fetch **NSW Property Sales** or **VIC Property Sales**, or upload a CSV with price data."
        )

    # Visualizations
    st.subheader("📈 Data Visualizations")

    tab1, tab2, tab3 = st.tabs(["Price Distribution", "Yield Analysis", "Geographic Spread"])

    with tab1:
        if has_price and has_state:
            price_df = df[df['Median Price'].notna() & (df['State'] != 'N/A')]
            fig = px.box(price_df, x='State', y='Median Price', title="Median Price Distribution by State")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Price distribution requires Median Price data. Fetch NSW/VIC Sales or upload a CSV.")

    with tab2:
        if has_price and has_yield:
            yield_df = df[df['Median Price'].notna() & df['Rental Yield on Houses'].notna()]
            fig = px.scatter(yield_df, x='Median Price', y='Rental Yield on Houses',
                           hover_data=['Suburb'] if 'Suburb' in yield_df.columns else None,
                           title="Rental Yield vs Median Price")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Yield analysis requires both Median Price and Rental Yield data.")

    with tab3:
        if has_state:
            state_counts = df[df['State'] != 'N/A']['State'].value_counts()
            fig = px.pie(values=state_counts.values, names=state_counts.index,
                        title="Suburb Distribution by State")
            st.plotly_chart(fig, use_container_width=True)
        elif 'erp_population' in df.columns:
            # Show population distribution as fallback
            top20 = df.nlargest(20, 'erp_population')[['Suburb', 'erp_population']]
            fig = px.bar(top20, x='Suburb', y='erp_population', title="Top 20 Suburbs by Population")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Geographic spread chart requires a 'State' column.")

    # Data table
    with st.expander("🔍 View Full Dataset", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)