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

### ✅ Latest Updates
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