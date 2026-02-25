@echo off
REM Sales Analytics Chatbot - Start Script
REM This script starts both backend and frontend servers

echo ========================================
echo  Starting Sales Analytics Chatbot
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if database exists
if not exist "sales_analytics.db" (
    echo Database not found. Creating and seeding...
    .venv\Scripts\python init_db_simple.py
    echo.
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Frontend dependencies not found. Installing...
    cd frontend
    call npm install
    cd ..
    echo.
)

echo [1/2] Starting Backend Server (Port 8000)...
start "Sales Analytics Backend" cmd /k ".venv\Scripts\python run_simple_server.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server (Port 5173)...
start "Sales Analytics Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo  SERVERS STARTED!
echo ========================================
echo.
echo  Backend:  http://localhost:8000/health
echo  Frontend: http://localhost:5173
echo.
echo  Press any key to open frontend in browser...
pause >nul

start http://localhost:5173

echo.
echo To stop servers: Close the Backend and Frontend windows
echo.
pause
