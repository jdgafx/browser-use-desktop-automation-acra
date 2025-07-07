# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a browser automation project that builds upon the existing [browser-use desktop](https://github.com/browser-use/desktop) implementation. The project integrates advanced AI-powered browser automation with the Model Context Protocol (MCP) ecosystem to create a comprehensive automation platform.

## Architecture

### Current Implementation (browser-use-desktop-actual/)
The existing browser-use desktop uses a **3-layer architecture**:

1. **Electron Main Process** (`src/main.ts`):
   - Spawns Python backend (`webui.py`) on port 7788
   - Manages Chrome with Debug Protocol on port 9222
   - Handles window positioning and process lifecycle
   - Creates directories: `~/Downloads/browser-use/{recordings,traces,history}`

2. **Python Backend** (`lib/web-ui/webui.py`):
   - Gradio web interface serving on port 7788
   - Browser automation via Playwright + Chrome Debug Protocol
   - Multi-LLM support (OpenAI, Anthropic, Google, DeepSeek, Ollama)
   - Natural language command processing

3. **Electron Renderer** (`src/renderer.ts`):
   - Embeds Python UI via `<webview>` tag
   - Real-time console output and process management
   - Dark/light theme support

### Communication Flow
```
User Input (Electron) → Python Web-UI (port 7788) → browser-use Library → Chrome CDP (port 9222) → Browser Actions
```

## Development Commands

### Setup and Installation
```bash
# Clone the actual browser-use desktop repository
git clone https://github.com/browser-use/desktop.git browser-use-desktop-actual
cd browser-use-desktop-actual

# Install dependencies
npm install

# Development server
npm run dev
# or
vite dev

# Build for production
npm run build

# Package for distribution
npm run make

# Lint code
npm run lint
```

### MCP Servers Development
```bash
# Install MCP servers (already configured in this repo)
npm install @upstash/context7-mcp @modelcontextprotocol/server-filesystem @notionhq/notion-mcp-server @sentry/mcp-server

# Test individual MCP servers
npx @upstash/context7-mcp
npx @modelcontextprotocol/server-filesystem /home/chris
npx @shelm/wikipedia-mcp-server

# Check Claude Desktop MCP configuration
cat ~/.config/claude/claude_desktop_config.json
```

### Chrome Debug Protocol Setup
```bash
# Chrome is launched automatically with these flags:
# --remote-debugging-port=9222
# --user-data-dir=~/.config/browser-use-desktop/ChromeProfile
# --window-position={halfWidth},0
# --window-size={halfWidth},{height}
```

## Key Configuration Files

### Environment Configuration
- **Production config**: `lib/web-ui/.env` (Python backend)
- **Development config**: `.env` (Electron app)
- **Chrome user data**: `~/.config/browser-use-desktop/ChromeProfile/`
- **MCP config**: `~/.config/claude/claude_desktop_config.json`

### Required Environment Variables
```env
# LLM Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key

# Browser Settings
CHROME_PATH=/path/to/chrome
CHROME_CDP=http://localhost:9222
CHROME_USER_DATA=~/.config/browser-use-desktop/ChromeProfile

# MCP Servers (see mcp-servers-setup.md for details)
UPSTASH_REDIS_URL=your_redis_url
UPSTASH_REDIS_TOKEN=your_redis_token
```

## MCP Integration

### Installed MCP Servers
The project includes 14 pre-configured MCP servers:

**Core Infrastructure:**
- `@upstash/context7-mcp` - Context-aware AI with Redis backend
- `@modelcontextprotocol/server-filesystem` - File system operations
- `mcp-server-code-runner` - Code execution capabilities

**Cloud Services:**
- `@notionhq/notion-mcp-server` - Notion workspace integration
- `@sentry/mcp-server` - Error monitoring
- `@elastic/mcp-server-elasticsearch` - Search and analytics
- `@cloudflare/mcp-server-cloudflare` - DNS/CDN management
- `@supabase/mcp-server-supabase` - Database operations

**Data Processing:**
- `@negokaz/excel-mcp-server` - Excel file manipulation
- `@shelm/wikipedia-mcp-server` - Wikipedia search
- `graphlit-mcp-server` - AI knowledge platform

See `mcp-servers-setup.md` for detailed configuration instructions.

### MCP Integration Architecture
```typescript
// Enhanced integration pattern
class MCPEnhancedBrowserAgent {
  private context7: Context7Client;
  private filesystem: FilesystemClient;
  private codeRunner: CodeRunnerClient;
  
  async executeTask(command: string) {
    const context = await this.context7.getContext(command);
    const plan = await this.planTask(command, context);
    
    for (const step of plan.steps) {
      if (step.requiresFileOps) {
        await this.filesystem.execute(step);
      } else if (step.requiresCodeExecution) {
        await this.codeRunner.execute(step);
      } else {
        await this.browserAgent.execute(step);
      }
    }
  }
}
```

## Development Workflow

### 1. Browser Automation Development
- Use Chrome Debug Protocol on port 9222
- Test automation scripts in `lib/web-ui/` Python environment
- Leverage Playwright for browser control
- Implement natural language processing with multiple LLM providers

### 2. Electron App Development
- Main process: `src/main.ts` (process management)
- Renderer process: `src/renderer.ts` (UI and communication)
- Preload script: `src/preload.ts` (secure IPC bridge)
- Configuration: `src/config.ts` (cross-platform settings)

