@echo off
REM Development script to run the Flask app locally on Windows

echo 🚀 Starting Study Buddy in development mode...

REM Set environment variables
set FLASK_APP=src/main.py
set FLASK_ENV=development
set DEBUG=True

REM Check if .env file exists
if not exist .env (
    echo ⚠️  No .env file found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file and add your GEMINI_API_KEY
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Run the Flask app
echo 🌐 Starting Flask server on http://localhost:5000
cd src && python main.py

pause
