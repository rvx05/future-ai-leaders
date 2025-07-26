#!/bin/bash
# Development script to run the Flask app locally

echo "🚀 Starting Study Buddy in development mode..."

# Set environment variables
export FLASK_APP=src/main.py
export FLASK_ENV=development
export DEBUG=True

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Run the Flask app
echo "🌐 Starting Flask server on http://localhost:5000"
cd src && python3 main.py
