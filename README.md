# Property Investment Analysis Platform

A comprehensive property investment analysis platform designed for property agents to provide data-driven investment recommendations to their clients. The platform combines AI-powered analysis with market data to streamline the property investment advisory process.

## Key Features

### 🤖 AI-Powered Analysis
- **AI/GenAI Recommendations**: OpenAI GPT-4 powered intelligent suburb recommendations
- **Multi-Engine Architecture**: AI/GenAI primary with rule-based and ML fallbacks
- **Natural Language Processing**: Contextual analysis of customer profiles and market trends
- **Smart Document Processing**: AI-powered extraction from customer documents

### 📊 Advanced Analytics
- **Comprehensive Scoring**: Growth potential, rental yield, risk assessment analysis
- **Interactive Visualizations**: Professional charts and market insights
- **Detailed Investment Insights**: Market overview, performance metrics, risk analysis
- **Configurable Recommendations**: Adjustable suburb count (5-20) based on client needs

### 🔄 Session Management
- **Automatic Data Persistence**: Never lose progress when switching tabs
- **Cross-Tab Navigation**: Seamless workflow with automatic backup/recovery
- **Session Recovery**: Automatic restoration of previous work sessions
- **Progress Tracking**: Visual workflow progress indicators

### 📄 Professional Reporting
- **PDF Report Generation**: Comprehensive client-ready reports with professional formatting
- **Multiple Export Formats**: CSV, JSON, and Excel export options
- **Dynamic File Naming**: Engine-specific export filenames for clarity
- **Interactive Dashboard**: Real-time analytics and suburb comparisons

## Tech Stack

- **Frontend**: Streamlit with custom professional styling
- **AI/ML**: OpenAI GPT-4, Scikit-learn, Custom ML models
- **Data Processing**: Pandas, NumPy with advanced analytics
- **Visualization**: Plotly, Matplotlib, Seaborn for interactive charts
- **PDF Generation**: ReportLab for professional report creation
- **Session Management**: Custom persistence layer with automatic backup

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage Workflow

### Step 1: Customer Profiling
- Upload client discovery documents (PDF/Word) or use manual form
- AI automatically extracts investment criteria and preferences
- Define budget, timeline, and risk tolerance

### Step 2: Data Upload & Integration
- Import market data (HtAG, CSV, Excel formats)
- Automatic data validation and quality checks
- Support for multiple data sources and formats

### Step 3: AI-Powered Analysis
- Configure number of suburb recommendations (5-20)
- AI/GenAI engine provides intelligent contextual analysis
- Fallback to rule-based scoring with customizable weights

### Step 4: Review & Insights
- Access detailed investment insights with interactive charts
- Review AI reasoning and market analysis
- Professional agent review and validation

### Step 5: Report Generation
- Generate comprehensive PDF reports
- Export data in multiple formats
- Client-ready presentations with professional formatting

## Project Structure

```
app/
├── components/     # Reusable UI components with session management
├── pages/         # Application pages with persistence
├── utils/         # Utility functions and session state management
├── models/        # ML models and enhanced scoring engines
├── services/      # OpenAI and external API integrations
├── styles/        # Professional UI styling
└── static/        # Static assets

data/
├── raw/          # Raw data files
├── processed/    # Processed data files
└── sample/       # Sample data for testing

config/           # Configuration files
docs/            # Documentation and user guides
```

## Recent Enhancements

### Latest Updates
- **Session Persistence**: Complete session management with automatic backup/recovery
- **PDF Generation**: Full implementation using ReportLab with professional formatting
- **Enhanced AI Integration**: OpenAI GPT-4 powered recommendation engine
- **Multi-Engine Architecture**: AI/GenAI primary, rule-based fallback, ML optional
- **Improved Analytics**: Detailed investment insights with interactive visualizations
- **User Guide Updates**: Comprehensive documentation of all features
- **Error Recovery**: Robust session recovery and troubleshooting capabilities

## Key Capabilities

- **Multi-Engine Recommendations**: AI/GenAI, Rule-Based, and ML engines
- **Professional PDF Reports**: Client-ready investment analysis documents
- **Session Persistence**: Never lose work when switching between tabs
- **Interactive Analytics**: Real-time charts and market insights
- **Configurable Analysis**: Adjustable recommendation parameters
- **Professional UI**: Modern design optimized for property professionals

## Architecture

The platform uses a multi-engine recommendation system:

1. **Primary Engine**: AI/GenAI (OpenAI GPT-4) for intelligent contextual analysis
2. **Fallback Engine**: Rule-based scoring with weighted criteria
3. **Optional Engine**: Machine Learning models with feature importance analysis

This ensures reliable recommendations with intelligent AI analysis when available, and robust fallback systems for consistent operation.

---

## Required Improvements

The following issues have been identified through code review and need to be addressed before the platform can be considered production-ready.

### Priority 1 — Fix Immediately

#### Security
- **Exposed API key in `.env`**: The OpenAI API key is committed to the repository in plaintext. Revoke the existing key in the OpenAI dashboard immediately, generate a new one, and ensure `.env` is listed in `.gitignore`. Never commit secrets to version control.

