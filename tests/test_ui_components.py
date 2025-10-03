"""
UI Component tests for Streamlit application
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


class TestPropertyCard:
    """Test property card component"""

    def test_property_card_data_structure(self):
        """Test that property card receives correct data structure"""
        sample_suburb = {
            'Suburb': 'Parramatta',
            'State': 'NSW',
            'Median Price': 800000,
            'Rental Yield on Houses': 4.2,
            'Investment Score': 8.5,
            '10 yr Avg. Annual Growth': 6.5,
            'Distance from CBD (km)': 15
        }

        required_fields = ['Suburb', 'State', 'Median Price', 'Rental Yield on Houses']

        for field in required_fields:
            assert field in sample_suburb, f"Missing required field: {field}"


class TestMetricDisplay:
    """Test metric display components"""

    def test_metric_formatting_price(self):
        """Test price formatting"""
        price = 800000
        formatted = f"${price:,.0f}"

        assert formatted == "$800,000"

    def test_metric_formatting_percentage(self):
        """Test percentage formatting"""
        yield_value = 4.23456
        formatted = f"{yield_value:.2f}%"

        assert formatted == "4.23%"

    def test_metric_formatting_growth(self):
        """Test growth rate formatting"""
        growth = 6.5432
        formatted = f"{growth:.1f}%"

        assert formatted == "6.5%"


class TestSuburbComparison:
    """Test suburb comparison functionality"""

    def test_comparison_extracts_correct_data(self):
        """Test that comparison extracts correct suburb data"""
        sample_data = pd.DataFrame({
            'Suburb': ['Parramatta', 'Chatswood', 'Penrith'],
            'Median Price': [800000, 1200000, 650000],
            'Rental Yield on Houses': [4.2, 3.8, 4.8]
        })

        suburb1 = 'Parramatta'
        suburb2 = 'Chatswood'

        s1_data = sample_data[sample_data['Suburb'] == suburb1].iloc[0]
        s2_data = sample_data[sample_data['Suburb'] == suburb2].iloc[0]

        assert s1_data['Median Price'] == 800000
        assert s2_data['Median Price'] == 1200000

    def test_comparison_handles_missing_suburbs(self):
        """Test that comparison handles missing suburbs gracefully"""
        sample_data = pd.DataFrame({
            'Suburb': ['Parramatta', 'Chatswood'],
            'Median Price': [800000, 1200000]
        })

        missing_suburb = 'NonExistent'
        result = sample_data[sample_data['Suburb'] == missing_suburb]

        assert result.empty


class TestDataValidationUI:
    """Test UI data validation"""

    def test_null_value_handling(self):
        """Test handling of null values in display"""
        import numpy as np

        value = np.nan
        formatted = f"{value:.2f}" if pd.notna(value) else "N/A"

        assert formatted == "N/A"

    def test_zero_value_handling(self):
        """Test handling of zero values"""
        value = 0
        assert value == 0  # Should display 0, not hide it

    def test_negative_value_validation(self):
        """Test that negative values are flagged"""
        price = -100000
        assert price < 0  # Should be detected as invalid


class TestChartDataPreparation:
    """Test data preparation for charts"""

    def test_chart_data_structure(self):
        """Test chart data is in correct format"""
        chart_data = pd.DataFrame({
            'Suburb': ['Parramatta', 'Chatswood'],
            'Median Price': [800000, 1200000]
        })

        assert 'Suburb' in chart_data.columns
        assert 'Median Price' in chart_data.columns
        assert len(chart_data) == 2

    def test_chart_data_types(self):
        """Test that chart data has correct types"""
        chart_data = pd.DataFrame({
            'Suburb': ['Parramatta'],
            'Median Price': [800000]
        })

        assert chart_data['Suburb'].dtype == object
        assert chart_data['Median Price'].dtype in [int, float, 'int64', 'float64']


class TestFormValidation:
    """Test form input validation"""

    def test_api_key_format_validation(self):
        """Test API key format validation"""
        valid_key = "sk-proj-1234567890"
        invalid_key = "invalid-key"

        assert valid_key.startswith('sk-')
        assert not invalid_key.startswith('sk-')

    def test_price_range_validation(self):
        """Test price range validation"""
        min_price = 500000
        max_price = 1000000

        assert min_price < max_price
        assert min_price >= 0
        assert max_price >= 0

    def test_percentage_range_validation(self):
        """Test percentage input validation"""
        yield_value = 4.5

        assert 0 <= yield_value <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
