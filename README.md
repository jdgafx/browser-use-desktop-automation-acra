# Browser Use Desktop Automation - Claude Code Edition

AI-powered browser automation with natural language commands using DeepSeek AI, built on browser-use desktop + web-ui integration.

## 🚀 Features

- **Natural Language Browser Control**: Give commands in plain English
- **DeepSeek AI Integration**: Powered by DeepSeek's advanced reasoning models (Chat & Reasoner)
- **Complete Browser-Use Stack**: Desktop app + Web UI + Python backend
- **Multi-LLM Support**: DeepSeek, OpenAI, Anthropic, Google, Ollama, and more
- **MCP Server Integration**: 14 pre-configured Model Context Protocol servers
- **Chrome Debug Protocol**: Direct browser control and automation
- **Cross-Platform**: Windows, macOS, and Linux support

## 🛠️ Architecture

This project uses a **3-layer architecture**:

1. **Electron Main Process** (`browser-use-desktop-actual/src/main.ts`):
   - Spawns Python backend on port 7788
   - Manages Chrome with Debug Protocol on port 9222
   - Handles window positioning and process lifecycle

2. **Python Backend** (`browser-use-desktop-actual/lib/web-ui/webui.py`):
   - Gradio web interface serving on port 7788
   - Browser automation via Playwright + Chrome Debug Protocol
   - Multi-LLM support with DeepSeek as default

3. **Electron Renderer** (`browser-use-desktop-actual/src/renderer.ts`):
   - Embeds Python UI via webview
   - Real-time console output and process management

## 🔧 Quick Setup

### Prerequisites
- Node.js 20.19.2+
- Python 3.11+
- Chrome/Chromium browser
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jdgafx/browser-use-desktop-automation-cc.git
   cd browser-use-desktop-automation-cc
   ```

2. **Setup the desktop application**:
   ```bash
   cd browser-use-desktop-actual
   npm install
   ```

3. **Setup the Python backend**:
   ```bash
   cd lib/web-ui
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install setuptools  # Required for distutils
   ```

4. **Configure DeepSeek API**:
   ```bash
   cp .env.example .env
   # Edit .env and add your DeepSeek API key:
   # DEEPSEEK_API_KEY=your_api_key_from_platform_deepseek_com
   ```

5. **Start the application**:
   ```bash
   cd ../../  # Back to browser-use-desktop-actual
   npm start
   ```

## 🌐 Usage

1. **Access the Web Interface**: http://localhost:7788
2. **Configure Settings**:
   - Go to "Agent Settings" tab
   - Select "deepseek" as LLM Provider (default)
   - Choose a DeepSeek model:
     - `deepseek-chat` - for general conversation and tasks
     - `deepseek-reasoner` - for advanced reasoning (recommended for complex automation)
   - Optionally enter API key directly in UI

3. **Run Automation**:
   - Go to "Run Agent" tab
   - Enter natural language commands like:
     - "Navigate to Google and search for AI news"
     - "Open YouTube and find videos about machine learning"
     - "Fill out the contact form with my information"

## 🔑 API Configuration

### DeepSeek AI (Default Provider)
```bash
DEEPSEEK_API_KEY=your_api_key_here  # Get from platform.deepseek.com
DEEPSEEK_ENDPOINT=https://api.deepseek.com  # Default endpoint
DEFAULT_LLM=deepseek  # Set as default
```

### Other Supported Providers
- **OpenAI**: `OPENAI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **Google Gemini**: `GOOGLE_API_KEY`
- **Ollama**: `OLLAMA_ENDPOINT=http://localhost:11434`

## 📁 Project Structure

```
browser-use-desktop-automation-cc/
├── browser-use-desktop-actual/          # Main application
│   ├── src/                            # Electron TypeScript source
│   │   ├── main.ts                     # Main process
│   │   ├── renderer.ts                 # Renderer process
│   │   └── config.ts                   # Configuration
│   ├── lib/web-ui/                     # Python backend
│   │   ├── webui.py                    # Main server
│   │   ├── src/                        # Source code
│   │   └── .env                        # Environment config
│   └── package.json                    # Node dependencies
├── mcp-servers-setup.md               # MCP configuration guide
└── CLAUDE.md                         # Development instructions
```

## 🤖 Available DeepSeek Models

### Recommended for Browser Automation:
- **`deepseek-reasoner`** (DeepSeek-R1) - Advanced reasoning, perfect for complex automation logic
- **`deepseek-chat`** (DeepSeek-V3) - General conversation and task execution

### Model Comparison:
| Model | Best For | Reasoning | Speed |
|-------|----------|-----------|-------|
| `deepseek-reasoner` | Complex automation, multi-step tasks | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| `deepseek-chat` | General automation, simple tasks | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🔍 Troubleshooting

### Connection Refused (localhost:7788)
1. Check if Python backend is running:
   ```bash
   cd browser-use-desktop-actual/lib/web-ui
   source .venv/bin/activate
   python webui.py --ip 127.0.0.1 --port 7788
   ```

2. Install missing dependencies:
   ```bash
   pip install setuptools langchain-openai
   ```

### Chrome Not Opening
- Verify Chrome is installed and accessible
- Check Chrome debug port (9222) isn't in use
- Review Chrome arguments in `src/config.ts`

### API Key Issues
- Ensure API key is valid and has proper permissions
- Check API key is set in `.env` file
- Verify no rate limits or quota issues

## 🛠️ Development

### Running in Development Mode
```bash
cd browser-use-desktop-actual
npm start  # Starts both Electron and Python backend
```

### Building for Production
```bash
npm run build
npm run make  # Creates distributables
```

### Testing API Integration
```bash
cd lib/web-ui
source .venv/bin/activate
python -c "
from src.utils.llm_provider import get_llm_model
llm = get_llm_model(provider='deepseek', model_name='deepseek-chat')
response = llm.invoke('Hello!')
print(response.content)
"
```

## 📖 Documentation

- [CLAUDE.md](CLAUDE.md) - Complete development guide
- [mcp-servers-setup.md](mcp-servers-setup.md) - MCP server configuration
- [Browser-Use Documentation](https://docs.browser-use.com)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test across platforms
5. Submit a pull request

## 📄 License

MIT License - see individual component licenses for details.

## 🙏 Acknowledgments

- [browser-use](https://github.com/browser-use/browser-use) - Core automation library
- [browser-use/desktop](https://github.com/browser-use/desktop) - Desktop application base
- [browser-use/web-ui](https://github.com/browser-use/web-ui) - Web interface
- DeepSeek Platform - Advanced AI models for automation

---

**Built with ❤️ using Claude Code** - AI-powered development at its finest!