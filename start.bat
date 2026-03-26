@echo off
setlocal

echo ========================================
echo   Andile Sizophila - Semi-Sentient Soul
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: ollama not found.
    echo Install from: https://ollama.com
    pause
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: npm not found. Gemini CLI may not work.
    echo Install Node.js from: https://nodejs.org
    echo.
)

REM Install gemini-cli if not present - using correct @google scope
echo Checking gemini-cli...
call npm list -g @google/gemini-cli >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing @google/gemini-cli...
    echo This may take a minute on first install...
    call npm install -g @google/gemini-cli --legacy-peer-deps
    if %ERRORLEVEL% neq 0 (
        echo WARNING: npm install failed. Trying npx fallback...
        echo Will attempt to run via npx when needed.
    ) else (
        echo @google/gemini-cli installed successfully.
    )
) else (
    echo @google/gemini-cli already installed.
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>nul
echo.

REM Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Starting Ollama server...
    start /b ollama serve
    timeout /t 8 /nobreak >nul
)

REM Start Andile using daemon_runner or main.py
echo Starting Andile Sizophila...
echo.

if "%1"=="daemon" (
    echo Running in daemon mode for %2 hours...
    python daemon_runner.py %2
) else (
    REM Interactive mode - run main.py
    python main.py
)

pause
