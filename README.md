# Property Insight App

A comprehensive residential property insight application for buyer's property agents to automate property research and customer profiling.

## Features

- **Customer Profiling**: AI-powered analysis of customer requirements from uploaded documents
- **Data Integration**: Support for multiple property data sources (H-Tag, DSR, Suburb Finder, etc.)
- **ML Recommendations**: Machine learning-based property recommendations
- **Automated Filtering**: Rule-based and weightage-based suburb filtering
- **Cash Flow Analysis**: Expected cash flow calculations for shortlisted properties
- **Natural Language Queries**: MCP integration for conversational interactions

## Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT, Scikit-learn
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Database**: SQLite with SQLAlchemy

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

## Usage

1. Upload customer profiling document
2. Import or upload suburb data
3. Configure filtering criteria
4. Review AI-generated recommendations
5. Generate detailed reports

## Project Structure

```
app/
├── components/     # Reusable UI components
├── pages/         # Application pages
├── utils/         # Utility functions
├── models/        # ML models and data models
├── services/      # External API integrations
└── static/        # Static assets

data/
├── raw/          # Raw data files
└── processed/    # Processed data files

config/           # Configuration files
tests/           # Test files
```