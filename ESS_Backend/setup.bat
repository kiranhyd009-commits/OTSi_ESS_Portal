@echo off
REM OTSI Attendance Portal - Automated Setup Script
setlocal enabledelayedexpansion

color 0A
echo.
echo ====================================================
echo   OTSI Attendance Portal - Auto Setup
echo ====================================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not added to PATH.
    echo Please install Python 3.8+ from https://python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

REM Navigate to backend directory using script directory
cd /d "%~dp0"
echo Navigated to: %cd%
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment (venv)...
if exist "venv" (
    echo Virtual environment (venv) already exists. Skipping creation...
) else (
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip and install dependencies
echo [4/5] Upgrading pip and installing required Python packages...
python -m pip install --upgrade pip --quiet
pip install --no-cache-dir -r requirements.txt

if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: Failed to install dependencies.
    echo Please check internet connection or run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Create .env if missing
echo [5/5] Checking configuration (.env)...
if exist ".env" (
    echo .env file already exists.
) else (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo Created .env from .env.example template.
    ) else (
        (
            echo FLASK_ENV=development
            echo FLASK_DEBUG=True
            echo FLASK_APP=app.py
            echo JWT_SECRET_KEY=otsi-jwt-secret-key-%RANDOM%-%RANDOM%
            echo SUPABASE_URL=https://your-project.supabase.co
            echo SUPABASE_KEY=your-supabase-api-key
            echo CORS_ORIGINS=http://localhost:5000,http://localhost:3000,http://127.0.0.1:5000
            echo SERVER_PORT=5000
            echo SERVER_HOST=0.0.0.0
        ) > .env
        echo Created default .env template.
    )
    echo NOTE: Please update .env with your Supabase credentials if needed.
)

color 0A
echo.
echo ====================================================
echo   Setup Complete! ✅
echo ====================================================
echo.
echo To start the server now, run:
echo   python app.py
echo or double-click start_server.bat in the root folder.
echo.