#### ML Model — Circular Logic
- **Hand-crafted target variable**: The Random Forest model is trained to predict a composite score that is manually constructed from `rental_yield × 0.30 + growth × 0.25 + vacancy_inverted × 0.20 + ...`. This means the model is learning to reproduce a formula that was already defined — it adds no predictive value over just applying the formula directly.
- **Fix**: Either remove the Random Forest entirely and use the weighted scoring formula directly and transparently, or replace it with a genuine supervised model trained on historical investment outcome data.

#### Silent Data Corruption via Hardcoded Defaults
- **Missing columns filled silently**: When uploaded data lacks key columns (e.g. Population, State, Rental Yield), the app fills them with hardcoded defaults (`Population=15000`, `State=NSW`, `Rental Yield=4.0`) without warning the user. This produces analysis on fabricated data.
- **Fix**: Warn the user clearly when critical columns are missing and require them to either provide the data or explicitly acknowledge the defaults being used.

---

### Priority 2 — Fix Before Real Use

#### GPT-4 Receives Insufficient Data
- **Only summary stats are sent**: GPT-4 receives a text summary of the suburb dataset (price range, yield range, column names) rather than the actual suburb rows. It is recommending suburbs without seeing suburb-level data.
- **Fix**: Send the full suburb dataset (or a structured, row-level representation) to GPT-4 so its recommendations are grounded in real data.

#### Brittle JSON Parsing from GPT-4
- **Regex-based extraction**: GPT-4 responses are parsed using `re.search(r'\{.*\}', content, re.DOTALL)`. This will silently fail or produce incorrect results if GPT-4 wraps the JSON in markdown, adds commentary, or returns nested structures.
- **Fix**: Use OpenAI's structured output / function calling feature to enforce a strict response schema, eliminating fragile string parsing.

#### No Multi-Dataset Support
- **Single file upload only**: The app accepts one file at a time. If a user uploads a second file it replaces the first. There is no mechanism to combine suburb rankings, property history, and demographic data from different sources.
- **Fix**: Add multi-file upload support with a defined join key (`Suburb + State`), dataset type tagging (rankings vs history vs demographics), a merge strategy, and conflict resolution for overlapping columns.

#### Misleading Feature Importance
- **Reflects your own weights, not real signal**: Because the ML target is a manual formula, the feature importances reported will always mirror the weights you hardcoded. Showing this to users as "ML-identified key factors" is misleading.
- **Fix**: Remove feature importance reporting until a genuine supervised model is in place, or clearly label the current output as "configured scoring weights" rather than learned feature importance.

---

### Priority 3 — Fix Before Production

#### Mock Property Data
- **Domain and REA APIs are stubs**: All property listings are generated with `numpy.random`. The `property_finder.py` service has API endpoint URLs defined but never calls them (`mock_data_enabled = True`).
- **Fix**: Integrate real property listing APIs (Domain, REA, or CoreLogic) or clearly document that the platform requires the user to supply their own data export.

#### No Persistent Storage
- **Session state only**: All data lives in `st.session_state` and is lost on page refresh. The `DATABASE_URL` and `REDIS_URL` environment variables are configured but never used.
- **Fix**: Implement a persistence layer (SQLite for development, PostgreSQL for production) to store customer profiles, uploaded datasets, and recommendation results.

#### Debug Output Left in Production Code
- **`st.write()` debug calls**: `openai_service.py` and `document_processor.py` contain `st.write()` statements that print raw document content and stack traces directly into the UI.
- **Fix**: Remove all debug `st.write()` calls and replace with structured logging.

#### UI Logic Inside Service Layer
- **Streamlit imports in business logic**: `ml_recommender.py` and `openai_service.py` import and call Streamlit (`st.error()`, `st.write()`, `st.warning()`) directly. Services should have no knowledge of the UI layer.
- **Fix**: Remove all Streamlit calls from service and model files. Raise exceptions or return error objects that the page layer handles and displays.

#### No Rate Limiting on OpenAI Calls
- **Unbounded API usage**: Every recommendation run makes multiple GPT-4 calls with no throttling, retry backoff, or cost controls.
- **Fix**: Add rate limiting, token usage tracking, and error handling for quota exceeded / rate limit responses.

---

### Priority 4 — Clean Up

#### Duplicate Components
- **Incomplete refactor**: Both `sidebar.py` / `clean_sidebar.py` and `home.py` / `clean_home.py` exist simultaneously. The `clean_` versions appear to be replacements that were never fully migrated.
- **Fix**: Remove the old versions and consolidate to the `clean_` variants.

#### Stale Files
- **`mcp_agent_old.py`**: An old version of the chat agent that is no longer used but still present in the codebase.
- **Fix**: Delete the file.

#### Dead Configuration
- **Unused environment variables**: `DATABASE_URL`, `REDIS_URL`, `GOOGLE_MAPS_API_KEY`, and email settings are defined in `.env.example` and `config.py` but never referenced in the application code.
- **Fix**: Remove unused config keys or implement the features they were intended for.