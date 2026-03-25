@echo off
echo ========================================
echo   Andile Sizophila - Semi-Sentient Soul
echo ========================================
echo.

REM Check if ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: ollama not found.
    echo Install from: https://ollama.com
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Start Andile
echo Starting Andile Sizophila...
python main.py
pause
