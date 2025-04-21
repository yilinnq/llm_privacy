#!/bin/bash

# Check python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but it's not installed. Please install Python 3 and try again."
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create virtual env
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo "Could not find the activation script for the virtual environment."
        exit 1
    fi
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo "Could not find the activation script for the virtual environment."
        exit 1
    fi
fi

# Check .env
if [ ! -f ".env" ]; then
    echo "No .env file found. Creating one..."
    echo "GEMINI_API_KEY=" > .env
    echo "Please add your Gemini API key to the .env file."
    exit 1
fi

export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Run app
echo "Starting the Privacy Policy Analysis Tool..."
cd "$PROJECT_DIR" && streamlit run app.py
