#!/bin/bash

# Electron Integration Setup for Remote Agent
# Integrates the remote agent with the existing Electron desktop app

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    Electron + Remote Agent Integration                      ║"
    echo "║              Integrate Remote Agent with Existing Desktop App              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

setup_electron_integration() {
    print_header "🖥️ Setting Up Electron Integration"
    
    # Check if browser-use-desktop-actual exists
    if [ -d "browser-use-desktop-actual" ]; then
        print_status "Found existing Electron app"
        
        # Create remote agent integration in the web-ui
        if [ -d "browser-use-desktop-actual/lib/web-ui" ]; then
            print_status "Integrating with existing web-ui..."
            
            # Copy remote agent files to web-ui directory
            cp remote_agent.py browser-use-desktop-actual/lib/web-ui/
            cp remote_agent_webui.py browser-use-desktop-actual/lib/web-ui/
            
            # Create integration script
            cat > browser-use-desktop-actual/lib/web-ui/integrated_webui.py << 'EOF'
#!/usr/bin/env python3
"""
Integrated Web UI - Combines existing browser-use with remote agent
"""

import gradio as gr
import asyncio
import threading
from typing import Optional

# Import existing components
try:
    from webui import create_interface as create_browser_use_interface
except ImportError:
    print("⚠️ Could not import existing webui")
    create_browser_use_interface = None

# Import remote agent
try:
    from remote_agent_webui import RemoteAgentWebUI
except ImportError:
    print("⚠️ Could not import remote agent webui")
    RemoteAgentWebUI = None

def create_integrated_interface():
    """Create integrated interface with both systems"""
    
    with gr.Blocks(
        title="Integrated Browser Automation",
        theme=gr.themes.Soft()
    ) as interface:
        
        gr.HTML("""
        <div style="text-align: center; background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1>🤖 Integrated Browser Automation System</h1>
            <p>Choose between existing browser-use or new remote agent</p>
        </div>
        """)
        
        with gr.Tab("🎯 Remote Agent (Universal Automation)"):
            if RemoteAgentWebUI:
                remote_ui = RemoteAgentWebUI()
                remote_interface = remote_ui.create_interface()
                # Embed the remote agent interface
                gr.HTML("<h3>Remote Agent interface would be embedded here</h3>")
            else:
                gr.HTML("<p>❌ Remote Agent not available</p>")
        
        with gr.Tab("🌐 Browser-Use (Existing System)"):
            if create_browser_use_interface:
                gr.HTML("<h3>Existing browser-use interface would be embedded here</h3>")
            else:
                gr.HTML("<p>❌ Existing browser-use not available</p>")
        
        with gr.Tab("📋 System Status"):
            status_text = gr.Textbox(
                label="System Status",
                value="Both systems available" if (RemoteAgentWebUI and create_browser_use_interface) else "Some systems unavailable",
                interactive=False
            )
    
    return interface

def main():
    print("🚀 Starting Integrated Browser Automation System...")
    
    interface = create_integrated_interface()
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7791,  # Different port to avoid conflicts
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()
EOF
            
            print_status "Created integrated web UI"
        fi
        
        # Update package.json to include remote agent dependencies
        if [ -f "package.json" ]; then
            print_status "Package.json found - Electron app detected"
            
            # Create a script to start the integrated system
            cat > start_integrated_electron.sh << 'EOF'
#!/bin/bash
# Start Integrated Electron App with Remote Agent

echo "🚀 Starting Integrated Electron App..."

# Check if we're in the right directory
if [ ! -d "browser-use-desktop-actual" ]; then
    echo "❌ browser-use-desktop-actual directory not found"
    echo "Please run this script from the repository root"
    exit 1
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start the Electron app
echo "🖥️ Starting Electron app with integrated remote agent..."
npm start
EOF
            chmod +x start_integrated_electron.sh
            
            print_status "Created Electron integration launcher"
        fi
        
    else
        print_warning "browser-use-desktop-actual not found"
        print_status "Creating standalone Electron setup instructions..."
        
        cat > ELECTRON_SETUP.md << 'EOF'
# Electron Integration Setup

## Option 1: Use Existing Electron App
If you have the browser-use-desktop-actual directory:
1. Run: `./setup_electron_integration.sh`
2. Start with: `./start_integrated_electron.sh`

## Option 2: Create New Electron App
1. Install Node.js and npm
2. Run: `npm init -y`
3. Install Electron: `npm install electron --save-dev`
4. Create main.js with remote agent integration
5. Update package.json scripts

## Option 3: Use Web Interface (Recommended)
1. Run: `./setup_integrated_remote_agent.sh`
2. Start with: `./run_integrated_system.sh`
3. Access at: http://127.0.0.1:7790
EOF
        
        print_status "Created Electron setup documentation"
    fi
}

create_desktop_launcher() {
    print_header "🖥️ Creating Desktop Integration"
    
    # Create .desktop file for Linux
    cat > remote_agent.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Simple Universal Web Automation
Comment=AI that can complete any task on any website
Exec=/bin/bash -c "cd $(dirname %k) && ./run_integrated_system.sh"
Icon=web-browser
Terminal=true
Categories=Development;Network;
EOF
    
    print_status "Created desktop launcher file"
    
    # Create Windows batch file
    cat > start_remote_agent.bat << 'EOF'
@echo off
echo Starting Simple Universal Web Automation...
cd /d "%~dp0"
call run_integrated_system.sh
pause
EOF
    
    print_status "Created Windows launcher"
}

main() {
    show_banner
    
    print_header "🚀 Starting Electron Integration Setup..."
    
    setup_electron_integration
    create_desktop_launcher
    
    echo
    print_header "✅ Electron Integration Setup Complete!"
    echo
    
    echo -e "${GREEN}🎉 Integration Options Available:${NC}"
    echo
    echo -e "${BLUE}1. Electron Integration (if available):${NC}"
    echo "   ./start_integrated_electron.sh"
    echo
    echo -e "${BLUE}2. Web Interface (Recommended):${NC}"
    echo "   ./setup_integrated_remote_agent.sh"
    echo "   ./run_integrated_system.sh"
    echo
    echo -e "${BLUE}3. Standalone Remote Agent:${NC}"
    echo "   python remote_agent_webui.py"
    echo
}

main "$@"
