#!/bin/bash
# LibreOffice Writer with AI Agent Startup Script for Linux/macOS
# This script starts LibreOffice Writer with UNO listener and launches the Python AI agent

echo "Starting LibreOffice Writer with AI Agent..."

# Check if OpenAI API key is provided
if [ -z "$1" ]; then
    echo "Error: Please provide OpenAI API key as first argument"
    echo "Usage: ./start_writer_ai.sh YOUR_OPENAI_API_KEY"
    exit 1
fi

OPENAI_API_KEY="$1"

# Find LibreOffice installation
LO_PATH=""
if command -v libreoffice >/dev/null 2>&1; then
    LO_PATH="libreoffice"
elif command -v soffice >/dev/null 2>&1; then
    LO_PATH="soffice"
elif [ -f "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
    LO_PATH="/Applications/LibreOffice.app/Contents/MacOS/soffice"
else
    echo "Error: LibreOffice installation not found"
    echo "Please install LibreOffice or update the path in this script"
    exit 1
fi

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "Error: Python not found. Please install Python"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

# Install required Python packages
echo "Installing required Python packages..."
$PYTHON_CMD -m pip install openai requests >/dev/null 2>&1

# Start LibreOffice Writer with UNO listener
echo "Starting LibreOffice Writer with UNO bridge..."
$LO_PATH --writer --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" --nologo --nodefault --nolockcheck --norestore &
LO_PID=$!

# Wait a bit for LibreOffice to start
sleep 3

# Start Python AI Agent
echo "Starting AI Agent..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$PYTHON_CMD "$SCRIPT_DIR/sw/source/aiagent/ai_agent.py" --api-key "$OPENAI_API_KEY" --port 8765 &
AI_PID=$!

echo "AI-enhanced LibreOffice Writer is now running!"
echo "- LibreOffice Writer is available with UNO bridge on port 2002 (PID: $LO_PID)"
echo "- AI Agent is running on port 8765 (PID: $AI_PID)"
echo "- Use the AI Assistant panel in the sidebar to interact with the agent"
echo ""
echo "Press Ctrl+C to stop both services..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $AI_PID 2>/dev/null
    kill $LO_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
wait