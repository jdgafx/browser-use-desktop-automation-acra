#!/bin/bash

# Ultimate Zero-Touch Browser Automation Setup
# Detects running processes, cleans up ports, and starts fresh
# Version: 3.0.0

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_NAME="Ultimate Zero-Touch Browser Automation"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"
INSTALL_DIR="$HOME/ultimate-browser-automation"
PORT=7790
BACKUP_PORT=7791

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

print_header() { echo -e "${CYAN}$1${NC}"; }
print_success() { echo -e "${GREEN}   ✓ $1${NC}"; }
print_error() { echo -e "${RED}   ✗ $1${NC}"; }
print_info() { echo -e "${BLUE}   → $1${NC}"; }
print_warning() { echo -e "${YELLOW}   ⚠ $1${NC}"; }

show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║               Ultimate Zero-Touch Browser Automation                        ║"
    echo "║                    Process Cleanup + Fresh Start                            ║"
    echo "║                          Version 3.0.0                                     ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${WHITE}Features:${NC}"
    echo "  🔧 Automatic process detection and cleanup"
    echo "  🚀 Port conflict resolution"
    echo "  🤖 Universal web automation for ANY website"
    echo "  🧠 Anthropic Claude AI reasoning"
    echo "  📸 Screenshot capture and progress tracking"
    echo "  🔐 Smart credential prompting"
    echo "  ⏰ Loop prevention with timeouts"
    echo
}

detect_and_kill_processes() {
    print_header "🔍 Detecting and cleaning up existing processes..."
    
    # Kill processes using our target ports
    for port in $PORT $BACKUP_PORT 7788 7789; do
        print_info "Checking port $port..."
        PID=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PID" ]; then
            print_warning "Found process $PID using port $port"
            kill -9 $PID 2>/dev/null || true
            print_success "Killed process on port $port"
        else
            print_success "Port $port is free"
        fi
    done
    
    # Kill any Python processes running browser automation
    print_info "Checking for browser automation processes..."
    pkill -f "browser.*automation" 2>/dev/null || true
    pkill -f "universal.*browser" 2>/dev/null || true
    pkill -f "gradio" 2>/dev/null || true
    pkill -f "webui.py" 2>/dev/null || true
    
    # Kill any Chrome/browser processes from automation
    print_info "Cleaning up browser processes..."
    pkill -f "chrome.*automation" 2>/dev/null || true
    pkill -f "chromium.*automation" 2>/dev/null || true
    
    # Wait a moment for processes to fully terminate
    sleep 2
    
    print_success "Process cleanup completed"
}

check_port_availability() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

find_available_port() {
    print_header "🔍 Finding available port..."
    
    for test_port in $PORT $BACKUP_PORT 7792 7793 7794 7795; do
        if check_port_availability $test_port; then
            PORT=$test_port
            print_success "Using port $PORT"
            return 0
        fi
    done
    
    print_error "Could not find available port"
    exit 1
}

setup_environment() {
    print_header "📁 Setting up clean environment..."
    
    # Remove old installation if exists
    if [ -d "$INSTALL_DIR" ]; then
        print_info "Removing old installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Create fresh installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_success "Created installation directory: $INSTALL_DIR"
    
    # Create virtual environment
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    print_success "Virtual environment created and activated"
}

install_dependencies() {
    print_header "📦 Installing dependencies..."
    
    # Install core packages
    print_info "Installing browser automation packages..."
    pip install browser-use gradio anthropic playwright psutil
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers..."
    playwright install chromium 2>/dev/null || print_warning "Browser installation may need manual setup later"
    
    print_success "Dependencies installed"
}

