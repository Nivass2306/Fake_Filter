@echo off
REM Enhanced FakeFilter Setup Script for Windows

echo.
echo ===================================
echo  FakeFilter - Enhanced Setup
echo ===================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Training enhanced model...
echo This may take 2-3 minutes on first run
python train_model_enhanced.py
if errorlevel 1 (
    echo ERROR: Failed to train model
    echo Continuing with fallback...
)

echo.
echo [3/4] Setup complete!
echo.
echo ===================================
echo  Starting FakeFilter App
echo ===================================
echo.
echo The app will open automatically in your browser.
echo Application: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the enhanced app
python app_enhanced.py

pause
