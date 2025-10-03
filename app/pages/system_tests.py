"""
System Testing Dashboard
Frontend UI for running and viewing test results
"""
import streamlit as st
import subprocess
import sys
from pathlib import Path
import time
from datetime import datetime
import json

from styles.global_styles import get_global_css, COLORS
from components.property_card import render_hero_section


def render_system_tests_page():
    """Render the system testing dashboard"""

    # Inject global CSS
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Hero Section
    render_hero_section(
        title="🧪 System Testing Dashboard",
        subtitle="Run comprehensive tests to validate application functionality"
    )

    # Initialize test results in session state
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}

    if 'last_test_run' not in st.session_state:
        st.session_state.last_test_run = None

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 Quick Tests",
        "📊 Test Results",
        "🔍 Data Validation",
        "🛠️ System Health"
    ])

    with tab1:
        render_quick_tests()

    with tab2:
        render_test_results()

    with tab3:
        render_data_validation()

    with tab4:
        render_system_health()


def render_quick_tests():
    """Render quick test execution interface"""

    st.subheader("🚀 Run Tests")

    st.info("""
    **About Testing:**
    - Tests validate core functionality and data integrity
    - Unit tests check individual components
    - Integration tests verify system workflows
    - UI tests validate interface components
    """)

    # Test suite selection
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Available Test Suites")

        test_suites = {
            "all": "🎯 All Tests (Comprehensive)",
            "data_processing": "📊 Data Processing Tests",
            "services": "⚙️ Service Layer Tests",
            "ui_components": "🎨 UI Component Tests"
        }

        selected_suite = st.radio(
            "Select Test Suite",
            options=list(test_suites.keys()),
            format_func=lambda x: test_suites[x],
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("### Quick Actions")

        if st.button("▶️ Run Tests", type="primary", use_container_width=True):
            run_test_suite(selected_suite)

        if st.button("🔄 Refresh Results", use_container_width=True):
            st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.test_results = {}
            st.session_state.last_test_run = None
            st.success("Test history cleared!")
            st.rerun()

    # Test configuration
    with st.expander("⚙️ Test Configuration"):
        col1, col2 = st.columns(2)

        with col1:
            verbose = st.checkbox("Verbose Output", value=True)
            show_warnings = st.checkbox("Show Warnings", value=True)

        with col2:
            stop_on_failure = st.checkbox("Stop on First Failure", value=False)
            coverage = st.checkbox("Generate Coverage Report", value=False)


def run_test_suite(suite_name):
    """Execute the selected test suite"""

    st.markdown("---")
    st.markdown("### 🔄 Running Tests...")

    # Map suite names to test files
    suite_files = {
        "all": ["tests/test_data_processing.py", "tests/test_services.py", "tests/test_ui_components.py"],
        "data_processing": ["tests/test_data_processing.py"],
        "services": ["tests/test_services.py"],
        "ui_components": ["tests/test_ui_components.py"]
    }

    test_files = suite_files.get(suite_name, [])

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    results = {
        'suite': suite_name,
        'timestamp': datetime.now().isoformat(),
        'tests_run': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'skipped': 0,
        'duration': 0,
        'details': []
    }

    start_time = time.time()

    try:
        # Run each test file
        for idx, test_file in enumerate(test_files):
            progress = (idx + 1) / len(test_files)
            progress_bar.progress(progress)
            status_text.text(f"Running {test_file}...")

            # Check if test file exists
            test_path = Path(test_file)
            if not test_path.exists():
                status_text.warning(f"⚠️ Test file not found: {test_file}")
                continue

            # Run pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse output (simplified)
            output = result.stdout + result.stderr

            # Count results (basic parsing)
            if "PASSED" in output:
                results['passed'] += output.count("PASSED")
            if "FAILED" in output:
                results['failed'] += output.count("FAILED")
            if "ERROR" in output:
                results['errors'] += output.count("ERROR")

            results['details'].append({
                'file': test_file,
                'output': output,
                'return_code': result.returncode
            })

        results['tests_run'] = results['passed'] + results['failed'] + results['errors']
        results['duration'] = time.time() - start_time

        # Store results
        st.session_state.test_results[suite_name] = results
        st.session_state.last_test_run = datetime.now()

        # Display summary
        progress_bar.progress(1.0)
        status_text.empty()

        display_test_summary(results)

    except subprocess.TimeoutExpired:
        st.error("⏱️ Test execution timed out (60s)")
    except Exception as e:
        st.error(f"❌ Error running tests: {str(e)}")


def display_test_summary(results):
    """Display test execution summary"""

    st.markdown("---")
    st.markdown("### 📊 Test Summary")

    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Tests", results['tests_run'])

    with col2:
        st.metric("✅ Passed", results['passed'])

    with col3:
        st.metric("❌ Failed", results['failed'])

    with col4:
        st.metric("⚠️ Errors", results['errors'])

    with col5:
        st.metric("⏱️ Duration", f"{results['duration']:.2f}s")

    # Success rate
    if results['tests_run'] > 0:
        success_rate = (results['passed'] / results['tests_run']) * 100
        st.progress(success_rate / 100)
        st.write(f"**Success Rate:** {success_rate:.1f}%")

        if success_rate == 100:
            st.success("🎉 All tests passed!")
            st.balloons()
        elif success_rate >= 80:
            st.warning("⚠️ Most tests passed, but some failures detected")
        else:
            st.error("❌ Multiple test failures detected")

    # Detailed results
    with st.expander("📝 Detailed Test Output"):
        for detail in results['details']:
            st.markdown(f"**File:** `{detail['file']}`")
            st.code(detail['output'], language='text')


def render_test_results():
    """Display historical test results"""

    st.subheader("📊 Test History")

    if not st.session_state.test_results:
        st.info("No test results available. Run tests from the 'Quick Tests' tab.")
        return

    # Display each test run
    for suite_name, results in st.session_state.test_results.items():
        with st.expander(f"📋 {suite_name.replace('_', ' ').title()} - {results['timestamp'][:19]}", expanded=True):

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Passed", results['passed'])
            with col2:
                st.metric("Failed", results['failed'])
            with col3:
                st.metric("Errors", results['errors'])
            with col4:
                st.metric("Duration", f"{results['duration']:.2f}s")

            # Show details
            if results.get('details'):
                st.markdown("**Test Files:**")
                for detail in results['details']:
                    status_icon = "✅" if detail['return_code'] == 0 else "❌"
                    st.write(f"{status_icon} {detail['file']}")


def render_data_validation():
    """Render data validation tests"""

    st.subheader("🔍 Data Validation")

    st.info("""
    Validate data integrity and structure for current session data.
    These tests run on your actual loaded data.
    """)

    if st.button("▶️ Run Validation", type="primary"):

        results = {
            'customer_profile': validate_customer_profile(),
            'suburb_data': validate_suburb_data(),
            'recommendations': validate_recommendations()
        }

        # Display results
        st.markdown("---")
        st.markdown("### Validation Results")

        for data_type, validation_result in results.items():
            with st.expander(f"📊 {data_type.replace('_', ' ').title()}", expanded=True):
                if validation_result['valid']:
                    st.success(f"✅ {data_type} is valid")
                else:
                    st.error(f"❌ {data_type} has issues")

                for check in validation_result['checks']:
                    status_icon = "✅" if check['passed'] else "❌"
                    st.write(f"{status_icon} {check['description']}")

                    if not check['passed'] and check.get('details'):
                        st.warning(f"   ⚠️ {check['details']}")


def validate_customer_profile():
    """Validate customer profile data"""

    checks = []
    profile = st.session_state.get('customer_profile')

    # Check if profile exists
    checks.append({
        'description': 'Customer profile exists',
        'passed': profile is not None,
        'details': 'No customer profile loaded' if profile is None else None
    })

    if profile:
        # Check required sections
        required_sections = ['financial_profile', 'investment_goals', 'property_preferences']
        for section in required_sections:
            checks.append({
                'description': f'Has {section} section',
                'passed': section in profile,
                'details': f'Missing {section}' if section not in profile else None
            })

        # Check preferred suburbs
        if 'property_preferences' in profile:
            suburbs = profile.get('property_preferences', {}).get('preferred_suburbs', [])
            checks.append({
                'description': 'Has preferred suburbs',
                'passed': isinstance(suburbs, list) and len(suburbs) > 0,
                'details': 'No preferred suburbs specified' if not suburbs else None
            })

    return {
        'valid': all(check['passed'] for check in checks),
        'checks': checks
    }


def validate_suburb_data():
    """Validate suburb data"""

    checks = []
    data = st.session_state.get('suburb_data')

    # Check if data exists
    checks.append({
        'description': 'Suburb data exists',
        'passed': data is not None,
        'details': 'No suburb data loaded' if data is None else None
    })

    if data is not None:
        import pandas as pd

        # Check it's a DataFrame
        is_df = isinstance(data, pd.DataFrame)
        checks.append({
            'description': 'Data is DataFrame',
            'passed': is_df,
            'details': f'Data type is {type(data)}' if not is_df else None
        })

        if is_df:
            # Check not empty
            checks.append({
                'description': 'Data is not empty',
                'passed': not data.empty,
                'details': 'DataFrame is empty' if data.empty else None
            })

            # Check required columns
            required_cols = ['Suburb', 'State', 'Median Price']
            for col in required_cols:
                checks.append({
                    'description': f'Has {col} column',
                    'passed': col in data.columns,
                    'details': f'Missing {col} column' if col not in data.columns else None
                })

            # Check data types
            if 'Median Price' in data.columns:
                checks.append({
                    'description': 'Median Price is numeric',
                    'passed': pd.api.types.is_numeric_dtype(data['Median Price']),
                    'details': None
                })

    return {
        'valid': all(check['passed'] for check in checks),
        'checks': checks
    }


def validate_recommendations():
    """Validate recommendations data"""

    checks = []
    recs = st.session_state.get('recommendations')

    # Check if recommendations exist
    checks.append({
        'description': 'Recommendations exist',
        'passed': recs is not None,
        'details': 'No recommendations generated' if recs is None else None
    })

    if recs:
        # Check structure
        checks.append({
            'description': 'Is dictionary',
            'passed': isinstance(recs, dict),
            'details': f'Type is {type(recs)}' if not isinstance(recs, dict) else None
        })

        if isinstance(recs, dict):
            # Check has recommendations
            has_recs = any(key in recs for key in ['primary_recommendations', 'ml_recommendations', 'rule_based'])
            checks.append({
                'description': 'Has recommendation data',
                'passed': has_recs,
                'details': 'No recommendation keys found' if not has_recs else None
            })

    return {
        'valid': all(check['passed'] for check in checks),
        'checks': checks
    }


def render_system_health():
    """Render system health checks"""

    st.subheader("🛠️ System Health")

    if st.button("🔍 Check System Health", type="primary"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📦 Dependencies")

            # Check key dependencies
            dependencies = {
                'streamlit': 'Core framework',
                'pandas': 'Data processing',
                'numpy': 'Numerical computing',
                'openai': 'AI services',
                'plotly': 'Visualizations',
                'pytest': 'Testing framework'
            }

            for package, description in dependencies.items():
                try:
                    __import__(package)
                    st.success(f"✅ {package} - {description}")
                except ImportError:
                    st.error(f"❌ {package} - {description} (NOT INSTALLED)")

        with col2:
            st.markdown("#### 🔧 Configuration")

            # Check configuration
            config_checks = []

            # API key
            api_key = st.session_state.get('user_openai_api_key')
            if api_key:
                st.success("✅ OpenAI API Key configured")
            else:
                st.warning("⚠️ OpenAI API Key not configured")

            # Session state
            if st.session_state:
                st.success(f"✅ Session state active ({len(st.session_state)} keys)")
            else:
                st.warning("⚠️ Session state empty")

            # Workflow status
            workflow_step = st.session_state.get('workflow_step', 1)
            st.info(f"ℹ️ Current workflow step: {workflow_step}/5")

        # File system checks
        st.markdown("---")
        st.markdown("#### 📁 File System")

        col1, col2 = st.columns(2)

        with col1:
            # Check test directory
            test_dir = Path("tests")
            if test_dir.exists():
                test_files = list(test_dir.glob("test_*.py"))
                st.success(f"✅ Tests directory ({len(test_files)} test files)")
            else:
                st.error("❌ Tests directory not found")

        with col2:
            # Check data directory
            data_dir = Path("data")
            if data_dir.exists():
                st.success("✅ Data directory exists")
            else:
                st.warning("⚠️ Data directory not found")
