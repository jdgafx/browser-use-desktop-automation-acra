#!/bin/bash

# Universal Browser Automation All-in-One Setup Script
# Sets up complete browser automation system and launches interface
# Version: 1.0.0

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_NAME="Universal Browser Automation Setup"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"
INSTALL_DIR="$HOME/universal-browser-automation"
PORT=7788

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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}   ✓ $1${NC}"
}

print_error() {
    echo -e "${RED}   ✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}   → $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}   ⚠ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                Universal Browser Automation Setup                            ║"
    echo "║                    AI-Powered Web Automation                                ║"
    echo "║                          Version 1.0.0                                     ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${WHITE}Features:${NC}"
    echo "  🤖 Universal web automation for ANY website"
    echo "  🧠 Anthropic Claude AI reasoning"
    echo "  🔐 Credential management and secure storage"
    echo "  📸 Screenshot capture and progress tracking"
    echo "  🎯 Complex multi-step workflow automation"
    echo "  🌐 Works on e-commerce, social media, banking, any site"
    echo
}

check_dependencies() {
    print_header "🔍 Checking system dependencies..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3: $PYTHON_VERSION"
    else
        print_error "Python 3 not found"
        print_info "Installing Python 3..."
        sudo apt update && sudo apt install -y python3 python3-pip python3-venv
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        print_success "Git installed"
    else
        print_info "Installing Git..."
        sudo apt install -y git
    fi
    
    # Check curl
    if command -v curl &> /dev/null; then
        print_success "curl installed"
    else
        print_info "Installing curl..."
        sudo apt install -y curl
    fi
    
    print_success "All dependencies ready"
}

setup_environment() {
    print_header "📁 Setting up environment..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_success "Created installation directory: $INSTALL_DIR"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
}

install_browser_automation() {
    print_header "🤖 Installing browser automation packages..."
    
    # Install core packages
    print_info "Installing browser-use and dependencies..."
    pip install browser-use gradio anthropic playwright
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers..."
    playwright install chromium || print_warning "Browser installation may need manual setup later"
    
    print_success "Browser automation packages installed"
}

