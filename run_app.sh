#!/bin/bash

# Property Insight App Runner
# This script starts the Streamlit application

echo "🏠 Starting Property Insight App..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "🔧 Please run setup.py first or create .env file manually"
    echo ""
    echo "Creating basic .env file..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Database Configuration
DATABASE_URL=sqlite:///property_insights.db

# Application Settings
APP_DEBUG=False
EOF
    echo "✅ Basic .env file created. Please add your OpenAI API key."
    echo ""
fi

# Install requirements if needed
if [ ! -d "venv" ] && [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    touch requirements_installed.flag
fi

# Create necessary directories
mkdir -p data/{raw,processed}
mkdir -p logs
mkdir -p exports

echo "🚀 Starting Streamlit app..."
echo "📱 App will be available at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Streamlit app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0