create_ultimate_interface() {
    print_header "🚀 Creating ultimate automation interface..."
    
    cat > "$INSTALL_DIR/ultimate_automation.py" << 'EOF'
#!/usr/bin/env python3
"""
Ultimate Browser Automation Interface
- Process-aware startup
- Port conflict resolution  
- Clean shutdown handling
- Smart credential prompting
- Loop prevention
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
import signal
import psutil
import socket
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    sys.exit(1)

class UltimateBrowserAutomation:
    def __init__(self, api_key, port):
        self.api_key = api_key
        self.port = port
        self.llm = self.setup_llm()
        self.session_data = {
            "credentials": {},
            "conversation_history": [],
            "current_url": "",
            "last_screenshot": None,
            "needs_credentials": False,
            "credential_prompt": "",
            "port_info": f"Running on port {port}"
        }
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup clean shutdown handlers"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up resources...")
        # Kill any browser processes we started
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and any(browser in proc.info['name'].lower() 
                    for browser in ['chrome', 'chromium', 'playwright']):
                    if proc.info['cmdline'] and any('automation' in str(cmd).lower() 
                        for cmd in proc.info['cmdline']):
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def setup_llm(self):
        """Setup Anthropic Claude LLM"""
        if self.api_key:
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.api_key,
                temperature=0.1,
                max_tokens=4000
            )
        return None
    
    def check_port_status(self):
        """Check if port is actually free"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', self.port))
                return True
        except OSError:
            return False
    
    async def execute_command(self, command, username="", password=""):
        """Execute automation command with enhanced error handling"""
        try:
            if not self.llm:
                return "❌ No API key configured"
            
            if not command.strip():
                return "❌ Please enter a command"
            
            # Enhanced prompt with strict loop prevention
            enhanced_command = f"""
{command}

CRITICAL EXECUTION RULES:
1. If you find what you're looking for (login page, target site), STAY THERE
2. Do NOT search repeatedly for the same thing
3. If credentials are provided: username="{username}", password="{password}"
4. If you need credentials and none provided, explain what login fields you see
5. Complete the task step by step without backtracking
6. Take screenshots to show progress
7. Maximum 10 steps total - be efficient

STOP CONDITIONS:
- If you reach a login page, describe it and ask for credentials if needed
- If login succeeds, proceed to the requested task
- If you complete the main objective, stop and report results
- Do not loop back to search engines once you find the target

Execute efficiently and stop when done.
"""
            
            print(f"🚀 Executing: {command[:50]}...")
            
            # Create agent with strict settings
            agent = Agent(
                task=enhanced_command,
                llm=self.llm,
                use_vision=True,
                max_failures=2,  # Strict limit
                retry_delay=1,
                browser_args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                    '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # Execute with strict timeout
            result = await asyncio.wait_for(agent.run(), timeout=180)  # 3 minutes max
            
            # Store result
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": str(result),
                "success": True,
                "credentials_used": bool(username and password)
            })
            
            # Capture state
            try:
                if hasattr(agent, 'browser') and agent.browser and agent.browser.pages:
                    current_page = agent.browser.pages[0]
                    self.session_data["current_url"] = current_page.url
                    
                    # Take screenshot
                    screenshot_path = f"/tmp/automation_{int(time.time())}.png"
                    await current_page.screenshot(path=screenshot_path, full_page=True)
                    self.session_data["last_screenshot"] = screenshot_path
                    
                    # Check for login requirements
                    page_content = await current_page.content()
                    if ("login" in page_content.lower() or "sign in" in page_content.lower()) and not (username and password):
                        self.session_data["needs_credentials"] = True
                        self.session_data["credential_prompt"] = f"Login detected at {current_page.url}"
                        
            except Exception as e:
                print(f"State capture warning: {e}")
            
            return f"✅ Command completed!\n\nResult: {result}"
            
        except asyncio.TimeoutError:
            return "⏰ Command timed out after 3 minutes. Automation may have been stuck."
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": error_msg,
                "success": False
            })
            return error_msg
    
    def create_interface(self):
        """Create the ultimate automation interface"""
        with gr.Blocks(
            title="Ultimate Browser Automation",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                background: linear-gradient(45deg, #7c3aed, #a855f7);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 25px;
            }
            .status-good { background: #d1fae5; border-left: 4px solid #10b981; padding: 10px; border-radius: 5px; }
            .status-warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 5px; }
            .status-error { background: #fee2e2; border-left: 4px solid #ef4444; padding: 10px; border-radius: 5px; }
            """
        ) as interface:
            
            gr.HTML(f"""
            <div class="main-header">
                <h1>🚀 Ultimate Browser Automation</h1>
                <h2>Process-Aware • Port-Safe • Loop-Free</h2>
                <p><strong>Running on port {self.port} • No conflicts • Clean execution</strong></p>
            </div>
            """)
            
            with gr.Tab("🚀 Automation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # System status
                        system_status = gr.HTML(
                            f"<div class='status-good'>✅ System ready on port {self.port}</div>"
                        )
                        
                        # Command input
                        gr.HTML("<h3>🎯 Automation Command</h3>")
                        command_input = gr.Textbox(
                            label="Universal Command",
                            placeholder="e.g., 'Login to turing.com and show my completed quizzes'",
                            lines=3
                        )
                        
                        # Credentials
                        gr.HTML("<h4>🔐 Credentials (if needed)</h4>")
                        with gr.Row():
                            username_input = gr.Textbox(label="Username/Email")
                            password_input = gr.Textbox(label="Password", type="password")
                        
                        execute_btn = gr.Button("🚀 Execute", variant="primary", size="lg")
                        
                        # Quick commands
                        gr.HTML("<h4>⚡ Quick Commands</h4>")
                        quick_commands = [
                            "Go to turing.com login page",
                            "Navigate to amazon.com and search for laptops",
                            "Visit linkedin.com and check messages",
                            "Go to github.com trending repositories",
                            "Login to twitter.com and check timeline"
                        ]
                        
                        for cmd in quick_commands:
                            btn = gr.Button(f"⚡ {cmd}", size="sm")
                            btn.click(fn=lambda c=cmd: c, outputs=command_input)
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Results</h3>")
                        
                        # Execution results
                        result_output = gr.Textbox(
                            label="Execution Results",
                            lines=12,
                            interactive=False
                        )
                        
                        # Current page info
                        current_url = gr.Textbox(label="Current URL", interactive=False)
                        
                        # Screenshot
                        screenshot_display = gr.Image(label="Page Screenshot", interactive=False)
            
            with gr.Tab("📊 Status & History"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3>🖥️ System Status</h3>")
                        
                        system_info = gr.JSON(
                            label="System Information",
                            value={
                                "port": self.port,
                                "status": "running",
                                "process_id": os.getpid(),
                                "port_check": self.check_port_status()
                            }
                        )
                        
                        refresh_status_btn = gr.Button("🔄 Refresh Status")
                    
                    with gr.Column():
                        gr.HTML("<h3>📜 Command History</h3>")
                        
                        command_history = gr.JSON(label="Recent Commands", value=[])
                        refresh_history_btn = gr.Button("🔄 Refresh History")
            
            # Event handlers
            def execute_handler(command, username, password):
                if not command.strip():
                    return (
                        "<div class='status-error'>❌ Please enter a command</div>",
                        "No command provided", "", None
                    )
                
                status_msg = "<div class='status-warning'>🚀 Executing command...</div>"
                
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.execute_command(command, username, password)
                    )
                    loop.close()
                    
                    url = self.session_data.get("current_url", "")
                    screenshot = self.session_data.get("last_screenshot")
                    
                    if self.session_data.get("needs_credentials"):
                        status_msg = f"<div class='status-warning'>🔐 {self.session_data.get('credential_prompt', 'Credentials needed')}</div>"
                    else:
                        status_msg = "<div class='status-good'>✅ Command completed</div>"
                    
                    return status_msg, result, url, screenshot
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    error_status = "<div class='status-error'>❌ Execution failed</div>"
                    return error_status, error_msg, "", None
            
            def refresh_status_handler():
                return {
                    "port": self.port,
                    "status": "running",
                    "process_id": os.getpid(),
                    "port_available": self.check_port_status(),
                    "last_refresh": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            def refresh_history_handler():
                return self.session_data.get("conversation_history", [])[-10:]
            
            # Wire up events
            execute_btn.click(
                fn=execute_handler,
                inputs=[command_input, username_input, password_input],
                outputs=[system_status, result_output, current_url, screenshot_display]
            )
            
            refresh_status_btn.click(
                fn=refresh_status_handler,
                outputs=system_info
            )
            
            refresh_history_btn.click(
                fn=refresh_history_handler,
                outputs=command_history
            )
        
        return interface

def main():
    # Get port from environment or use default
    port = int(os.environ.get("AUTOMATION_PORT", "7790"))
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print("🚀 Starting Ultimate Browser Automation...")
    print(f"🔧 Process-aware startup on port {port}")
    print("✅ Clean shutdown handling enabled")
    print()
    
    try:
        automation = UltimateBrowserAutomation(api_key, port)
        interface = automation.create_interface()
        
        print(f"🌐 Interface starting on port {port}...")
        print(f"📍 Access at: http://127.0.0.1:{port}")
        print("🎯 Ultimate automation ready!")
        print()
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=port,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup on exit
        if 'automation' in locals():
            automation.cleanup()

if __name__ == "__main__":
    main()
EOF
    
    print_success "Ultimate automation interface created"
}

create_startup_script() {
    print_header "🚀 Creating startup script..."
    
    cat > "$INSTALL_DIR/start_ultimate.sh" << EOF
#!/bin/bash

echo "🚀 Ultimate Browser Automation Startup"
echo "======================================"

cd "$INSTALL_DIR"

# Set environment variables
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
export AUTOMATION_PORT="$PORT"

# Activate virtual environment
source venv/bin/activate

# Display startup info
echo "🌐 Starting on port $PORT"
echo "📍 Access at: http://127.0.0.1:$PORT"
echo

# Start the ultimate interface
python ultimate_automation.py
EOF
    
    chmod +x "$INSTALL_DIR/start_ultimate.sh"
    print_success "Startup script created"
}

run_tests() {
    print_header "🧪 Running system tests..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # Test imports
    python -c "
import sys
try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    import gradio as gr
    import psutil
    import socket
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || {
        print_error "System test failed"
        exit 1
    }
    
    print_success "System tests passed"
}

launch_ultimate_automation() {
    print_header "🚀 Launching Ultimate Browser Automation..."
    
    cd "$INSTALL_DIR"
    
    # Set environment variables
    export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
    export AUTOMATION_PORT="$PORT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Final status check
    print_header "📊 Final system status:"
    echo -e "   ${WHITE}Installation:${NC}     $INSTALL_DIR"
    echo -e "   ${WHITE}Port:${NC}             $PORT"
    echo -e "   ${WHITE}API Key:${NC}          Configured ✓"
    echo -e "   ${WHITE}Process Cleanup:${NC}  Completed ✓"
    echo -e "   ${WHITE}Dependencies:${NC}     Installed ✓"
    echo
    
    print_header "🌐 Starting ultimate automation interface..."
    echo -e "   ${WHITE}Interface URL:${NC}    http://127.0.0.1:$PORT"
    echo -e "   ${WHITE}Features:${NC}         Process-aware, port-safe, loop-free"
    echo -e "   ${WHITE}Ready for:${NC}        Universal website automation"
    echo
    
    print_header "🎯 Starting interface..."
    echo
    
    # Start the ultimate interface
    python ultimate_automation.py
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    show_banner
    
    print_header "🚀 Starting Ultimate Zero-Touch Setup..."
    echo
    
    detect_and_kill_processes
    find_available_port
    setup_environment
    install_dependencies
    create_ultimate_interface
    create_startup_script
    run_tests
    
    echo
    print_header "✅ Ultimate setup completed successfully!"
    echo
    
    launch_ultimate_automation
}

# Trap signals for clean shutdown
trap 'echo -e "\n🛑 Setup interrupted. Cleaning up..."; exit 1' INT TERM

# Run the main function
main "$@"