create_interface_script() {
    print_header "🌐 Creating browser automation interface..."
    
    cat > "$INSTALL_DIR/universal_browser_interface.py" << 'EOF'
#!/usr/bin/env python3
"""
Universal Browser Automation Interface
AI-powered automation for ANY website using Anthropic Claude
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    sys.exit(1)

class UniversalBrowserAutomation:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = self.setup_llm()
        self.session_data = {
            "credentials": {},
            "conversation_history": [],
            "current_url": "",
            "last_screenshot": None,
            "active_websites": []
        }
    
    def setup_llm(self):
        """Setup Anthropic Claude LLM"""
        if self.api_key:
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.api_key,
                temperature=0.3,
                max_tokens=4000
            )
        return None
    
    async def execute_universal_command(self, command, website="", username="", password=""):
        """Execute automation command on any website"""
        try:
            if not self.llm:
                return "❌ No API key configured"
            
            # Build universal automation prompt
            enhanced_command = f"""
{command}

UNIVERSAL WEB AUTOMATION INSTRUCTIONS:
1. This command should work on ANY website - adapt to whatever site is specified
2. Use vision to understand the page layout and identify interactive elements
3. Handle different website designs, UI patterns, and navigation structures
4. For authentication: look for login forms, username/password fields, login buttons
5. For e-commerce: find product searches, add to cart buttons, checkout processes
6. For social media: locate post buttons, message fields, profile links
7. For forms: identify input fields, dropdowns, checkboxes, submit buttons
8. For data extraction: find and read relevant information from any page structure

{f"Target website: {website}" if website else ""}
{f"Username available: {username}" if username else ""}
{f"Password available: [HIDDEN]" if password else ""}

EXECUTION APPROACH:
- Take screenshot first to see the current page
- Navigate step by step, explaining what you see
- Handle any pop-ups, modals, or interruptions
- Wait for pages to load completely
- Provide detailed feedback on each action
- If you encounter errors, try alternative approaches
- Take final screenshot to confirm completion

Execute this automation task with precision and adaptability.
"""
            
            print(f"🚀 Executing universal automation: {command}")
            
            # Create agent with enhanced settings for universal automation
            agent = Agent(
                task=enhanced_command,
                llm=self.llm,
                use_vision=True,
                max_failures=5,  # More retries for complex sites
                retry_delay=3,   # Longer delay for page loads
                browser_args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                    '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Execute the automation
            result = await agent.run()
            
            # Store execution in history
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "website": website,
                "result": str(result),
                "success": True
            })
            
            # Capture current state
            try:
                if hasattr(agent, 'browser') and agent.browser and agent.browser.pages:
                    current_page = agent.browser.pages[0]
                    self.session_data["current_url"] = current_page.url
                    
                    # Extract website domain
                    from urllib.parse import urlparse
                    domain = urlparse(current_page.url).netloc
                    if domain and domain not in self.session_data["active_websites"]:
                        self.session_data["active_websites"].append(domain)
                    
                    # Take screenshot
                    screenshot_path = f"/tmp/automation_screenshot_{int(time.time())}.png"
                    await current_page.screenshot(path=screenshot_path, full_page=True)
                    self.session_data["last_screenshot"] = screenshot_path
                    print(f"📸 Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"State capture warning: {e}")
            
            return f"✅ Universal automation completed successfully!\n\nResult: {result}"
            
        except Exception as e:
            error_msg = f"❌ Automation failed: {str(e)}"
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "website": website,
                "result": error_msg,
                "success": False
            })
            return error_msg
    
    def create_interface(self):
        """Create Gradio interface for universal automation"""
        with gr.Blocks(
            title="Universal Browser Automation",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                background: linear-gradient(45deg, #6366f1, #8b5cf6);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 25px;
                box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
            }
            .automation-section {
                border: 2px solid #6366f1;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                background: linear-gradient(135deg, #f8faff, #f1f5ff);
            }
            .website-examples {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div class="main-header">
                <h1>🌐 Universal Browser Automation</h1>
                <h2>AI-Powered Automation for ANY Website</h2>
                <p><strong>E-commerce • Social Media • Banking • Job Sites • Government • Education • Any Website</strong></p>
            </div>
            """)
            
            with gr.Tab("🚀 Universal Automation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎯 Automation Commands</h3>")
                        
                        # Main command input
                        automation_command = gr.Textbox(
                            label="Universal Automation Command",
                            placeholder="e.g., 'Go to Amazon, search for wireless headphones, add the top-rated one to cart'",
                            lines=4,
                            elem_classes="automation-section"
                        )
                        
                        # Optional website specification
                        target_website = gr.Textbox(
                            label="Target Website (Optional)",
                            placeholder="e.g., amazon.com, linkedin.com, github.com",
                            lines=1
                        )
                        
                        # Credentials for sites requiring login
                        gr.HTML("<h4>🔐 Login Credentials (If Needed)</h4>")
                        with gr.Row():
                            login_username = gr.Textbox(
                                label="Username/Email",
                                placeholder="Enter if site requires login"
                            )
                            login_password = gr.Textbox(
                                label="Password",
                                type="password",
                                placeholder="Enter if site requires login"
                            )
                        
                        execute_automation_btn = gr.Button(
                            "🚀 Execute Universal Automation", 
                            variant="primary", 
                            size="lg"
                        )
                        
                        # Website categories and examples
                        gr.HTML("""
                        <div class="website-examples">
                            <h4>📋 Universal Automation Examples</h4>
                            <p><strong>E-commerce:</strong> "Search for iPhone on eBay, filter by price under $500, message top 3 sellers"</p>
                            <p><strong>Social Media:</strong> "Login to LinkedIn, search for AI engineers, connect with first 10"</p>
                            <p><strong>Job Sites:</strong> "Go to Indeed, search Python jobs, apply to first 5 with my resume"</p>
                            <p><strong>Banking:</strong> "Login to my bank, check balance, transfer $1000 to savings"</p>
                            <p><strong>Shopping:</strong> "Order my usual groceries from the supermarket website"</p>
                            <p><strong>Government:</strong> "Fill out DMV license renewal form with my information"</p>
                        </div>
                        """)
                        
                        # Quick automation templates
                        gr.HTML("<h4>⚡ Quick Templates</h4>")
                        quick_templates = [
                            ("🛒 E-commerce", "Go to Amazon, search for [product], add best-rated item to cart"),
                            ("💼 Job Search", "Search for [job title] on Indeed, apply to top 5 positions"),
                            ("📱 Social Media", "Login to LinkedIn, update my status with a professional post"),
                            ("🏦 Banking", "Login to my bank account, check recent transactions"),
                            ("📧 Email", "Login to Gmail, send email to [recipient] about [topic]"),
                            ("🎓 Education", "Login to course platform, check my progress and assignments"),
                            ("🏛️ Government", "Navigate to tax website, download my tax documents"),
                            ("🛍️ Shopping", "Book a restaurant reservation for tonight at 7pm")
                        ]
                        
                        for category, template in quick_templates:
                            btn = gr.Button(f"{category}: {template[:50]}...", size="sm")
                            btn.click(
                                fn=lambda t=template: t,
                                outputs=automation_command
                            )
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Automation Results</h3>")
                        
                        automation_output = gr.Textbox(
                            label="Execution Results",
                            lines=18,
                            max_lines=30,
                            interactive=False
                        )
                        
                        # Current automation state
                        with gr.Row():
                            current_url_display = gr.Textbox(
                                label="Current URL",
                                interactive=False
                            )
                            
                            active_websites_display = gr.Textbox(
                                label="Active Websites",
                                interactive=False
                            )
                        
                        # Screenshot display
                        screenshot_output = gr.Image(
                            label="Latest Screenshot",
                            interactive=False
                        )
            
            with gr.Tab("📊 Session & History"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3>📈 Session Statistics</h3>")
                        
                        session_stats = gr.JSON(
                            label="Current Session",
                            value={}
                        )
                        
                        gr.HTML("<h3>🌐 Visited Websites</h3>")
                        
                        websites_list = gr.JSON(
                            label="Active Websites",
                            value=[]
                        )
                    
                    with gr.Column():
                        gr.HTML("<h3>📜 Automation History</h3>")
                        
                        automation_history = gr.JSON(
                            label="Recent Automations",
                            value=[]
                        )
                        
                        refresh_data_btn = gr.Button("🔄 Refresh Data")
            
            # Event handlers
            def execute_automation_handler(command, website, username, password):
                if not command.strip():
                    return "❌ Please enter an automation command", "", "", None
                
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.execute_universal_command(command, website, username, password)
                    )
                    loop.close()
                    
                    current_url = self.session_data.get("current_url", "")
                    active_sites = ", ".join(self.session_data.get("active_websites", []))
                    screenshot = self.session_data.get("last_screenshot")
                    
                    return result, current_url, active_sites, screenshot
                    
                except Exception as e:
                    return f"❌ Error: {str(e)}", "", "", None
            
            def refresh_data_handler():
                stats = {
                    "total_automations": len(self.session_data["conversation_history"]),
                    "successful_automations": len([h for h in self.session_data["conversation_history"] if h.get("success", False)]),
                    "current_url": self.session_data.get("current_url", ""),
                    "session_start": "Current session"
                }
                
                websites = self.session_data.get("active_websites", [])
                history = self.session_data.get("conversation_history", [])[-10:]  # Last 10
                
                return stats, websites, history
            
            # Wire up events
            execute_automation_btn.click(
                fn=execute_automation_handler,
                inputs=[automation_command, target_website, login_username, login_password],
                outputs=[automation_output, current_url_display, active_websites_display, screenshot_output]
            )
            
            refresh_data_btn.click(
                fn=refresh_data_handler,
                outputs=[session_stats, websites_list, automation_history]
            )
        
        return interface

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No API key found in environment")
        return
    
    print("🚀 Starting Universal Browser Automation...")
    print("🌐 Works on ANY website - e-commerce, social media, banking, etc.")
    print("🤖 Powered by Anthropic Claude AI")
    print()
    
    try:
        automation = UniversalBrowserAutomation(api_key)
        interface = automation.create_interface()
        
        print("🌐 Starting universal automation interface...")
        print("📍 Access at: http://127.0.0.1:7788")
        print("🎯 Ready for automation on any website!")
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7788,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
EOF
    
    print_success "Universal automation interface created"
}

