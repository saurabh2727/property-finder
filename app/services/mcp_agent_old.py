import streamlit as st
import json
from typing import Dict, Any, List, Optional
from services.openai_service import OpenAIService
import pandas as pd
import re

class MCPAgent:
    """Model Context Protocol Agent for natural language queries"""

    def __init__(self):
        self.openai_service = OpenAIService()
        self.context = {}
        self.conversation_history = []

    def initialize_context(self):
        """Initialize context with comprehensive app state"""
        # Get all available app data
        customer_profile = st.session_state.get('customer_profile', {})
        suburb_data = st.session_state.get('suburb_data')
        recommendations = st.session_state.get('recommendations', [])
        filtered_suburbs = st.session_state.get('filtered_suburbs')
        ml_recommender = st.session_state.get('ml_recommender')

        self.context = {
            'customer_profile': customer_profile,
            'customer_profile_summary': self._get_profile_summary(customer_profile),
            'suburb_data': self._serialize_dataframe(suburb_data),
            'suburb_data_summary': self._get_data_summary(suburb_data),
            'recommendations': recommendations,
            'recommendations_summary': self._get_recommendations_summary(recommendations),
            'filtered_suburbs': self._serialize_dataframe(filtered_suburbs),
            'workflow_step': st.session_state.get('workflow_step', 1),
            'available_features': self._get_available_features(),
            'ml_model_info': self._get_ml_model_info(ml_recommender),
            'app_state': {
                'profile_generated': st.session_state.get('profile_generated', False),
                'data_uploaded': st.session_state.get('data_uploaded', False),
                'ml_trained': bool(ml_recommender),
                'recommendations_available': bool(recommendations),
                'total_suburbs': len(suburb_data) if suburb_data is not None else 0,
                'total_recommendations': len(recommendations) if recommendations else 0
            }
        }

    def _serialize_dataframe(self, df):
        """Serialize dataframe for context"""
        if df is None or df.empty:
            return None

        # Convert to summary statistics and sample data
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'sample_data': df.head(5).to_dict('records') if len(df) > 0 else [],
            'summary_stats': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
        }

    def _get_available_features(self):
        """Get list of available features based on current state"""
        features = ['customer_profiling', 'data_upload', 'suburb_analysis']

        if st.session_state.get('profile_generated'):
            features.append('profile_complete')

        if st.session_state.get('data_uploaded'):
            features.append('data_available')

        if st.session_state.get('ml_recommender'):
            features.append('ml_trained')

        if st.session_state.get('recommendations'):
            features.append('recommendations_generated')

        return features

    def _get_profile_summary(self, profile):
        """Generate customer profile summary"""
        if not profile:
            return "No customer profile available"

        summary = []
        if 'investment_amount' in profile:
            summary.append(f"Investment Budget: ${profile['investment_amount']:,}")
        if 'income' in profile:
            summary.append(f"Annual Income: ${profile['income']:,}")
        if 'investment_goal' in profile:
            summary.append(f"Goal: {profile['investment_goal']}")
        if 'risk_tolerance' in profile:
            summary.append(f"Risk Tolerance: {profile['risk_tolerance']}")
        if 'property_type' in profile:
            summary.append(f"Property Type: {profile['property_type']}")
        if 'location_preference' in profile:
            summary.append(f"Location: {profile['location_preference']}")

        return " | ".join(summary) if summary else "Basic profile information available"

    def _get_data_summary(self, df):
        """Generate data summary for context"""
        if df is None or df.empty:
            return "No market data uploaded"

        summary = f"HtAG Data: {len(df)} suburbs loaded"

        if 'suburb' in df.columns:
            summary += f" | Unique suburbs: {df['suburb'].nunique()}"
        if 'median_price' in df.columns:
            avg_price = df['median_price'].mean()
            summary += f" | Avg median price: ${avg_price:,.0f}"
        if 'rental_yield' in df.columns:
            avg_yield = df['rental_yield'].mean()
            summary += f" | Avg yield: {avg_yield:.2f}%"
        if 'growth_rate' in df.columns:
            avg_growth = df['growth_rate'].mean()
            summary += f" | Avg growth: {avg_growth:.2f}%"

        return summary

    def _get_recommendations_summary(self, recommendations):
        """Generate recommendations summary"""
        if not recommendations:
            return "No recommendations generated yet"

        summary = f"AI Recommendations: {len(recommendations)} suburbs recommended"

        if recommendations and isinstance(recommendations[0], dict):
            if 'total_score' in recommendations[0]:
                top_score = recommendations[0]['total_score']
                summary += f" | Top score: {top_score:.2f}"
            if 'suburb' in recommendations[0]:
                top_suburb = recommendations[0]['suburb']
                summary += f" | Top pick: {top_suburb}"

        return summary

    def _get_ml_model_info(self, ml_recommender):
        """Get ML model information"""
        if not ml_recommender:
            return "No ML model trained"

        try:
            info = {
                'model_type': 'Random Forest Ensemble',
                'features_used': len(ml_recommender.feature_columns) if hasattr(ml_recommender, 'feature_columns') else 'Unknown',
                'training_status': 'Trained and ready',
                'prediction_capability': 'Growth, Yield, Risk scoring'
            }
            return info
        except:
            return "ML model available but details unavailable"

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process natural language query and return response with actions"""

        try:
            self.initialize_context()

            # Create system prompt with context
            system_prompt = self._create_system_prompt()

            # Create user prompt with query and detailed context
            user_prompt = f"""
            User Query: {user_query}

            DETAILED APPLICATION CONTEXT:

            Customer Profile Details:
            {json.dumps(self.context.get('customer_profile', {}), indent=2) if self.context.get('customer_profile') else 'No customer profile available'}

            Current Recommendations:
            {json.dumps(self.context.get('recommendations', [])[:3], indent=2) if self.context.get('recommendations') else 'No recommendations available'}

            Market Data Summary:
            {self.context.get('suburb_data_summary', 'No market data available')}

            Application State:
            - Workflow Step: {self.context.get('workflow_step', 1)}
            - Available Features: {', '.join(self.context.get('available_features', []))}
            - Profile Status: {self.context.get('customer_profile_summary', 'Not created')}
            - Data Status: {self.context.get('suburb_data_summary', 'Not uploaded')}
            - Recommendations Status: {self.context.get('recommendations_summary', 'Not generated')}

            IMPORTANT: Use the specific data provided above to answer the user's question.
            Reference actual suburb names, prices, yields, scores, and profile details when relevant.

            Please analyze the query and provide:
            1. A natural language response using the specific data context
            2. Any specific actions that should be taken in the app
            3. Data insights based on the available information
            4. Navigation suggestions if relevant
            """

            # Get AI response
            response = self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            ai_response = response.choices[0].message.content

            # Parse response and extract actions
            parsed_response = self._parse_ai_response(ai_response, user_query)

            # Update conversation history
            self.conversation_history.append({
                'user_query': user_query,
                'ai_response': parsed_response['response'],
                'actions': parsed_response.get('actions', [])
            })

            return parsed_response

        except Exception as e:
            return {
                'response': f"I apologize, but I encountered an error processing your query: {str(e)}",
                'actions': [],
                'data': None,
                'error': True
            }

    def _create_system_prompt(self) -> str:
        """Create system prompt with comprehensive app context"""

        # Get context summaries
        profile_summary = self.context.get('customer_profile_summary', 'No customer profile available')
        data_summary = self.context.get('suburb_data_summary', 'No market data uploaded')
        recommendations_summary = self.context.get('recommendations_summary', 'No recommendations generated yet')
        ml_model_info = self.context.get('ml_model_info', 'No ML model trained')
        app_state = self.context.get('app_state', {})

        return f"""
        You are an intelligent property investment assistant integrated into a property analysis application.
        You have access to all uploaded data, customer profiles, and analysis results.

        CURRENT DATA CONTEXT:

        CUSTOMER PROFILE:
        {profile_summary}

        MARKET DATA:
        {data_summary}

        AI RECOMMENDATIONS:
        {recommendations_summary}

        ML MODEL STATUS:
        {ml_model_info if isinstance(ml_model_info, str) else f"Model: {ml_model_info.get('model_type', 'Unknown')} | Features: {ml_model_info.get('features_used', 'Unknown')} | Status: {ml_model_info.get('training_status', 'Unknown')}"}

        APPLICATION STATE:
        - Profile Complete: {'Yes' if app_state.get('profile_generated') else 'No'}
        - Data Uploaded: {'Yes' if app_state.get('data_uploaded') else 'No'}
        - ML Model Trained: {'Yes' if app_state.get('ml_trained') else 'No'}
        - Recommendations Available: {'Yes' if app_state.get('recommendations_available') else 'No'}
        - Total Suburbs: {app_state.get('total_suburbs', 0)}
        - Total Recommendations: {app_state.get('total_recommendations', 0)}

        IMPORTANT: You have access to the customer's profile data, uploaded HtAG market data,
        and all generated recommendations. Reference this data directly in your responses.
        Do NOT say you don't have access to this data - you do have it!

        CAPABILITIES:
        You can help users with:
        1. Understanding their property investment profile and goals
        2. Analyzing market data trends and suburb statistics
        3. Interpreting AI-generated recommendations and scores
        4. Providing investment insights based on their specific profile
        5. Explaining risk assessments and growth projections
        6. Filtering and searching through suburb data
        7. Navigating through the application workflow
        8. Generating custom reports and analysis

        AVAILABLE DATA TO REFERENCE:
        - Customer investment budget, income, goals, risk tolerance
        - Suburb median prices, rental yields, growth rates
        - AI recommendation scores and rankings
        - Risk assessments and cash flow projections
        - Feature importance and ML explanations

        RESPONSE FORMAT:
        Structure your responses as JSON with the following format:
        {{
            "response": "Natural language response to the user referencing specific data",
            "actions": [
                {{
                    "type": "action_type",
                    "description": "What this action does",
                    "parameters": {{}}
                }}
            ],
            "data": {{"key": "value"}} or null,
            "suggestions": ["suggestion1", "suggestion2"]
        }}

        ACTION TYPES:
        - "navigate": Navigate to a different page
        - "filter": Apply filters to data
        - "analyze": Perform analysis
        - "display": Display specific information
        - "export": Export data or reports
        - "search": Search through data

        Always be helpful, accurate, and provide actionable insights based on the available data.
        Reference specific data points, suburb names, prices, yields, and scores when relevant.
        """

    def _parse_ai_response(self, ai_response: str, user_query: str) -> Dict[str, Any]:
        """Parse AI response and extract structured information"""

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)

            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)

                # Validate structure
                if 'response' in parsed:
                    return parsed

        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback to text parsing and create structured response
        return self._create_fallback_response(ai_response, user_query)

    def _create_fallback_response(self, ai_response: str, user_query: str) -> Dict[str, Any]:
        """Create fallback structured response"""

        # Analyze query for intent
        query_lower = user_query.lower()
        actions = []
        suggestions = []

        # Navigation intents
        if any(word in query_lower for word in ['profile', 'customer', 'questionnaire']):
            actions.append({
                "type": "navigate",
                "description": "Go to customer profile page",
                "parameters": {"page": "customer_profile"}
            })

        if any(word in query_lower for word in ['data', 'upload', 'import', 'suburbs']):
            actions.append({
                "type": "navigate",
                "description": "Go to data upload page",
                "parameters": {"page": "data_upload"}
            })

        if any(word in query_lower for word in ['recommend', 'suggestions', 'best']):
            if st.session_state.get('recommendations'):
                actions.append({
                    "type": "navigate",
                    "description": "View recommendations",
                    "parameters": {"page": "recommendations"}
                })
            else:
                suggestions.append("Complete customer profiling and data upload first to get recommendations")

        if any(word in query_lower for word in ['report', 'export', 'download']):
            actions.append({
                "type": "navigate",
                "description": "Go to reports page",
                "parameters": {"page": "reports"}
            })

        # Analysis intents
        if any(word in query_lower for word in ['analyze', 'filter', 'search']):
            if st.session_state.get('data_uploaded'):
                actions.append({
                    "type": "navigate",
                    "description": "Go to suburb analysis",
                    "parameters": {"page": "suburb_analysis"}
                })

        return {
            'response': ai_response,
            'actions': actions,
            'data': None,
            'suggestions': suggestions
        }

    def execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute an action in the application"""

        try:
            action_type = action.get('type')
            parameters = action.get('parameters', {})

            if action_type == 'navigate':
                page = parameters.get('page')
                if page and page in ['home', 'customer_profile', 'data_upload', 'suburb_analysis', 'recommendations', 'reports']:
                    st.session_state.current_page = page
                    return True

            elif action_type == 'filter':
                # Apply data filters
                return self._apply_filters(parameters)

            elif action_type == 'search':
                # Perform search
                return self._perform_search(parameters)

            elif action_type == 'analyze':
                # Trigger analysis
                return self._trigger_analysis(parameters)

            return False

        except Exception as e:
            st.error(f"Error executing action: {str(e)}")
            return False

    def _apply_filters(self, parameters: Dict[str, Any]) -> bool:
        """Apply filters to suburb data"""
        # Implementation for applying filters
        return True

    def _perform_search(self, parameters: Dict[str, Any]) -> bool:
        """Perform search on data"""
        # Implementation for search functionality
        return True

    def _trigger_analysis(self, parameters: Dict[str, Any]) -> bool:
        """Trigger analysis operations"""
        # Implementation for analysis triggers
        return True

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

