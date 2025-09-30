import openai
import streamlit as st
from typing import Dict, Any, Optional
import json
import re
from pathlib import Path
import sys

# Add config to path
config_path = Path(__file__).parent.parent.parent / "config"
sys.path.append(str(config_path))

from config import OPENAI_API_KEY, OPENAI_MODEL

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        # Priority: user-provided key > session state > environment variable
        self.api_key = api_key or st.session_state.get('user_openai_api_key') or OPENAI_API_KEY

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please enter your API key in the sidebar.")

        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)

    def analyze_customer_profile(self, document_content: str) -> Dict[str, Any]:
        """Analyze customer profile document and extract structured information"""

        # Debug logging
        st.write("🔍 **Debug Info:**")
        st.write(f"Document content length: {len(document_content)} characters")

        if len(document_content) < 50:
            st.error("⚠️ Document content is too short. Content extracted:")
            st.code(document_content)
            return self._create_empty_profile()

        st.write(f"First 200 characters: {document_content[:200]}...")

        prompt = f"""
        Analyze the following customer discovery questionnaire and extract structured information.
        Please provide a comprehensive customer profile in JSON format with the following structure:

        {{
            "financial_profile": {{
                "annual_income": "estimated amount or range",
                "available_equity": "amount available for withdrawal",
                "loan_capacity": "estimated borrowing capacity",
                "current_debt": "existing financial commitments",
                "cash_available": "liquid funds available"
            }},
            "investment_goals": {{
                "primary_purpose": "investment purpose (capital growth/rental income/both)",
                "investment_timeline": "short/medium/long term",
                "target_yield": "desired rental yield percentage",
                "growth_expectation": "expected capital growth rate",
                "risk_tolerance": "low/medium/high"
            }},
            "property_preferences": {{
                "preferred_suburbs": ["list of preferred areas"],
                "property_types": ["house/unit/townhouse/etc"],
                "bedroom_range": "number of bedrooms preferred",
                "price_range": {{
                    "min": "minimum budget",
                    "max": "maximum budget"
                }},
                "special_features": ["specific requirements or features"]
            }},
            "lifestyle_factors": {{
                "proximity_to_cbd": "importance level (high/medium/low)",
                "school_quality": "importance level",
                "transport_access": "importance level",
                "shopping_amenities": "importance level",
                "future_development": "preference for established vs developing areas"
            }},
            "experience_level": "first-time investor/experienced/portfolio builder",
            "buying_readiness": "ready to buy/researching/planning",
            "additional_notes": "any other relevant information or special circumstances"
        }}

        Customer Document Content:
        {document_content}

        Please analyze the content and provide the structured profile. If certain information is not available,
        indicate "not specified" for that field. Focus on extracting factual information and making reasonable
        inferences where appropriate.
        """

        try:
            st.write("🤖 Calling OpenAI API...")
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert property investment advisor who specializes in analyzing customer profiles and investment requirements. Provide detailed, structured analysis in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            # Extract JSON from response
            content = response.choices[0].message.content
            st.write("✅ Got response from OpenAI")
            st.write(f"Response length: {len(content)} characters")

            # Show the raw response for debugging
            with st.expander("🔍 Raw AI Response (Debug)"):
                st.code(content)

            json_match = re.search(r'\{.*\}', content, re.DOTALL)

            if json_match:
                json_str = json_match.group()
                st.write("✅ Found JSON in response")
                try:
                    profile_data = json.loads(json_str)
                    st.write("✅ Successfully parsed JSON")
                    st.success("🎉 Profile analysis completed successfully!")
                    return profile_data
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON parsing failed: {str(e)}")
                    st.code(json_str)
                    return self._create_fallback_profile(content)
            else:
                st.error("❌ No JSON found in AI response")
                return self._create_fallback_profile(content)

        except Exception as e:
            st.error(f"❌ Error analyzing customer profile: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return self._create_empty_profile()

    def generate_suburb_recommendations(self, customer_profile: Dict[str, Any], suburb_data: Any, num_recommendations: int = 10, approach: str = "Balanced") -> Dict[str, Any]:
        """Generate suburb recommendations based on customer profile and available data"""

        # Convert suburb data to string representation for analysis
        suburb_summary = self._summarize_suburb_data(suburb_data)

        approach_guidance = {
            "Balanced": "Equal weight to yield and growth potential. Best for diversified investors seeking stable returns with moderate growth.",
            "Growth Focused": "Prioritize capital growth opportunities. Suitable for long-term investors willing to accept lower initial yields for higher appreciation.",
            "Yield Focused": "Emphasize high rental returns. Ideal for investors seeking immediate cash flow and steady income streams.",
            "Conservative": "Lower risk, stable investment options. Perfect for risk-averse investors prioritizing capital preservation."
        }

        prompt = f"""
        You are an expert property investment advisor. Based on the customer profile and available suburb data, provide intelligent recommendations.

        INVESTMENT APPROACH: {approach}
        GUIDANCE: {approach_guidance.get(approach, "")}
        NUMBER OF RECOMMENDATIONS REQUIRED: {num_recommendations}

        Customer Profile:
        {json.dumps(customer_profile, indent=2)}

        Available Suburb Data Summary:
        {suburb_summary}

        Please provide exactly {num_recommendations} recommendations in the following JSON format, ranked by suitability score:
        {{
            "recommended_suburbs": [
                {{
                    "suburb_name": "name",
                    "score": "0-100 matching score",
                    "reasons": ["reason 1", "reason 2", "reason 3"],
                    "investment_potential": "high/medium/low",
                    "key_metrics": {{
                        "median_price": "price range",
                        "rental_yield": "estimated yield",
                        "growth_potential": "growth rating"
                    }}
                }}
            ],
            "filtering_criteria": {{
                "price_range": "applied price filter",
                "yield_threshold": "minimum yield considered",
                "growth_requirement": "growth criteria used"
            }},
            "investment_strategy": "recommended approach based on customer goals",
            "risk_assessment": "overall risk profile of recommendations",
            "next_steps": ["recommended actions for the customer"]
        }}

        Focus on matching suburbs to the customer's specific requirements, financial capacity, and investment goals.
        """

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert property investment advisor specializing in suburb analysis and investment recommendations. Provide data-driven, practical advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2500
            )

            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)

            if json_match:
                json_str = json_match.group()
                recommendations = json.loads(json_str)
                return recommendations
            else:
                return self._create_fallback_recommendations()

        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return self._create_fallback_recommendations()

    def _summarize_suburb_data(self, suburb_data) -> str:
        """Create a summary of suburb data for AI analysis"""
        if suburb_data is None:
            return "No suburb data available"

        try:
            # Basic summary of the data structure
            summary = f"Dataset contains {len(suburb_data)} suburbs with the following metrics:\n"
            if len(suburb_data) > 0:
                columns = list(suburb_data.columns)
                summary += f"Available data fields: {', '.join(columns[:20])}\n"

                # Sample statistics if available
                if 'Median Price' in columns:
                    summary += f"Price range: ${suburb_data['Median Price'].min():,.0f} - ${suburb_data['Median Price'].max():,.0f}\n"
                if 'Rental Yield on Houses' in columns:
                    summary += f"Rental yields: {suburb_data['Rental Yield on Houses'].min():.1f}% - {suburb_data['Rental Yield on Houses'].max():.1f}%\n"

            return summary
        except Exception:
            return "Suburb data structure could not be analyzed"

    def _create_fallback_profile(self, content: str) -> Dict[str, Any]:
        """Create a basic profile structure when JSON parsing fails"""
        return {
            "financial_profile": {
                "annual_income": "not specified",
                "available_equity": "not specified",
                "loan_capacity": "not specified",
                "current_debt": "not specified",
                "cash_available": "not specified"
            },
            "investment_goals": {
                "primary_purpose": "not specified",
                "investment_timeline": "not specified",
                "target_yield": "not specified",
                "growth_expectation": "not specified",
                "risk_tolerance": "medium"
            },
            "property_preferences": {
                "preferred_suburbs": [],
                "property_types": ["house"],
                "bedroom_range": "3-4",
                "price_range": {"min": "not specified", "max": "not specified"},
                "special_features": []
            },
            "lifestyle_factors": {
                "proximity_to_cbd": "medium",
                "school_quality": "medium",
                "transport_access": "medium",
                "shopping_amenities": "medium",
                "future_development": "not specified"
            },
            "experience_level": "not specified",
            "buying_readiness": "researching",
            "additional_notes": f"AI analysis partial. Raw content: {content[:500]}..."
        }

    def _create_empty_profile(self) -> Dict[str, Any]:
        """Create an empty profile structure"""
        return {
            "financial_profile": {
                "annual_income": "not specified",
                "available_equity": "not specified",
                "loan_capacity": "not specified",
                "current_debt": "not specified",
                "cash_available": "not specified"
            },
            "investment_goals": {
                "primary_purpose": "not specified",
                "investment_timeline": "not specified",
                "target_yield": "not specified",
                "growth_expectation": "not specified",
                "risk_tolerance": "medium"
            },
            "property_preferences": {
                "preferred_suburbs": [],
                "property_types": [],
                "bedroom_range": "not specified",
                "price_range": {"min": "not specified", "max": "not specified"},
                "special_features": []
            },
            "lifestyle_factors": {
                "proximity_to_cbd": "medium",
                "school_quality": "medium",
                "transport_access": "medium",
                "shopping_amenities": "medium",
                "future_development": "not specified"
            },
            "experience_level": "not specified",
            "buying_readiness": "researching",
            "additional_notes": "Profile analysis failed"
        }

    def _create_fallback_recommendations(self) -> Dict[str, Any]:
        """Create fallback recommendations when AI analysis fails"""
        return {
            "recommended_suburbs": [
                {
                    "suburb_name": "Analysis Required",
                    "score": "N/A",
                    "reasons": ["Insufficient data for analysis"],
                    "investment_potential": "unknown",
                    "key_metrics": {
                        "median_price": "N/A",
                        "rental_yield": "N/A",
                        "growth_potential": "N/A"
                    }
                }
            ],
            "filtering_criteria": {
                "price_range": "not applied",
                "yield_threshold": "not applied",
                "growth_requirement": "not applied"
            },
            "investment_strategy": "Please upload customer profile and suburb data for analysis",
            "risk_assessment": "Cannot assess without proper data",
            "next_steps": ["Upload customer requirements", "Import suburb data", "Configure analysis parameters"]
        }