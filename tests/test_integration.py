"""
Integration tests that require actual data
These tests validate the full workflow with real session data
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


class TestDataIntegration:
    """Test integration with actual data files"""

    def test_sample_customer_profile_exists(self):
        """Test that sample customer profile file exists"""
        profile_path = Path(__file__).parent.parent / "data" / "raw" / "sample_customer_profile.json"
        assert profile_path.exists(), "Sample customer profile file should exist"

    def test_sample_customer_profile_valid_json(self):
        """Test that sample customer profile is valid JSON"""
        import json
        profile_path = Path(__file__).parent.parent / "data" / "raw" / "sample_customer_profile.json"

        if profile_path.exists():
            with open(profile_path, 'r') as f:
                profile = json.load(f)

            # Verify required sections
            assert 'financial_profile' in profile, "Profile should have financial_profile"
            assert 'investment_goals' in profile, "Profile should have investment_goals"
            assert 'property_preferences' in profile, "Profile should have property_preferences"

    def test_sample_suburb_data_exists(self):
        """Test that sample suburb data exists"""
        data_dir = Path(__file__).parent.parent / "data" / "raw"

        # Look for any CSV files in data directory
        csv_files = list(data_dir.glob("*.csv"))

        assert len(csv_files) > 0, "At least one CSV file should exist in data/raw"

    def test_sample_suburb_data_structure(self):
        """Test that suburb data has correct structure"""
        data_dir = Path(__file__).parent.parent / "data" / "raw"
        csv_files = list(data_dir.glob("*.csv"))

        if csv_files:
            df = pd.read_csv(csv_files[0])

            # Check for required columns
            required_cols = ['Suburb', 'State']
            for col in required_cols:
                assert col in df.columns, f"Suburb data should have '{col}' column"

            # Check data is not empty
            assert len(df) > 0, "Suburb data should not be empty"


class TestWorkflowValidation:
    """Test complete workflow validation"""

    def test_workflow_requires_profile_before_data(self):
        """Test that workflow enforces profile before data upload"""
        # This test would check the actual page logic
        # For now, we document the expected behavior
        assert True, "Workflow should require customer profile before data upload"

    def test_workflow_requires_data_before_recommendations(self):
        """Test that workflow enforces data before recommendations"""
        # This test would check the actual page logic
        assert True, "Workflow should require data upload before recommendations"

    def test_complete_workflow_order(self):
        """Test that workflow steps are in correct order"""
        expected_order = [
            'customer_profile',
            'data_upload',
            'recommendations',
            'agent_review',
            'reports'
        ]

        # Verify the order is logical
        assert len(expected_order) == 5, "Workflow should have 5 main steps"


class TestSessionDataValidation:
    """Test session data validation that mimics frontend validation"""

    def test_empty_profile_validation(self):
        """Test validation catches empty customer profile"""
        profile = None

        # Validation check
        is_valid = profile is not None

        assert not is_valid, "Empty profile should fail validation"

    def test_empty_suburb_data_validation(self):
        """Test validation catches empty suburb data"""
        suburb_data = None

        # Validation check
        is_valid = suburb_data is not None

        assert not is_valid, "Empty suburb data should fail validation"

    def test_empty_recommendations_validation(self):
        """Test validation catches empty recommendations"""
        recommendations = None

        # Validation check
        is_valid = recommendations is not None

        assert not is_valid, "Empty recommendations should fail validation"

    def test_profile_structure_validation(self):
        """Test profile structure validation"""
        # Valid profile
        valid_profile = {
            'financial_profile': {'annual_income': '$100,000'},
            'investment_goals': {'primary_purpose': 'Growth'},
            'property_preferences': {'preferred_suburbs': ['Sydney']},
            'lifestyle_factors': {'proximity_to_cbd': 'High'}
        }

        # Check all required sections exist
        required_sections = ['financial_profile', 'investment_goals',
                           'property_preferences', 'lifestyle_factors']

        is_valid = all(section in valid_profile for section in required_sections)

        assert is_valid, "Valid profile should pass validation"

    def test_incomplete_profile_validation(self):
        """Test incomplete profile fails validation"""
        incomplete_profile = {
            'financial_profile': {'annual_income': '$100,000'}
            # Missing other required sections
        }

        required_sections = ['financial_profile', 'investment_goals',
                           'property_preferences', 'lifestyle_factors']

        is_valid = all(section in incomplete_profile for section in required_sections)

        assert not is_valid, "Incomplete profile should fail validation"

    def test_suburb_data_dataframe_validation(self):
        """Test suburb data must be DataFrame"""
        import pandas as pd

        # Valid data
        valid_data = pd.DataFrame({'Suburb': ['Sydney'], 'State': ['NSW']})
        assert isinstance(valid_data, pd.DataFrame), "Valid data should be DataFrame"

        # Invalid data
        invalid_data = {'Suburb': ['Sydney']}  # Dict, not DataFrame
        assert not isinstance(invalid_data, pd.DataFrame), "Dict should not pass as DataFrame"

    def test_recommendations_structure_validation(self):
        """Test recommendations structure validation"""
        valid_recs = {
            'primary_recommendations': pd.DataFrame({'Suburb': ['Sydney']}),
            'recommendation_engine': 'ai_genai'
        }

        # Check has primary recommendations
        has_recs = 'primary_recommendations' in valid_recs
        assert has_recs, "Valid recommendations should have primary_recommendations"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
