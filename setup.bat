@echo off
REM Quick setup script for Windows

echo ========================================
echo Sales Analytics Chatbot - Setup
echo ========================================

echo.
echo [1] Creating Python virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)

echo [2] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo [4] Checking .env file...
if not exist .env (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo IMPORTANT: Edit .env with your AWS and RDS credentials
)

echo [5] Initializing database...
python init_db.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env with your AWS and RDS credentials
echo   2. Start backend: uvicorn app.main:app --reload
echo   3. In another terminal, start frontend:
echo      cd frontend
echo      npm install
echo      npm run dev
echo.
echo Open http://localhost:5173 in your browser
echo ========================================
