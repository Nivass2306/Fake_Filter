#!/bin/bash
# Enhanced FakeFilter Setup Script for Linux/Mac

echo ""
echo "==================================="
echo " FakeFilter - Enhanced Setup"
echo "==================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from python.org"
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/4] Training enhanced model..."
echo "This may take 2-3 minutes on first run"
python3 train_model_enhanced.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to train model"
    echo "Continuing with fallback..."
fi

echo ""
echo "[3/4] Setup complete!"
echo ""
echo "==================================="
echo " Starting FakeFilter App"
echo "==================================="
echo ""
echo "The app will open automatically in your browser."
echo "Application: http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the enhanced app
python3 app_enhanced.py
