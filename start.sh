#!/bin/bash

# Email Verification System Startup Script

echo "Email Verification System"
echo "=========================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo ""
    echo "Flask not found. Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ Flask is installed"

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo "Creating uploads directory..."
    mkdir -p uploads
    echo "✓ Uploads directory created"
fi

echo ""
echo "Starting server..."
echo "===================="
echo ""
echo "Web UI: http://localhost:5000"
echo "API: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python3 app.py
