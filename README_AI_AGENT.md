# LibreOffice Writer with AI Agent

A LibreOffice Writer fork that integrates an AI writing assistant similar to Cursor's AI capabilities. This adds an AI agent that can help with text rewriting, summarization, expansion, grammar correction, and other writing tasks directly within LibreOffice Writer.

## Features

- **AI-powered text editing**: Select text and ask the AI to rewrite, improve, or modify it
- **Smart writing assistance**: Summarize, expand, or correct text with simple commands
- **Integrated sidebar panel**: Chat interface directly in LibreOffice Writer
- **OpenAI integration**: Powered by OpenAI's GPT models
- **Quick action buttons**: One-click access to common AI operations
- **Real-time document manipulation**: AI directly modifies your document

## Architecture

The system consists of several components:

1. **Python AI Agent** (`sw/source/aiagent/ai_agent.py`): Backend service that handles OpenAI API calls and UNO communication
2. **UNO Bridge Service** (`sw/source/aiagent/AIAgentService.*`): C++ service that bridges LibreOffice and Python
3. **Sidebar Panel** (`sw/source/uibase/sidebar/AIAgentPanel.*`): User interface for interacting with the AI
4. **Build Configuration**: Integration into LibreOffice build system

## Prerequisites

- LibreOffice development environment (for building from source)
- Python 3.7 or newer
- OpenAI API key
- Required Python packages: `openai`, `requests`

## Quick Start (Pre-built LibreOffice)

If you have a pre-built version of this enhanced LibreOffice:

### Windows
```batch
# Using batch script
start_writer_ai.bat YOUR_OPENAI_API_KEY

# Using PowerShell (recommended)
powershell -ExecutionPolicy Bypass -File start_writer_ai.ps1 -ApiKey YOUR_OPENAI_API_KEY
```

### Linux/macOS
```bash
chmod +x start_writer_ai.sh
./start_writer_ai.sh YOUR_OPENAI_API_KEY
```

## Building from Source

### 1. Set up LibreOffice Build Environment

Follow the standard LibreOffice build instructions for your platform:
- [LibreOffice Development Wiki](https://wiki.documentfoundation.org/Development)
- [Building LibreOffice](https://wiki.documentfoundation.org/Development/BuildingOnWindows) (Windows)
- [Building LibreOffice](https://wiki.documentfoundation.org/Development/BuildingOnLinux) (Linux)

### 2. Build the Enhanced Writer

```bash
# Configure build
./autogen.sh

# Build LibreOffice with AI agent components
make sw

# Or build everything
make
```

### 3. Install Python Dependencies

```bash
pip install openai requests
```

## Usage

### Starting the System

1. **Start LibreOffice with UNO Bridge**:
   ```bash
   soffice --writer --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" --nologo --nodefault --nolockcheck --norestore
   ```

2. **Start the AI Agent**:
   ```bash
   python sw/source/aiagent/ai_agent.py --api-key YOUR_OPENAI_API_KEY --port 8765
   ```

3. **Open the AI Assistant Panel** in LibreOffice Writer sidebar

### Using the AI Assistant

#### Quick Actions
- **Rewrite**: Select text and click "Rewrite" to improve it
- **Summarize**: Select text or use on whole document to create a summary
- **Expand**: Add more details to selected text
- **Correct**: Fix grammar and spelling errors

#### Custom Commands
Type natural language commands in the chat interface:
- "Rewrite this in a more formal tone"
- "Make this paragraph simpler"
- "Add more technical details to this explanation"
- "Fix any grammar mistakes"
- "Translate this to Spanish"

### Command Examples

```
User: "rewrite in simpler words"
→ AI rewrites selected text to be more accessible

User: "summarize this document"
→ AI creates a summary and inserts it into the document

User: "expand this with examples"
→ AI adds relevant examples to the selected text

User: "make this more professional"
→ AI adjusts the tone and language to be more formal
```

## API Reference

### AI Agent Service (C++)

The `AIAgentService` class provides the UNO interface:

```cpp
// Send a command to the AI agent
void sendCommand(const OUString& sCommand);

// Process text selection with specific operation
void processTextSelection(const OUString& sOperation);

// Check if agent is running
bool isAgentRunning() const;
```

### Python AI Agent

The Python backend provides these capabilities:

```python
# Main service class
class AIAgentService:
    def process_user_command(self, command: str) -> Dict[str, Any]
    def get_selected_text(self) -> Optional[str]
    def replace_selected_text(self, new_text: str) -> bool
    def insert_text_at_cursor(self, text: str) -> bool
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Python Agent Options
- `--api-key`: OpenAI API key
- `--port`: Socket server port (default: 8765)

### LibreOffice UNO Bridge
- Default port: 2002
- Protocol: URP (UNO Remote Protocol)

## Development

### Adding New AI Commands

1. **Extend Python Backend**:
   ```python
   def _handle_new_command(self, command: str) -> Dict[str, Any]:
       # Implement new command logic
       pass
   ```

2. **Add UI Controls** (optional):
   Update `AIAgentPanel.ui` and corresponding C++ handlers

3. **Update Command Processing**:
   Modify `process_user_command()` to recognize new command patterns

### Building Individual Components

```bash
# Build just the Writer module
make sw

# Build UI configurations
make UIConfig_swriter

# Build individual files
make sw/source/aiagent/AIAgentService.cxx
```

## Troubleshooting

### Common Issues

1. **"Failed to connect to LibreOffice"**
   - Ensure LibreOffice is running with UNO bridge
   - Check if port 2002 is available

2. **"OpenAI API key required"**
   - Set the `OPENAI_API_KEY` environment variable
   - Or pass it as `--api-key` parameter

3. **"Python dependencies missing"**
   - Install required packages: `pip install openai requests`

4. **"AI Agent Panel not visible"**
   - Check if the panel is registered in sidebar configuration
   - Restart LibreOffice after building

### Debug Information

The AI agent logs to console with detailed information:
```bash
python ai_agent.py --api-key YOUR_KEY --port 8765
# Outputs connection status, command processing, and errors
```

LibreOffice debug output (if enabled):
```bash
SAL_LOG="+WARN+INFO.sw.aiagent+INFO.sw.sidebar" soffice --writer
```

## Security Considerations

- **API Key Protection**: Never commit API keys to version control
- **Network Security**: The UNO bridge and AI agent use localhost connections
- **Data Privacy**: Selected text is sent to OpenAI's API - review their privacy policy
- **Firewall**: Ensure ports 2002 and 8765 are available locally

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow LibreOffice coding conventions for C++ code
- Use PEP 8 for Python code
- Add appropriate documentation and comments

## License

This project inherits LibreOffice's licensing:
- Main code: Mozilla Public License 2.0 (MPL-2.0)
- Some components: Apache License 2.0
- Documentation: Creative Commons Attribution-ShareAlike 4.0

See individual files for specific license information.

## Acknowledgments

- LibreOffice community for the excellent foundation
- OpenAI for providing the AI capabilities
- Cursor team for inspiration on AI-integrated editing

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review LibreOffice development documentation
3. Open an issue in this repository