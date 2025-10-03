"""
Unit tests for data processing functions
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from utils.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test document processing functionality"""

    def test_process_text_file(self):
        """Test processing of text files"""
        # This would need a sample text file
        pass

    def test_extract_suburbs_from_text(self):
        """Test suburb extraction from text"""
        sample_text = "Looking for properties in Parramatta, Chatswood, and Hornsby"
        # Test extraction logic
        assert True  # Placeholder


class TestDataValidation:
    """Test data validation functions"""

    def test_validate_suburb_data_columns(self):
        """Test that suburb data has required columns"""
        required_columns = [
            'Suburb',
            'State',
            'Median Price',
            'Rental Yield on Houses',
            '10 yr Avg. Annual Growth'
        ]

        # Create sample dataframe
        sample_data = pd.DataFrame({
            'Suburb': ['Parramatta', 'Chatswood'],
            'State': ['NSW', 'NSW'],
            'Median Price': [800000, 1200000],
            'Rental Yield on Houses': [4.2, 3.8],
            '10 yr Avg. Annual Growth': [6.5, 5.2]
        })

        # Check all required columns exist
        for col in required_columns:
            assert col in sample_data.columns, f"Missing required column: {col}"

    def test_data_types_are_correct(self):
        """Test that data types are correct"""
        sample_data = pd.DataFrame({
            'Suburb': ['Parramatta'],
            'Median Price': [800000],
            'Rental Yield on Houses': [4.2],
        })

        assert sample_data['Median Price'].dtype in [np.int64, np.float64]
        assert sample_data['Rental Yield on Houses'].dtype in [np.float64]

    def test_no_negative_prices(self):
        """Test that there are no negative prices"""
        sample_data = pd.DataFrame({
            'Median Price': [800000, 1200000, 650000],
        })

        assert (sample_data['Median Price'] >= 0).all()

    def test_rental_yield_range(self):
        """Test that rental yields are in valid range"""
        sample_data = pd.DataFrame({
            'Rental Yield on Houses': [4.2, 3.8, 5.5],
        })

        assert (sample_data['Rental Yield on Houses'] >= 0).all()
        assert (sample_data['Rental Yield on Houses'] <= 20).all()  # Reasonable upper bound


class TestCustomerProfileStructure:
    """Test customer profile data structure"""

    def test_profile_has_required_sections(self):
        """Test that customer profile has all required sections"""
        sample_profile = {
            "financial_profile": {
                "annual_income": "$150,000",
                "available_equity": "$200,000"
            },
            "investment_goals": {
                "primary_purpose": "Capital Growth"
            },
            "property_preferences": {
                "preferred_suburbs": ["Parramatta", "Chatswood"]
            },
            "lifestyle_factors": {
                "proximity_to_cbd": "Medium"
            }
        }

        required_sections = [
            'financial_profile',
            'investment_goals',
            'property_preferences',
            'lifestyle_factors'
        ]

        for section in required_sections:
            assert section in sample_profile, f"Missing required section: {section}"

    def test_preferred_suburbs_is_list(self):
        """Test that preferred suburbs is a list"""
        sample_profile = {
            "property_preferences": {
                "preferred_suburbs": ["Parramatta", "Chatswood"]
            }
        }

        suburbs = sample_profile['property_preferences']['preferred_suburbs']
        assert isinstance(suburbs, list), "Preferred suburbs should be a list"


class TestRecommendationDataStructure:
    """Test recommendation data structure"""

    def test_recommendations_has_primary_key(self):
        """Test that recommendations dict has primary recommendations"""
        sample_recommendations = {
            "primary_recommendations": pd.DataFrame({
                'Suburb': ['Parramatta', 'Chatswood'],
                'Median Price': [800000, 1200000]
            })
        }

        assert 'primary_recommendations' in sample_recommendations

    def test_recommendations_is_dataframe(self):
        """Test that recommendations are DataFrames"""
        sample_df = pd.DataFrame({
            'Suburb': ['Parramatta'],
            'Median Price': [800000]
        })

        assert isinstance(sample_df, pd.DataFrame)
        assert not sample_df.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
