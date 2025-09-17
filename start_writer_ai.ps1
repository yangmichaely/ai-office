# LibreOffice Writer with AI Agent Startup Script for Windows PowerShell
# This script starts LibreOffice Writer with UNO listener and launches the Python AI agent

param(
    [Parameter(Mandatory=$true, HelpMessage="OpenAI API Key")]
    [string]$ApiKey
)

Write-Host "Starting LibreOffice Writer with AI Agent..." -ForegroundColor Green

# Find LibreOffice installation
$LO_PATH = $null
$PossiblePaths = @(
    "C:\Program Files\LibreOffice\program\soffice.exe",
    "C:\Program Files (x86)\LibreOffice\program\soffice.exe"
)

foreach ($path in $PossiblePaths) {
    if (Test-Path $path) {
        $LO_PATH = $path
        break
    }
}

if (-not $LO_PATH) {
    Write-Error "LibreOffice installation not found. Please install LibreOffice."
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Error "Python not found. Please install Python and add it to PATH."
    exit 1
}

# Install required Python packages
Write-Host "Installing required Python packages..." -ForegroundColor Yellow
try {
    python -m pip install openai requests 2>$null
    Write-Host "Python packages installed successfully" -ForegroundColor Gray
} catch {
    Write-Warning "Failed to install some Python packages. Continuing anyway..."
}

# Start LibreOffice Writer with UNO listener
Write-Host "Starting LibreOffice Writer with UNO bridge..." -ForegroundColor Yellow
$LO_Process = Start-Process -FilePath $LO_PATH -ArgumentList "--writer", "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager", "--nologo", "--nodefault", "--nolockcheck", "--norestore" -PassThru

# Wait a bit for LibreOffice to start
Start-Sleep -Seconds 3

# Start Python AI Agent
Write-Host "Starting AI Agent..." -ForegroundColor Yellow
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AIAgentScript = Join-Path $ScriptDir "sw\source\aiagent\ai_agent.py"

if (Test-Path $AIAgentScript) {
    $AI_Process = Start-Process -FilePath "python" -ArgumentList $AIAgentScript, "--api-key", $ApiKey, "--port", "8765" -PassThru
    
    Write-Host "`nAI-enhanced LibreOffice Writer is now running!" -ForegroundColor Green
    Write-Host "- LibreOffice Writer is available with UNO bridge on port 2002 (PID: $($LO_Process.Id))" -ForegroundColor Gray
    Write-Host "- AI Agent is running on port 8765 (PID: $($AI_Process.Id))" -ForegroundColor Gray
    Write-Host "- Use the AI Assistant panel in the sidebar to interact with the agent" -ForegroundColor Gray
    
    Write-Host "`nPress any key to stop both services..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    # Cleanup
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    try {
        Stop-Process -Id $AI_Process.Id -Force -ErrorAction SilentlyContinue
        Stop-Process -Id $LO_Process.Id -Force -ErrorAction SilentlyContinue
        Write-Host "Services stopped." -ForegroundColor Green
    } catch {
        Write-Warning "Some processes may still be running. Check Task Manager if needed."
    }
} else {
    Write-Error "AI Agent script not found at: $AIAgentScript"
    Stop-Process -Id $LO_Process.Id -Force -ErrorAction SilentlyContinue
    exit 1
}