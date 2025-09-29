import streamlit as st
import json
import pickle
import base64
from datetime import datetime
import pandas as pd

def initialize_session_state():
    """Initialize session state variables with persistence and recovery"""

    # Initialize session ID for tracking
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 1

    # Customer profile with persistence check
    if 'customer_profile' not in st.session_state:
        st.session_state.customer_profile = {}

    if 'profile_generated' not in st.session_state:
        st.session_state.profile_generated = False

    # Data upload with persistence check
    if 'suburb_data' not in st.session_state:
        st.session_state.suburb_data = None

    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False

    # Analysis with persistence check
    if 'filtered_suburbs' not in st.session_state:
        st.session_state.filtered_suburbs = None

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None

    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    # Reports
    if 'final_report' not in st.session_state:
        st.session_state.final_report = None

    # Session persistence flags
    if 'session_backup_available' not in st.session_state:
        st.session_state.session_backup_available = False

    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()

    # Auto-recover on initialization
    if not st.session_state.get('session_initialized', False):
        recovered = recover_session_data()
        st.session_state.session_initialized = True
        if recovered:
            st.session_state.session_backup_available = True

    # Create initial backup if we have data but no backup
    if (st.session_state.get('customer_profile') or
        st.session_state.get('suburb_data') is not None or
        st.session_state.get('recommendations') is not None) and \
       not st.session_state.get('session_backup_available', False):
        backup_session_data()

def backup_session_data():
    """Create a backup of current session data using browser localStorage simulation"""
    try:
        # Create backup data structure
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'workflow_step': st.session_state.get('workflow_step', 1),
            'customer_profile': st.session_state.get('customer_profile', {}),
            'profile_generated': st.session_state.get('profile_generated', False),
            'data_uploaded': st.session_state.get('data_uploaded', False),
            'analysis_complete': st.session_state.get('analysis_complete', False),
            'session_id': st.session_state.get('session_id', ''),
        }

        # Handle DataFrame serialization for suburb_data
        if st.session_state.get('suburb_data') is not None:
            try:
                # Convert DataFrame to JSON-serializable format
                backup_data['suburb_data_json'] = st.session_state.suburb_data.to_json()
                backup_data['has_suburb_data'] = True
            except Exception as e:
                st.warning(f"Could not backup suburb data: {e}")
                backup_data['has_suburb_data'] = False

        # Handle recommendations data
        if st.session_state.get('recommendations') is not None:
            try:
                # Serialize recommendations (can be dict or DataFrame)
                recs = st.session_state.recommendations
                if isinstance(recs, dict):
                    # Handle DataFrame values in dict
                    serialized_recs = {}
                    for key, value in recs.items():
                        if isinstance(value, pd.DataFrame):
                            serialized_recs[key] = value.to_json()
                        else:
                            serialized_recs[key] = value
                    backup_data['recommendations'] = serialized_recs
                else:
                    backup_data['recommendations'] = str(recs)  # Fallback
                backup_data['has_recommendations'] = True
            except Exception as e:
                st.warning(f"Could not backup recommendations: {e}")
                backup_data['has_recommendations'] = False

        # Store in session state for persistence across page changes
        st.session_state.session_backup = backup_data
        st.session_state.session_backup_available = True
        st.session_state.last_activity = datetime.now()

        return True
    except Exception as e:
        st.error(f"Failed to create session backup: {e}")
        return False

def recover_session_data():
    """Recover session data from backup if available"""
    try:
        backup_data = st.session_state.get('session_backup')
        if not backup_data:
            return False

        # Restore basic session data
        st.session_state.workflow_step = backup_data.get('workflow_step', 1)
        st.session_state.customer_profile = backup_data.get('customer_profile', {})
        st.session_state.profile_generated = backup_data.get('profile_generated', False)
        st.session_state.data_uploaded = backup_data.get('data_uploaded', False)
        st.session_state.analysis_complete = backup_data.get('analysis_complete', False)

        # Restore suburb data
        if backup_data.get('has_suburb_data', False) and 'suburb_data_json' in backup_data:
            try:
                st.session_state.suburb_data = pd.read_json(backup_data['suburb_data_json'])
            except Exception as e:
                st.warning(f"Could not restore suburb data: {e}")

        # Restore recommendations
        if backup_data.get('has_recommendations', False) and 'recommendations' in backup_data:
            try:
                recs_data = backup_data['recommendations']
                if isinstance(recs_data, dict):
                    # Deserialize DataFrames in the dict
                    restored_recs = {}
                    for key, value in recs_data.items():
                        if isinstance(value, str) and key.endswith('_recommendations'):
                            try:
                                restored_recs[key] = pd.read_json(value)
                            except:
                                restored_recs[key] = value
                        else:
                            restored_recs[key] = value
                    st.session_state.recommendations = restored_recs
                else:
                    st.session_state.recommendations = recs_data
            except Exception as e:
                st.warning(f"Could not restore recommendations: {e}")

        return True
    except Exception as e:
        st.warning(f"Failed to recover session data: {e}")
        return False

def update_workflow_step(step):
    """Update the current workflow step and backup data"""
    st.session_state.workflow_step = step
    backup_session_data()  # Auto-backup when workflow advances

def reset_session_state():
    """Reset all session state variables"""
    keys_to_reset = [
        'customer_profile', 'profile_generated', 'suburb_data', 'data_uploaded',
        'filtered_suburbs', 'recommendations', 'analysis_complete', 'final_report',
        'session_backup', 'session_backup_available'
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.workflow_step = 1
    st.session_state.current_page = 'home'

def get_workflow_progress():
    """Get the current workflow progress as percentage"""
    total_steps = 5
    return (st.session_state.workflow_step / total_steps) * 100

def save_customer_profile(profile_data):
    """Save customer profile and create backup"""
    st.session_state.customer_profile = profile_data
    st.session_state.profile_generated = True
    backup_session_data()

def save_suburb_data(data):
    """Save suburb data and create backup"""
    st.session_state.suburb_data = data
    st.session_state.data_uploaded = True
    backup_session_data()

def save_recommendations(recommendations):
    """Save recommendations and create backup"""
    st.session_state.recommendations = recommendations
    st.session_state.analysis_complete = True
    backup_session_data()

def get_session_status():
    """Get current session status for debugging"""
    return {
        'session_id': st.session_state.get('session_id', 'N/A'),
        'workflow_step': st.session_state.get('workflow_step', 1),
        'profile_generated': st.session_state.get('profile_generated', False),
        'data_uploaded': st.session_state.get('data_uploaded', False),
        'analysis_complete': st.session_state.get('analysis_complete', False),
        'backup_available': st.session_state.get('session_backup_available', False),
        'last_activity': st.session_state.get('last_activity', 'N/A')
    }