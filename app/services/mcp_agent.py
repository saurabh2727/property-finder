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
            # Refresh context before each query to get latest data
            self.initialize_context()

            customer_profile = self.context.get('customer_profile', {})
            app_state = self.context.get('app_state', {})

            # Build detailed context string
            context_info = []
            if customer_profile:
                context_info.append(f"Client Profile: Available with {len(customer_profile)} sections")
                context_info.append(f"Profile Details: {json.dumps(customer_profile, indent=2)}")
            else:
                context_info.append("Client Profile: Not yet created")

            context_info.append(f"Data Status: {json.dumps(app_state, indent=2)}")

            system_prompt = f"""You are an AI assistant for a property agent analysis platform.

Current Session Data:
{chr(10).join(context_info)}

Your role is to help property agents analyze data and assist their clients with property decisions.
If client profile or data is available, use it to provide specific, personalized answers.
If data is missing, guide the user to complete the necessary steps.
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
            profile_status = "✓ Available" if context.get('customer_profile') else "Not created"
            data_status = "✓ Available" if context.get('suburb_data') else "Not uploaded"
            recommendations_status = "✓ Available" if context.get('recommendations') else "Not generated"

            welcome_message = f"""As an AI assistant for a property agent analysis platform, I can assist you in a number of ways:

1. **Property Analysis:** I can provide comprehensive data analysis on properties, including price trends, historical data, rental yield, etc., to help you make informed decisions.

2. **Recommendations:** Based on your client's profile and preferences, I can recommend potential suburbs or specific properties. Currently, we don't have any available recommendations because your client's profile and data status are not provided.

3. **Market Trends:** I can keep you updated with the latest market trends and news, which could influence your strategies.

4. **Risk Assessment:** I can help you assess the potential risks associated with different properties or areas, and suggest ways to mitigate them.

5. **Portfolio Management:** I can assist you in managing your client's property portfolio, tracking their properties, and optimizing returns.

Please provide more specific information about your client's preferences, financial situation, and property goals, so I can provide more personalized assistance.

**Current Session Data:**
• Client Profile: {profile_status}
• Market Data: {data_status}
• Recommendations: {recommendations_status}"""

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
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': prompt
            })

            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)

            # Process with clean loading and show response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.agent.process_query(prompt)

                    # Add response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response['response']
                    })

                    # Display response
                    st.markdown(response['response'])


def render_chat_page():
    """Render clean ChatGPT-like chat page"""
    nl_interface = NaturalLanguageInterface()
    nl_interface.render_enhanced_chat_interface()