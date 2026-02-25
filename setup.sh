#!/bin/bash
# Quick setup script for macOS/Linux

echo "========================================"
echo "Sales Analytics Chatbot - Setup"
echo "========================================"

echo ""
echo "[1] Creating Python virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2] Activating virtual environment..."
source .venv/bin/activate

echo "[3] Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4] Checking .env file..."
if [ ! -f .env ]; then
    echo "WARNING: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "IMPORTANT: Edit .env with your AWS and RDS credentials"
fi

echo "[5] Initializing database..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to initialize database"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your AWS and RDS credentials"
echo "  2. Start backend: uvicorn app.main:app --reload"
echo "  3. In another terminal, start frontend:"
echo "     cd frontend"
echo "     npm install"
echo "     npm run dev"
echo ""
echo "Open http://localhost:5173 in your browser"
echo "========================================"
