@echo off
echo Starting Dynamic Prompt Template App...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server...
echo Open your browser to: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload