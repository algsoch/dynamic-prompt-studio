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

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found
    echo Creating template .env file...
    echo # Use your own API keys for full functionality > .env
    echo GEMINI_API_KEY=your_gemini_api_key_here >> .env
    echo YT_API_KEY=your_youtube_api_key_here >> .env
    echo.
    echo Please edit .env with your API keys for full functionality
    echo The app will work in demo mode without API keys
    echo.
)

echo.
echo Starting FastAPI server...
echo Open your browser to: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload