#!/bin/bash

# Alfred Startup Script
# This script sets up and runs the Alfred AI Assistant

echo "🤖 Starting Alfred AI Assistant..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd backend && ./start.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    cd ..
    python -m venv .venv
    cd backend
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚠️  No .env file found. Creating from .env.example..."
        cp .env.example .env
        echo "❗ Please edit .env file and add your GOOGLE_API_KEY before continuing"
        echo "   Get your API key from: https://makersuite.google.com/app/apikey"
        exit 1
    else
        echo "❌ No .env or .env.example file found"
        exit 1
    fi
fi

# Start the application
echo "🚀 Starting Alfred..."
echo "   Local access: http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload