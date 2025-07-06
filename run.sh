#!/bin/bash

# AI Resume Enhancer Startup Script

echo "🚀 Starting AI Resume Enhancer (Free Version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model if needed
echo "📚 Checking spaCy model..."
python -m spacy download en_core_web_sm --quiet

# Check environment variables
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from template..."
    cp config/.env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    exit 1
fi

# Run the application
echo "🌟 Starting Streamlit application..."
streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
