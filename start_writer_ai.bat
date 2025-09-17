@echo off
REM LibreOffice Writer with AI Agent Startup Script for Windows
REM This script starts LibreOffice Writer with UNO listener and launches the Python AI agent

echo Starting LibreOffice Writer with AI Agent...

REM Set environment variables
set OPENAI_API_KEY=%1
if "%OPENAI_API_KEY%"=="" (
    echo Error: Please provide OpenAI API key as first argument
    echo Usage: start_writer_ai.bat YOUR_OPENAI_API_KEY
    pause
    exit /b 1
)

REM Find LibreOffice installation
set LO_PATH=""
if exist "C:\Program Files\LibreOffice\program\soffice.exe" (
    set LO_PATH="C:\Program Files\LibreOffice\program\soffice.exe"
) else if exist "C:\Program Files (x86)\LibreOffice\program\soffice.exe" (
    set LO_PATH="C:\Program Files (x86)\LibreOffice\program\soffice.exe"
) else (
    echo Error: LibreOffice installation not found
    echo Please install LibreOffice or update the path in this script
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python and add it to PATH
    pause
    exit /b 1
)

REM Install required Python packages
echo Installing required Python packages...
python -m pip install openai requests >nul 2>&1

REM Start LibreOffice Writer with UNO listener
echo Starting LibreOffice Writer with UNO bridge...
start "" %LO_PATH% --writer --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" --nologo --nodefault --nolockcheck --norestore

REM Wait a bit for LibreOffice to start
timeout /t 3 /nobreak >nul

REM Start Python AI Agent
echo Starting AI Agent...
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%sw\source\aiagent\ai_agent.py" --api-key %OPENAI_API_KEY% --port 8765

echo AI-enhanced LibreOffice Writer is now running!
echo - LibreOffice Writer is available with UNO bridge on port 2002
echo - AI Agent is running on port 8765
echo - Use the AI Assistant panel in the sidebar to interact with the agent
echo.
echo Press any key to stop the AI Agent...
pause >nul

REM Kill Python processes (AI Agent)
taskkill /f /im python.exe >nul 2>&1

echo AI Agent stopped.