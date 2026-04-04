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
                "preferred_suburbs": ["list of preferred areas - IMPORTANT: extract ALL suburbs exactly as written, preserving state information if present (e.g., 'Berwick,Victoria', 'Parramatta,NSW'). Do NOT filter suburbs by state or region."],
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

        CRITICAL EXTRACTION RULES:
        1. Extract ALL suburbs mentioned in preferred_suburbs, regardless of state or location
        2. Preserve exact suburb names and any state information (e.g., "Berwick,Victoria")
        3. Do NOT filter or exclude suburbs based on geographic location
        4. If suburb names include state information separated by comma, keep the exact format
        5. Focus on extracting factual information exactly as provided

        If certain information is not available, indicate "not specified" for that field.
        """

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": (
                        "You are an expert property investment advisor. "
                        "Extract structured customer profile information from the document. "
                        "Respond with valid JSON only — no markdown, no commentary."
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            try:
                profile_data = json.loads(content)
                return profile_data
            except json.JSONDecodeError:
                return self._create_fallback_profile(content)

        except Exception as e:
            st.error(f"Error analyzing customer profile: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return self._create_empty_profile()

    def generate_suburb_recommendations(self, customer_profile: Dict[str, Any], suburb_data: Any, num_recommendations: int = 10, approach: str = "Balanced", ml_context: str = "") -> Dict[str, Any]:
        """Generate suburb recommendations based on customer profile and available data, enhanced with ML insights"""

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
        {ml_context}

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
                    {"role": "system", "content": (
                        "You are an expert property investment advisor specializing in suburb analysis. "
                        "You will be given actual suburb data rows in CSV format. "
                        "Only recommend suburbs that appear in the provided data. "
                        "Base your scores and reasons on the actual column values shown. "
                        "Respond with valid JSON only — no markdown, no commentary."
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3500,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            recommendations = json.loads(content)
            return recommendations

        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return self._create_fallback_recommendations()

    def extract_intent_weights(self, query: str, customer_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Use LLM to parse a natural-language intent query and return dimension weights.

        Returns a dict with keys: affordability, schools, crime, transport,
        lifestyle, employment, investment — all values sum to 1.0.
        Falls back to None on any error so caller can use mode weights instead.
        """
        from models.hybrid_recommender import DIMENSIONS
        prompt = f"""
You are a property preference analyst. A user described what matters to them when choosing a suburb.
Convert their intent into importance weights across these 7 dimensions:
{DIMENSIONS}

User intent: "{query}"
Customer profile summary: Primary purpose = {customer_profile.get('investment_goals', {}).get('primary_purpose', 'not specified')}

Return ONLY valid JSON with exactly these keys and float values that sum to 1.0:
{{"affordability": 0.0, "schools": 0.0, "crime": 0.0, "transport": 0.0, "lifestyle": 0.0, "employment": 0.0, "investment": 0.0}}
"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You extract structured preference weights from natural language. Respond with valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"},
            )
            weights = json.loads(response.choices[0].message.content)
            # Normalize to sum to 1
            total = sum(weights.values()) or 1.0
            return {k: v / total for k, v in weights.items() if k in DIMENSIONS}
        except Exception:
            return None

    def generate_suburb_explanations(
        self,
        suburbs_df,
        weights: Dict[str, float],
        customer_profile: Dict[str, Any],
        top_n: int = 5,
    ) -> Dict[str, str]:
        """
        Generate a 2-sentence explanation for why each suburb was recommended.
        Returns dict of {suburb_name: explanation_text}.
        Sends all top_n suburbs in one API call to minimise cost.
        """
        if suburbs_df is None or suburbs_df.empty:
            return {}

        suburb_col = 'Suburb' if 'Suburb' in suburbs_df.columns else suburbs_df.columns[0]
        dim_cols = [c for c in suburbs_df.columns if c.endswith('_dim_score')]

        # Build compact suburb summaries
        rows = []
        for _, row in suburbs_df.head(top_n).iterrows():
            name = row.get(suburb_col, 'Unknown')
            dims = {c.replace('_dim_score', ''): round(float(row[c]), 2) for c in dim_cols if c in row}
            price = row.get('Median Price', 'N/A')
            yld   = row.get('Rental Yield on Houses', 'N/A')
            score = round(float(row.get('final_score', 0)), 3)
            rows.append(f"- {name}: score={score}, price={price}, yield={yld}%, dims={dims}")

        suburb_summaries = "\n".join(rows)
        purpose = customer_profile.get('investment_goals', {}).get('primary_purpose', 'investment')
        top_weights = sorted(weights.items(), key=lambda x: -x[1])[:3]
        top_weight_str = ", ".join(f"{k} ({v:.0%})" for k, v in top_weights if v > 0)

        prompt = f"""
You are a property investment advisor. Explain in exactly 2 sentences why each suburb suits this buyer.

Buyer: {purpose} focus. Top priorities: {top_weight_str}.

Suburbs:
{suburb_summaries}

Return JSON only: {{"suburb_name": "2-sentence explanation", ...}}
Keep each explanation under 40 words. Be specific about the suburb's strengths.
"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You write concise property suburb explanations. Respond with valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {}

    def _summarize_suburb_data(self, suburb_data, max_rows: int = 50) -> str:
        """
        Build a structured suburb data payload for GPT-4.

        Sends actual per-suburb rows (capped at max_rows) so GPT-4 can make
        specific, data-grounded recommendations rather than generic ones.
        Pre-filters to the most investment-relevant columns.
        """
        if suburb_data is None or suburb_data.empty:
            return "No suburb data available."

        try:
            # Columns to include — ordered by relevance
            preferred_cols = [
                "Suburb", "State",
                "Median Price", "Rental Yield on Houses",
                "10 yr Avg. Annual Growth", "Distance (km) to CBD",
                "Population", "Vacancy Rate", "Sales Days on Market",
                # ABS enrichment
                "seifa_irsad_decile", "pop_growth_rate_5yr",
                "median_personal_income_weekly", "owner_occupied_pct",
                "total_approvals_12m",
                # Schools
                "school_quality_score",
                # Domain / sales
                "domain_median_list_price", "domain_median_rental_estimate",
                "nsw_median_sale_price", "vic_median_sale_price",
                "median_rent_weekly_actual",
            ]
            available_cols = [c for c in preferred_cols if c in suburb_data.columns]

            # If none of the preferred cols exist, fall back to all columns
            if not available_cols:
                available_cols = list(suburb_data.columns)

            df = suburb_data[available_cols].copy()

            # Drop rows with no price data
            if "Median Price" in df.columns:
                df = df.dropna(subset=["Median Price"])

            # Cap rows — take top max_rows by ML score if available, else head
            score_col = next((c for c in ["AI_Score", "Overall_Score", "Investment_Score"]
                              if c in df.columns), None)
            if score_col:
                df = df.nlargest(max_rows, score_col)
            else:
                df = df.head(max_rows)

            # Round floats for readability
            df = df.round(2)

            total = len(suburb_data)
            shown = len(df)
            header = (
                f"Dataset: {total} suburbs total. "
                f"Showing top {shown} by relevance.\n"
                f"Columns: {', '.join(available_cols)}\n\n"
            )
            return header + df.to_csv(index=False)

        except Exception as e:
            return f"Suburb data could not be serialised: {e}"

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