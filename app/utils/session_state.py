import streamlit as st

def initialize_session_state():
    """Initialize session state variables"""

    # Navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 1

    # Customer profile
    if 'customer_profile' not in st.session_state:
        st.session_state.customer_profile = {}

    if 'profile_generated' not in st.session_state:
        st.session_state.profile_generated = False

    # Data upload
    if 'suburb_data' not in st.session_state:
        st.session_state.suburb_data = None

    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False

    # Analysis
    if 'filtered_suburbs' not in st.session_state:
        st.session_state.filtered_suburbs = None

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None

    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    # Reports
    if 'final_report' not in st.session_state:
        st.session_state.final_report = None

def reset_session_state():
    """Reset all session state variables"""
    keys_to_reset = [
        'customer_profile', 'profile_generated', 'suburb_data', 'data_uploaded',
        'filtered_suburbs', 'recommendations', 'analysis_complete', 'final_report'
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.workflow_step = 1
    st.session_state.current_page = 'home'

def update_workflow_step(step):
    """Update the current workflow step"""
    st.session_state.workflow_step = step

def get_workflow_progress():
    """Get the current workflow progress as percentage"""
    total_steps = 5
    return (st.session_state.workflow_step / total_steps) * 100