### 3. MCP Server Development
- Create custom MCP servers for browser-specific tasks
- Integrate with existing MCP ecosystem
- Use Context7 for session persistence across browser restarts
- Implement filesystem operations for downloads/uploads

### 4. Testing Strategy
```bash
# Test Python backend standalone
cd lib/web-ui
python webui.py --ip 127.0.0.1 --port 7788

# Test Chrome automation
# Chrome should be accessible at http://localhost:9222/json

# Test MCP servers individually
npx [mcp-server-name]

# Full integration test
npm run dev
```

## Project Structure

```
/home/chris/dev/browser-use-desktop-automation/
├── browser-use-desktop-actual/          # Actual browser-use implementation
│   ├── src/                            # Electron TypeScript source
│   │   ├── main.ts                     # Main process (process management)
│   │   ├── renderer.ts                 # Renderer process (UI)
│   │   ├── preload.ts                  # IPC bridge
│   │   └── config.ts                   # Configuration management
│   ├── lib/web-ui/                     # Python Gradio backend
│   │   └── webui.py                    # Web interface server
│   ├── package.json                    # Node.js dependencies
│   ├── forge.config.ts                 # Electron builder config
│   └── vite.*.config.ts                # Vite build configuration
├── awesome-mcp-servers/                # MCP server repository
├── node_modules/                       # Installed MCP servers
├── mcp-servers-setup.md               # MCP configuration guide
├── browser-use-desktop-automation-PRD.txt  # Product requirements
├── browser-use-desktop-automation-setup-run.sh  # Setup script
└── ~/.config/claude/claude_desktop_config.json  # Claude MCP config
```

## Key Implementation Patterns

### 1. Process Management
- Electron main process spawns and manages Python backend
- Python process runs independently with Gradio web server
- Chrome launched with debug protocol for automation
- Graceful cleanup on app exit with process termination

### 2. Cross-Process Communication
- IPC between Electron main/renderer via preload script
- HTTP/WebSocket communication with Python backend
- Chrome Debug Protocol for browser control
- MCP protocol for server communication

### 3. Error Handling
- Retry mechanisms with exponential backoff
- Process restart capabilities from UI
- Comprehensive logging to console and files
- Graceful degradation when components fail

### 4. Security Considerations
- Sandboxed renderer process with context isolation
- Secure IPC communication patterns
- Chrome user data directory isolation
- Environment variable management for API keys

## Debugging and Troubleshooting

### Common Issues
1. **Python backend not starting**: Check virtual environment and dependencies
2. **Chrome not connecting**: Verify debug port 9222 is available
3. **MCP servers failing**: Check API keys and network connectivity
4. **Electron build issues**: Clear node_modules and reinstall

### Debug Tools
```bash
# Enable Electron developer tools
mainWindow.webContents.openDevTools();

# Check Chrome debug endpoint
curl http://localhost:9222/json/version

# Test Python backend directly
curl http://127.0.0.1:7788

# MCP server diagnostics
npx [mcp-server] --help
```

### Logging
- Electron logs: Console in main/renderer processes
- Python logs: Gradio console output on port 7788
- Chrome logs: Debug protocol and browser console
- MCP logs: Individual server output

## Performance Considerations

### Browser Automation Targets (from PRD)
- Page load time: <2s for 95% of requests
- Element interaction: <100ms response time
- Memory usage: <500MB for single browser instance
- Success rate: >95% for standard web interactions
- Concurrent users: Support 1000+ users

### Optimization Strategies
- Use existing Chrome instance (no fresh browser spawning)
- Implement element caching and reuse
- Optimize screenshot/recording quality vs performance
- Batch operations where possible
- Use MCP servers for enhanced caching (Context7)

## Extension Points

### 1. Custom MCP Servers
Create browser-automation-specific MCP servers:
```typescript
// Example: browser-automation-mcp-server
export class BrowserAutomationMCPServer extends MCPServer {
  tools = [
    "navigate", "click_element", "type_text", "take_screenshot",
    "extract_data", "wait_for_element", "execute_javascript"
  ];
}
```

### 2. LLM Provider Extensions
Add new LLM providers to the Python backend:
```python
# In lib/web-ui/webui.py
class CustomLLMProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_completion(self, prompt: str) -> str:
        # Custom LLM integration
        pass
```

### 3. Browser Engine Extensions
Support additional browsers beyond Chrome:
```typescript
// In src/config.ts
const BROWSER_ENGINES = {
  chrome: ChromeEngine,
  firefox: FirefoxEngine,
  safari: SafariEngine,
  edge: EdgeEngine
};
```

## Deployment

### Local Development
```bash
npm run dev  # Start development server
```

### Production Build
```bash
npm run build   # Build application
npm run make    # Create distributables
```

### Distribution
- macOS: `.dmg` installer
- Windows: `.exe` installer  
- Linux: `.deb`, `.rpm`, `.AppImage`

### Auto-Updates
Electron's built-in update mechanism handles automatic updates for end users.

## Contributing

When working on this project:

1. **Follow the existing architecture patterns**
2. **Test across all supported platforms** (macOS, Windows, Linux)
3. **Ensure MCP server compatibility**
4. **Maintain backward compatibility** with existing browser-use scripts
5. **Document API changes** in this file
6. **Test with multiple LLM providers**
7. **Verify Chrome Debug Protocol integration**

## Resources

- [Browser-Use Documentation](https://docs.browser-use.com)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Electron Documentation](https://electronjs.org/docs)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Playwright Documentation](https://playwright.dev/)
- [Gradio Documentation](https://gradio.app/)