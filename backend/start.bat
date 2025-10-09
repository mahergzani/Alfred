@echo off
REM Alfred Startup Script for Windows
REM This script sets up and runs the Alfred AI Assistant

echo 🤖 Starting Alfred AI Assistant...
echo ==================================

REM Check if we're in the right directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the backend directory
    echo    cd backend ^&^& start.bat
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "../.venv" (
    echo ⚠️  Virtual environment not found. Creating one...
    cd ..
    python -m venv .venv
    cd backend
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call ..\.venv\Scripts\activate.bat

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo ⚠️  No .env file found. Creating from .env.example...
        copy .env.example .env
        echo ❗ Please edit .env file and add your GOOGLE_API_KEY before continuing
        echo    Get your API key from: https://makersuite.google.com/app/apikey
        pause
        exit /b 1
    ) else (
        echo ❌ No .env or .env.example file found
        pause
        exit /b 1
    )
)

REM Start the application
echo 🚀 Starting Alfred...
echo    Local access: http://localhost:8000
echo    API docs: http://localhost:8000/docs
echo    Press Ctrl+C to stop
echo.

uvicorn main:app --reload