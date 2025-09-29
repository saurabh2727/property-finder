import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///property_insights.db")

# Application Settings
APP_TITLE = "Property Insight App"
APP_DESCRIPTION = "Residential Property Insight Application for Buyer's Property Agents"

# File Upload Settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {
    "documents": [".docx", ".pdf", ".txt"],
    "data": [".csv", ".xlsx", ".xls"],
    "images": [".png", ".jpg", ".jpeg"]
}

# ML Model Settings
MODEL_RANDOM_STATE = 42
TEST_SIZE = 0.2
CROSS_VALIDATION_FOLDS = 5

# Property Analysis Settings
DEFAULT_INVESTMENT_HORIZON = 10  # years
DEFAULT_RENTAL_YIELD_THRESHOLD = 4.0  # percentage
DEFAULT_GROWTH_RATE_THRESHOLD = 5.0  # percentage per annum

# Suburb Filtering Weights (default)
DEFAULT_WEIGHTS = {
    "rental_yield": 0.25,
    "growth_potential": 0.25,
    "vacancy_rate": 0.15,
    "proximity_to_cbd": 0.10,
    "school_quality": 0.10,
    "crime_rate": 0.10,
    "infrastructure": 0.05
}

# Performance Metrics
PERFORMANCE_METRICS = [
    "rental_yield",
    "capital_growth",
    "vacancy_rate",
    "days_on_market",
    "price_to_income_ratio"
]