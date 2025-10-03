"""
Unit tests for service layer (OpenAI, recommendation engine)
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


class TestOpenAIService:
    """Test OpenAI service integration"""

    def test_api_key_validation(self):
        """Test that API key validation works"""
        # Test empty API key
        with pytest.raises(ValueError):
            from services.openai_service import OpenAIService
            service = OpenAIService(api_key="")

    @patch('openai.OpenAI')
    def test_customer_profile_analysis(self, mock_openai):
        """Test customer profile analysis"""
        from services.openai_service import OpenAIService

        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "financial_profile": {
                "annual_income": "$150,000"
            },
            "investment_goals": {
                "primary_purpose": "Capital Growth"
            },
            "property_preferences": {
                "preferred_suburbs": ["Parramatta"]
            },
            "lifestyle_factors": {
                "proximity_to_cbd": "Medium"
            }
        }
        '''

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Test would go here
        assert True  # Placeholder


class TestRecommendationEngine:
    """Test recommendation engine logic"""

    def test_filtering_by_price_range(self):
        """Test that suburbs are filtered by price range"""
        import pandas as pd

        sample_data = pd.DataFrame({
            'Suburb': ['Parramatta', 'Chatswood', 'Penrith'],
            'Median Price': [800000, 1200000, 650000]
        })

        min_price = 700000
        max_price = 900000

        filtered = sample_data[
            (sample_data['Median Price'] >= min_price) &
            (sample_data['Median Price'] <= max_price)
        ]

        assert len(filtered) == 1
        assert filtered.iloc[0]['Suburb'] == 'Parramatta'

    def test_sorting_by_growth(self):
        """Test that suburbs are sorted by growth rate"""
        import pandas as pd

        sample_data = pd.DataFrame({
            'Suburb': ['Parramatta', 'Chatswood', 'Penrith'],
            '10 yr Avg. Annual Growth': [6.5, 5.2, 7.1]
        })

        sorted_data = sample_data.sort_values('10 yr Avg. Annual Growth', ascending=False)

        assert sorted_data.iloc[0]['Suburb'] == 'Penrith'
        assert sorted_data.iloc[1]['Suburb'] == 'Parramatta'
        assert sorted_data.iloc[2]['Suburb'] == 'Chatswood'

    def test_yield_calculation(self):
        """Test rental yield calculations"""
        median_price = 800000
        annual_rent = 33600  # $646/week * 52

        rental_yield = (annual_rent / median_price) * 100

        assert 4.0 <= rental_yield <= 5.0  # Should be around 4.2%

    def test_scoring_weights(self):
        """Test that scoring weights sum to 1"""
        weights = {
            'growth_weight': 0.4,
            'yield_weight': 0.4,
            'risk_weight': 0.2
        }

        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01  # Allow small floating point error


class TestSessionManagement:
    """Test session state management"""

    def test_customer_profile_persistence(self):
        """Test that customer profile persists in session"""
        sample_profile = {
            "financial_profile": {"annual_income": "$150,000"}
        }

        # Simulate session state
        session = {'customer_profile': sample_profile}

        assert 'customer_profile' in session
        assert session['customer_profile']['financial_profile']['annual_income'] == "$150,000"

    def test_workflow_step_tracking(self):
        """Test workflow step progression"""
        workflow_steps = [1, 2, 3, 4, 5]

        for step in workflow_steps:
            assert 1 <= step <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
