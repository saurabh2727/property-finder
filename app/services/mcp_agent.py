import streamlit as st
import json
from openai import OpenAI

class MCPAgent:
    def __init__(self, api_key=None):
        # Use user-provided API key from session state or parameter
        user_api_key = api_key or st.session_state.get('user_openai_api_key')
        if not user_api_key:
            raise ValueError("OpenAI API key not found. Please enter your API key in the sidebar.")
        self.client = OpenAI(api_key=user_api_key)
        self.context = {}
        self.history = []

    def initialize_context(self):
        """Initialize context with comprehensive app state"""
        # Get all available app data
        customer_profile = st.session_state.get('customer_profile', {})
        suburb_data = st.session_state.get('suburb_data')
        recommendations = st.session_state.get('recommendations', [])

        self.context = {
            'customer_profile': customer_profile,
            'suburb_data': self._serialize_dataframe(suburb_data) if suburb_data is not None else None,
            'recommendations': recommendations,
            'app_state': {
                'profile_generated': st.session_state.get('profile_generated', False),
                'data_uploaded': st.session_state.get('data_uploaded', False),
                'ml_trained': bool(st.session_state.get('ml_recommender')),
                'recommendations_available': bool(recommendations),
                'total_suburbs': len(suburb_data) if suburb_data is not None else 0,
                'total_recommendations': len(recommendations) if recommendations else 0
            }
        }

    def _serialize_dataframe(self, df):
        """Convert DataFrame to JSON serializable format"""
        if df is None:
            return None
        return {
            'columns': df.columns.tolist(),
            'data': df.head(50).to_dict('records'),  # Limit to 50 rows for context
            'shape': df.shape
        }

    def process_query(self, query: str) -> dict:
        """Process user query with context"""
        try:
            system_prompt = f"""You are an AI assistant for a property investment analysis platform.

Context:
- Customer Profile: {json.dumps(self.context.get('customer_profile', {}), indent=2)}
- Data Status: {json.dumps(self.context.get('app_state', {}), indent=2)}
- Available Recommendations: {len(self.context.get('recommendations', []))} suburbs

Provide helpful, specific answers about property investment analysis based on the available data.
"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return {
                'response': response.choices[0].message.content,
                'actions': [],
                'suggestions': []
            }

        except Exception as e:
            return {
                'response': f"I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists.",
                'actions': [],
                'suggestions': []
            }

    def clear_history(self):
        """Clear conversation history"""
        self.history = []


class NaturalLanguageInterface:
    def __init__(self):
        # Check for API key before initializing agent
        if not st.session_state.get('user_openai_api_key'):
            self.agent = None
        else:
            self.agent = MCPAgent()

    def render_enhanced_chat_interface(self):
        """Render clean ChatGPT-like interface"""

        # Check if API key is provided
        if not self.agent:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to use the AI Assistant.")
            st.info("Get your API key at: https://platform.openai.com/api-keys")
            return

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

        # Header to match other pages
        st.title("🤖 AI Property Assistant")
        st.subheader("Get instant answers about your property analysis")

        # Initialize chat history with clean welcome message
        if 'chat_history' not in st.session_state:
            self.agent.initialize_context()
            context = self.agent.context

            # Clean status indicators
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

            st.session_state.chat_history = [{
                'role': 'assistant',
                'content': welcome_message
            }]

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


def render_chat_page():
    """Render clean ChatGPT-like chat page"""
    nl_interface = NaturalLanguageInterface()
    nl_interface.render_enhanced_chat_interface()