class NaturalLanguageInterface:
    """Natural Language Interface for the property app"""

    def __init__(self):
        self.agent = MCPAgent()

    def render_chat_interface(self):
        """Render the chat interface in Streamlit"""

        st.subheader("🤖 AI Assistant")
        st.caption("Ask me anything about your property analysis!")

        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = [
                {
                    'role': 'assistant',
                    'content': "Hi! I'm your AI property investment assistant. I can help you navigate the app, analyze data, understand recommendations, and answer questions about your property investment journey. What would you like to know?"
                }
            ]

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message['role']):
                st.write(message['content'])

        # Chat input
        if prompt := st.chat_input("Ask me about your property analysis..."):
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': prompt
            })

            with st.chat_message("user"):
                st.write(prompt)

            # Process query with MCP agent
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.agent.process_query(prompt)

                    # Display response
                    st.write(response['response'])

                    # Execute actions if any
                    actions = response.get('actions', [])
                    if actions:
                        st.markdown("**Actions:**")
                        for action in actions:
                            if st.button(f"▶️ {action['description']}", key=f"action_{hash(str(action))}"):
                                success = self.agent.execute_action(action)
                                if success:
                                    st.rerun()

                    # Show suggestions
                    suggestions = response.get('suggestions', [])
                    if suggestions:
                        st.markdown("**Suggestions:**")
                        for suggestion in suggestions:
                            st.info(suggestion)

                    # Store assistant response
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response['response']
                    })

    def render_quick_queries(self):
        """Render quick query buttons"""

        st.markdown("### 🚀 Quick Questions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 What's my best investment option?", use_container_width=True):
                self._handle_quick_query("What's my best investment option based on my profile?")

        with col2:
            if st.button("🎯 How do I improve my recommendations?", use_container_width=True):
                self._handle_quick_query("How can I improve the quality of my property recommendations?")

        with col3:
            if st.button("📈 Explain the market analysis", use_container_width=True):
                self._handle_quick_query("Can you explain the market analysis results?")

        col4, col5, col6 = st.columns(3)

        with col4:
            if st.button("💰 Show me cash flow projections", use_container_width=True):
                self._handle_quick_query("Show me the cash flow projections for recommended properties")

        with col5:
            if st.button("⚠️ What are the investment risks?", use_container_width=True):
                self._handle_quick_query("What are the main investment risks I should be aware of?")

        with col6:
            if st.button("🔍 Help me understand my data", use_container_width=True):
                self._handle_quick_query("Help me understand my suburb data and what it means")

    def _handle_quick_query(self, query: str):
        """Handle quick query button clicks"""
        # Add to chat history and process
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        st.session_state.chat_history.append({
            'role': 'user',
            'content': query
        })

        response = self.agent.process_query(query)

        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response['response']
        })

        st.rerun()

    def render_enhanced_chat_interface(self):
        """Render enhanced chat interface with better design"""

        # Initialize chat history with enhanced welcome message
        if 'chat_history' not in st.session_state:
            # Initialize context to get current data status
            self.agent.initialize_context()
            context = self.agent.context

            # Create dynamic welcome message based on available data
            profile_status = "Available" if context.get('customer_profile') else "Not created"
            data_status = "Available" if context.get('suburb_data') else "Not uploaded"
            recommendations_status = "Available" if context.get('recommendations') else "Not generated"

            welcome_message = f"""Hello! I'm your AI property investment assistant.

**Current Status:**
• Customer Profile: {profile_status}
• Market Data: {data_status}
• AI Recommendations: {recommendations_status}

**How I can help:**
• Analyze your investment profile and goals
• Interpret HtAG market data and trends
• Explain AI recommendation scores and rankings
• Provide cash flow projections and risk analysis
• Search and filter property data
• Generate custom reports

What would you like to know about your property analysis?"""

            st.session_state.chat_history = [
                {
                    'role': 'assistant',
                    'content': welcome_message
                }
            ]

        # Add ChatGPT-like styling
        st.markdown("""
        <style>
        /* Clean ChatGPT-like interface */
        .stApp {
            background-color: #f7f7f8;
        }

        /* Clean header */
        .chat-header {
            background: white;
            padding: 24px;
            border-bottom: 1px solid #e5e5e5;
            margin-bottom: 24px;
            border-radius: 12px;
            text-align: center;
        }

        /* Chat container */
        .main .block-container {
            padding-bottom: 120px;
            max-width: 800px;
            margin: 0 auto;
        }

        /* Message styling */
        .stChatMessage {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Remove emojis from avatars */
        .stChatMessage img {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)

        # Clean header
        st.markdown("""
        <div class="chat-header">
            <h2 style="margin: 0; color: #1f2937; font-weight: 600;">AI Property Assistant</h2>
            <p style="margin: 8px 0 0 0; color: #6b7280;">Get instant answers about your property analysis</p>
        </div>
        """, unsafe_allow_html=True)

        # Display chat history with clean design
        for message in st.session_state.chat_history:
            if message['role'] == 'assistant':
                with st.chat_message("assistant"):
                    st.markdown(message['content'])
            else:
                with st.chat_message("user"):
                    st.markdown(message['content'])

        # Clean chat input
        if prompt := st.chat_input("Ask anything about your property analysis...", key="main_chat_input"):
                # Add user message
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': prompt
                })

            # Process with clean loading
            with st.spinner("Thinking..."):
                response = self.agent.process_query(prompt)

                # Add response
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response['response']
                })

            st.rerun()

    def render_enhanced_quick_queries(self):
        """Render enhanced quick query buttons with better organization"""

        # Context-aware quick queries
        current_step = st.session_state.get('workflow_step', 1)
        has_profile = st.session_state.get('profile_generated', False)
        has_data = st.session_state.get('data_uploaded', False)
        has_recommendations = st.session_state.get('recommendations', False)

        # Beginner queries
        if not has_profile or not has_data:
            st.markdown("#### Getting Started")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("How do I start?", use_container_width=True, key="quick_start"):
                    self._handle_quick_query("How do I get started with the property analysis? What steps should I follow?")

            with col2:
                if st.button("Create profile", use_container_width=True, key="quick_profile"):
                    self._handle_quick_query("Help me create a customer profile and understand what information I need")

        # Analysis queries (when data available)
        if has_data:
            st.markdown("#### Data Analysis")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Market trends", use_container_width=True, key="quick_trends"):
                    self._handle_quick_query("What are the key market trends in my uploaded data?")

            with col2:
                if st.button("Best suburbs", use_container_width=True, key="quick_suburbs"):
                    self._handle_quick_query("Which suburbs look most promising based on my data?")

        # Investment queries (when recommendations available)
        if has_recommendations:
            st.markdown("#### Investment Analysis")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Top pick", use_container_width=True, key="quick_top"):
                    self._handle_quick_query("What's my #1 recommended property and why?")

            with col2:
                if st.button("Risks", use_container_width=True, key="quick_risks"):
                    self._handle_quick_query("What are the main investment risks I should consider?")

            col3, col4 = st.columns(2)

            with col3:
                if st.button("Cash flow", use_container_width=True, key="quick_cashflow"):
                    self._handle_quick_query("Show me cash flow projections for top recommendations")

            with col4:
                if st.button("Strategy", use_container_width=True, key="quick_strategy"):
                    self._handle_quick_query("What investment strategy should I follow based on my profile?")

        # Advanced queries
        st.markdown("#### Advanced")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Explain AI", use_container_width=True, key="quick_explain"):
                self._handle_quick_query("How does the AI recommendation engine work? Explain the scoring methodology")

        with col2:
            if st.button("Generate report", use_container_width=True, key="quick_report"):
                self._handle_quick_query("How can I generate and customize investment reports for my client?")

        # Help section
        st.markdown("---")
        st.markdown("#### Need Help?")

        help_examples = [
            "Try asking: 'Compare yield vs growth strategies'",
            "Try asking: 'Filter suburbs under $800k with 5%+ yield'",
            "Try asking: 'Explain the ML feature importance'",
            "Try asking: 'Show me one-page suburb reports'"
        ]

        for example in help_examples:
            st.caption(example)

# Integration component for sidebar
def render_ai_assistant_sidebar():
    """Render AI assistant in sidebar"""

    with st.sidebar:
        st.markdown("---")
        st.subheader("🤖 AI Assistant")

        # Quick status check
        if st.button("💬 Ask AI Assistant", use_container_width=True):
            # Show/hide chat interface
            st.session_state.show_ai_chat = not st.session_state.get('show_ai_chat', False)

        # Quick insights
        if st.session_state.get('recommendations'):
            st.success("✅ Recommendations ready - Ask me about them!")

        if st.session_state.get('profile_generated') and st.session_state.get('data_uploaded'):
            st.info("💡 Try asking: 'What's my best investment option?'")

        # Quick actions
        st.markdown("**Quick Actions:**")
        if st.button("📊 Analyze Data", key="sidebar_analyze", use_container_width=True):
            nl_interface = NaturalLanguageInterface()
            response = nl_interface.agent.process_query("Analyze my current data and provide insights")
            st.info(response['response'][:200] + "..." if len(response['response']) > 200 else response['response'])

# Main chat page component
def render_chat_page():
    """Render enhanced full chat page"""

    # Apply custom CSS for better chat styling
    st.markdown("""
    <style>
    .chat-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }

    .quick-action-btn {
        background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        border: none;
        margin: 5px;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .quick-action-btn:hover {
        transform: translateY(-2px);
    }

    .stats-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    .chat-input-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
        border: 2px solid #e1e8ed;
    }

    .assistant-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }

    .user-message {
        background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

    nl_interface = NaturalLanguageInterface()
    nl_interface.render_enhanced_chat_interface()