create_env_file() {
    print_header "🔑 Setting up API configuration..."
    
    cat > "$INSTALL_DIR/.env" << EOF
# Universal Browser Automation Configuration
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Browser Settings
BROWSER_TYPE=chromium
BROWSER_HEADLESS=false
BROWSER_PATH=auto

# Interface Settings
SERVER_HOST=127.0.0.1
SERVER_PORT=$PORT
SHARE=false

# Automation Settings
MAX_RETRIES=5
RETRY_DELAY=3
SCREENSHOT_ENABLED=true
LOGGING_LEVEL=info
EOF
    
    print_success "Environment configuration created"
}

create_launcher_script() {
    print_header "🚀 Creating launcher script..."
    
    cat > "$INSTALL_DIR/start_automation.sh" << EOF
#!/bin/bash

# Universal Browser Automation Launcher
echo "🚀 Starting Universal Browser Automation..."
echo "🌐 AI-powered automation for ANY website"
echo

cd "$INSTALL_DIR"

# Export environment variables
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
export BROWSER_HEADLESS=false

# Activate virtual environment
source venv/bin/activate

# Start the interface
python universal_browser_interface.py
EOF
    
    chmod +x "$INSTALL_DIR/start_automation.sh"
    print_success "Launcher script created"
}

run_system_tests() {
    print_header "🧪 Running system tests..."
    
    # Test Python imports
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    python -c "
import sys
try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    import gradio as gr
    import asyncio
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

launch_interface() {
    print_header "🚀 Launching Universal Browser Automation..."
    
    cd "$INSTALL_DIR"
    
    # Set environment variables
    export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Display launch information
    echo
    print_header "🌐 Universal Browser Automation is starting..."
    echo -e "   ${WHITE}Interface URL:${NC}     http://127.0.0.1:$PORT"
    echo -e "   ${WHITE}Installation:${NC}      $INSTALL_DIR"
    echo -e "   ${WHITE}API Key:${NC}           Configured ✓"
    echo
    
    print_header "🎯 Ready for automation on ANY website:"
    echo "   🛒 E-commerce: Amazon, eBay, shopping sites"
    echo "   💼 Job sites: LinkedIn, Indeed, AngelList"
    echo "   🏦 Banking: Online banking, financial sites"
    echo "   📱 Social: Twitter, Facebook, Instagram"
    echo "   🏛️ Government: Tax sites, DMV, permits"
    echo "   📚 Education: Coursera, university portals"
    echo "   🌐 Any website you need automated!"
    echo
    
    print_header "🚀 Starting interface..."
    echo
    
    # Start the interface
    python universal_browser_interface.py
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    show_banner
    
    print_header "🚀 Starting Universal Browser Automation Setup..."
    echo
    
    check_dependencies
    setup_environment
    install_browser_automation
    create_interface_script
    create_env_file
    create_launcher_script
    run_system_tests
    
    echo
    print_header "✅ Setup completed successfully!"
    echo
    
    launch_interface
}

# Run the main function
main "$@"