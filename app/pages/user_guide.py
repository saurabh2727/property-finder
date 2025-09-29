import streamlit as st

def render_user_guide_page():
    """Render a comprehensive user guide for property professionals"""

    st.title("📚 User Guide")
    st.subheader("Complete guide for property professionals")

    # Overview section
    st.markdown("## Platform Overview")

    st.markdown("""
    The Property Investment Analysis Platform is designed specifically for property agents and investment advisors
    to provide data-driven, professional investment recommendations to their clients. The platform combines
    artificial intelligence with comprehensive market data to streamline your analysis workflow and enhance
    client presentations.

    **Key Benefits:**
    - Reduce analysis time from hours to minutes
    - Provide consistent, data-backed recommendations
    - Generate professional client reports automatically
    - Access comprehensive market insights including HtAG data
    - Leverage AI to identify optimal investment opportunities
    """)

    st.markdown("---")

    # Detailed workflow steps
    st.markdown("## Complete Workflow Guide")

    # Step 1
    st.markdown("### Step 1: Customer Profiling")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Create a comprehensive profile of your client's investment goals, financial capacity, and preferences.

        **What You'll Do:**
        - Upload client discovery questionnaires (PDF/Word documents)
        - OR manually enter client information using our guided form
        - Define investment budget and financial constraints
        - Set investment timeline and goals (capital growth vs rental yield)
        - Specify location preferences and property types

        **What the System Does:**
        - Automatically extracts key information from uploaded documents using AI
        - Validates and structures client data for analysis
        - Creates investment criteria profiles
        - Establishes filtering parameters for suburb selection

        **Professional Tip**: The more detailed your client profile, the more targeted and relevant your recommendations will be. Include specific location preferences, risk tolerance, and any special requirements.
        """)

    with col2:
        st.info("""
        **Required Information:**
        - Investment budget range
        - Preferred locations/regions
        - Property type preferences
        - Investment timeline
        - Risk tolerance level
        - Rental yield vs growth priority
        """)

    st.markdown("---")

    # Step 2
    st.markdown("### Step 2: Market Data Import")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Import comprehensive market data to enable accurate suburb analysis and scoring.

        **Data Sources Supported:**
        - **HtAG Data**: Premium suburb performance metrics and forecasts
        - **DSR Data**: Demand to Supply Ratio analysis
        - **Suburb Finder**: Comparative market analysis
        - **Custom CSV/Excel**: Your own market research data
        - **API Integrations**: Real-time market feeds

        **What You'll Do:**
        - Select your preferred data source
        - Upload data files or connect to APIs
        - Map data columns to platform requirements
        - Validate data quality and completeness

        **What the System Does:**
        - Automatically detects file formats and headers
        - Validates data quality and identifies missing information
        - Standardizes suburb names and postcodes
        - Calculates derived metrics (growth rates, yield ratios)
        - Stores data for immediate analysis

        **Data Quality Check**: The system will highlight any missing or inconsistent data and suggest corrections before proceeding to analysis.
        """)

    with col2:
        st.warning("""
        **Data Requirements:**
        - Suburb names and postcodes
        - Median property values
        - Rental yields
        - Historical growth rates
        - Market indicators
        - Population demographics
        """)

    st.markdown("---")

    # Step 3
    st.markdown("### Step 3: Market Analysis & Suburb Scoring")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Automatically analyze suburbs against client criteria and generate investment scores.

        **Analysis Components:**

        **Growth Potential Scoring (35% weight)**
        - Historical capital growth trends
        - Infrastructure development plans
        - Population growth projections
        - Economic indicators and employment growth

        **Rental Yield Analysis (30% weight)**
        - Current gross and net rental yields
        - Rental growth trends
        - Vacancy rates and rental demand
        - Property management costs

        **Risk Assessment (25% weight)**
        - Market volatility measures
        - Economic dependency analysis
        - Natural disaster risk factors
        - Market oversupply indicators

        **Client Fit Scoring (10% weight)**
        - Budget alignment with median prices
        - Location preference matching
        - Property type availability
        - Investment timeline suitability

        **What You'll Do:**
        - Review and adjust scoring weights if needed
        - Set minimum thresholds for each criterion
        - Apply any additional filters (distance, amenities)

        **What the System Does:**
        - Calculates comprehensive scores for each suburb
        - Ranks suburbs based on total weighted scores
        - Identifies top investment opportunities
        - Highlights potential risks and opportunities
        """)

    with col2:
        st.success("""
        **Scoring Metrics:**
        - Overall Investment Score (0-100)
        - Growth Potential Score
        - Rental Yield Score
        - Risk Assessment Score
        - Client Fit Score

        **Output:**
        - Ranked suburb list
        - Detailed scorecards
        - Comparative analysis
        """)

    st.markdown("---")

    # Step 4
    st.markdown("### Step 4: AI-Powered Recommendations")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Generate intelligent, contextual investment recommendations using advanced AI/GenAI analysis.

        **Multi-Engine Recommendation System:**

        **🤖 Primary: AI/GenAI Engine (OpenAI GPT-4)**
        - Natural language processing of customer profiles
        - Contextual analysis of market data and trends
        - Intelligent suburb matching based on client goals
        - Generates personalized investment strategies
        - Provides detailed reasoning for each recommendation

        **📊 Fallback: Rule-Based Engine**
        - Mathematical scoring algorithms
        - Weighted criteria analysis (growth, yield, risk, fit)
        - Automated when AI engine is unavailable
        - Ensures system reliability and consistency

        **🧠 Additional: ML Engine (Optional)**
        - Machine learning models with feature importance
        - SHAP explainability for model interpretability
        - Advanced analytics and insights

        **Recommendation Output:**

        **Primary Recommendations**
        - Top-ranked suburbs based on client criteria
        - Detailed investment rationale and scoring
        - Expected returns and risk assessments
        - Location preferences and budget alignment

        **Export Options:**
        - `ai_genai_recommendations.csv` (when AI used)
        - `rule_based_recommendations.csv` (when fallback used)
        - `ai_analysis.json` (detailed AI insights)

        **What You'll Review:**
        - Engine type used for recommendations
        - AI-generated suburb recommendations and reasoning
        - Investment rationale and supporting data
        - Risk assessments and market timing advice
        - Projected returns and cash flow analysis
        """)

    with col2:
        st.info("""
        **System Features:**
        - Multi-engine architecture
        - Automatic fallback mechanisms
        - Engine transparency
        - Accurate export naming

        **AI/GenAI Considers:**
        - Client investment goals
        - Risk tolerance
        - Budget constraints
        - Preferred locations
        - Market trends
        - Economic indicators

        **Outputs:**
        - Engine-specific filenames
        - Ranked recommendations
        - Investment rationale
        - Risk assessments
        - Return projections
        """)

    st.markdown("---")

    # Step 5
    st.markdown("### Step 5: Agent Review & Validation")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Apply your professional expertise to validate and enhance AI recommendations.

        **Your Professional Review:**

        **Validate Recommendations**
        - Review AI-generated suburb rankings
        - Check recommendations against local market knowledge
        - Verify data accuracy and currency
        - Assess practical considerations (transport, schools, amenities)

        **Add Professional Insights**
        - Include local market intelligence
        - Add knowledge of upcoming developments
        - Consider client-specific factors
        - Note any special considerations or risks

        **Adjust Scoring Weights**
        - Modify scoring criteria based on client feedback
        - Adjust for market conditions or timing
        - Incorporate any new client requirements

        **Quality Assurance**
        - Ensure recommendations align with client goals
        - Verify all supporting data and calculations
        - Check for any obvious issues or oversights

        **What You Can Modify:**
        - Suburb rankings and scores
        - Investment rationale and comments
        - Risk assessments and warnings
        - Recommendation priorities

        **Professional Notes**: Add your own insights, local knowledge, and specific advice that only an experienced property professional would know.
        """)

    with col2:
        st.warning("""
        **Review Checklist:**
        - Data accuracy validation
        - Local market alignment
        - Client goal matching
        - Risk factor assessment
        - Practical considerations
        - Professional insights added
        """)

    st.markdown("---")

    # Step 6
    st.markdown("### Step 6: Professional Report Generation")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Generate comprehensive, professional reports for client presentation and decision-making.

        **Report Components:**

        **Executive Summary**
        - Investment recommendations overview
        - Key findings and opportunities
        - Risk assessment summary
        - Next steps and action items

        **Client Profile Summary**
        - Investment goals and criteria
        - Budget and timeline parameters
        - Risk tolerance and preferences

        **Market Analysis**
        - Suburb ranking and scoring details
        - Comparative market analysis
        - Growth potential assessments
        - Rental yield analysis

        **Investment Recommendations**
        - Top suburb recommendations with detailed rationale
        - Expected returns and cash flow projections
        - Risk factors and mitigation strategies
        - Investment timeline and strategy

        **Supporting Data**
        - Market statistics and trends
        - Property listings and examples
        - Financial projections and scenarios
        - Maps and location analysis

        **Professional Insights**
        - Agent commentary and recommendations
        - Local market knowledge and tips
        - Strategic advice and next steps

        **Report Formats:**
        - PDF presentation for client meetings
        - Excel spreadsheet with detailed data
        - Interactive dashboard for ongoing monitoring
        """)

    with col2:
        st.success("""
        **Report Features:**
        - Professional branding
        - Executive summary
        - Detailed analysis
        - Supporting charts/graphs
        - Action recommendations
        - Contact information

        **Export Options:**
        - PDF for presentations
        - Excel for analysis
        - Interactive dashboard
        """)

    st.markdown("---")

    # AI Assistant section
    st.markdown("### AI Assistant Chat")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Purpose**: Get instant answers about your analysis, explore alternative scenarios, and receive expert guidance.

        **AI Assistant Capabilities:**
        - Access to all your uploaded client data and market analysis
        - Real-time answers about suburb recommendations
        - Alternative scenario exploration
        - Market trend explanations
        - Investment strategy advice

        **How to Use:**
        - Ask specific questions about recommended suburbs
        - Request alternative analysis with different criteria
        - Get explanations of scoring methodology
        - Explore "what-if" scenarios
        - Receive market trend insights

        **Example Questions:**
        - "Why was [suburb] ranked higher than [suburb]?"
        - "What would happen if my client increased their budget to $800k?"
        - "Are there any emerging areas with high growth potential?"
        - "What are the risks of investing in [specific suburb]?"
        - "How do current interest rates affect these recommendations?"
        """)

    with col2:
        st.info("""
        **AI Has Access To:**
        - Your client profiles
        - All imported market data
        - Generated recommendations
        - Scoring methodology
        - Market trends

        **Get Help With:**
        - Analysis questions
        - Alternative scenarios
        - Market insights
        - Strategy advice
        """)

    st.markdown("---")

    # Best practices
    st.markdown("## Best Practices for Property Professionals")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Data Quality Management:**
        - Always validate imported data before analysis
        - Use multiple data sources when possible
        - Keep market data updated regularly
        - Cross-reference AI recommendations with current listings

        **Client Communication:**
        - Present recommendations in context of client goals
        - Explain methodology and data sources clearly
        - Highlight both opportunities and risks transparently
        - Provide clear next steps and action items

        **Professional Development:**
        - Stay updated on platform features and improvements
        - Regularly review and refine your analysis approach
        - Build a library of successful case studies
        - Continuously improve your local market knowledge
        """)

    with col2:
        st.markdown("""
        **Analysis Accuracy:**
        - Always apply local market knowledge to AI recommendations
        - Consider factors not captured in data (noise, traffic, future development)
        - Validate suburb boundaries and postcodes
        - Account for seasonal market variations

        **Risk Management:**
        - Always discuss investment risks with clients
        - Consider multiple scenarios (best case, worst case, most likely)
        - Keep detailed records of analysis and recommendations
        - Regularly review and update investment strategies

        **Competitive Advantage:**
        - Use the platform to provide faster, more comprehensive analysis
        - Combine AI insights with your professional expertise
        - Offer clients data-driven, professional presentations
        - Build reputation for thorough, analytical approach
        """)

    st.markdown("---")

    # Troubleshooting
    st.markdown("## Common Questions & Troubleshooting")

    with st.expander("Data Import Issues"):
        st.markdown("""
        **Problem**: "My CSV file won't upload properly"
        **Solution**: Ensure your CSV file has proper headers and is saved in UTF-8 encoding. Check that suburb names match standard formats.

        **Problem**: "Some suburbs are missing from my analysis"
        **Solution**: Check for spelling variations in suburb names. The system will attempt to match similar names but may need manual correction.

        **Problem**: "HtAG data integration is not working"
        **Solution**: Verify you have the correct HtAG file format. Contact support if you need help with specific data source integration.
        """)

    with st.expander("Analysis & Scoring Questions"):
        st.markdown("""
        **Question**: "Why are the suburb scores different from my expectations?"
        **Answer**: Scoring is based on objective data analysis. Your local knowledge is valuable - use the Agent Review step to adjust scores and add professional insights.

        **Question**: "Can I change the scoring weights for different criteria?"
        **Answer**: Yes, you can adjust weights for growth potential, rental yield, risk factors, and client fit in the analysis settings.

        **Question**: "How current is the market data used in analysis?"
        **Answer**: Data currency depends on your source. HtAG data is typically updated quarterly, while other sources may vary. Always check data dates before presenting to clients.
        """)

    with st.expander("Client Presentation Tips"):
        st.markdown("""
        **Tip**: "Always explain your methodology to clients - it builds confidence in your recommendations"

        **Tip**: "Use the interactive features during client meetings to explore alternative scenarios in real-time"

        **Tip**: "Combine the generated reports with your local market knowledge for the most compelling presentations"

        **Tip**: "Keep clients engaged by explaining both the data insights and your professional interpretation"
        """)

    st.markdown("---")

    # Support section
    st.markdown("## Support & Training")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Getting Help:**
        - Use the AI Assistant for immediate analysis questions
        - Contact support for technical issues
        - Join our professional user community for tips and insights
        - Access video tutorials and webinars

        **Training Resources:**
        - Platform walkthrough videos
        - Best practices webinars
        - Property analysis methodology guides
        - Sample client case studies
        """)

    with col2:
        st.markdown("""
        **Contact Information:**
        - Email: support@propertyinsight.com
        - Training: training@propertyinsight.com
        - Technical Support: Available Monday-Friday 9AM-5PM

        **Additional Resources:**
        - User manual and documentation
        - Video tutorial library
        - Professional development courses
        - Industry insights and market reports
        """)

    # Call to action
    st.markdown("---")

    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center; margin: 2rem 0;">
        <h3 style="color: #1f2937; margin-bottom: 1rem;">Ready to Get Started?</h3>
        <p style="color: #6b7280; margin-bottom: 1.5rem;">
            Begin your first analysis by creating a customer profile, or explore the platform with sample data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Start New Analysis", type="primary", use_container_width=True):
            st.session_state.current_page = 'customer_profile'
            st.rerun()

    with col2:
        if st.button("Import Sample Data", use_container_width=True):
            st.session_state.current_page = 'data_upload'
            st.rerun()

    with col3:
        if st.button("Try AI Assistant", use_container_width=True):
            st.session_state.current_page = 'ai_chat'
            st.rerun()