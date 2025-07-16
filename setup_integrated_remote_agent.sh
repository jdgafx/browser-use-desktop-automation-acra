#!/bin/bash

# Integrated Remote Agent Setup Script
# Sets up the remote agent with proper virtual environment and integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║              Integrated Simple Universal Web Automation Setup               ║"
    echo "║                   AI that can complete any task on any website              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${CYAN}🎯 Primary Example: 'Log into turing.com with Google, find quizzes, complete all remaining ones'${NC}"
    echo -e "${CYAN}🌐 Universal Support: Works on ANY website with the same pattern${NC}"
    echo -e "${CYAN}🔧 Integrated with existing browser-use system${NC}"
    echo
}

# Print colored header
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo
}

# Print status message
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Print error message
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup virtual environment
setup_virtual_environment() {
    print_header "🐍 Setting Up Virtual Environment"
    
    # Check if venv already exists
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Remove existing venv and create new one? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            print_status "Removed existing virtual environment"
        else
            print_status "Using existing virtual environment"
        fi
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating new virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "pip upgraded"
    
    echo
}

# Install dependencies
install_dependencies() {
    print_header "📦 Installing Dependencies"
    
    # Ensure we're in virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Virtual environment not activated"
        exit 1
    fi
    
    print_status "Installing core dependencies..."
    
    # Core dependencies for remote agent
    pip install playwright>=1.40.0
    pip install gradio>=4.0.0
    pip install langchain>=0.1.0
    pip install langchain-anthropic>=0.1.0
    pip install langchain-openai>=0.1.0
    pip install langchain-google-genai>=1.0.0
    pip install opencv-python>=4.8.0
    pip install pillow>=10.0.0
    pip install numpy>=1.24.0
    pip install aiohttp
    pip install requests
    pip install python-dotenv
    
    # Install existing browser-use dependencies if requirements exist
    if [ -f "requirements.txt" ]; then
        print_status "Installing existing requirements..."
        pip install -r requirements.txt
    fi
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers..."
    python -m playwright install chromium
    python -m playwright install-deps
    
    print_status "Dependencies installed successfully"
    echo
}

# Create integrated configuration
create_integrated_config() {
    print_header "⚙️ Creating Integrated Configuration"
    
    # Create comprehensive .env file
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Integrated Simple Universal Web Automation Configuration

# AI Provider API Keys (choose one or more)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# DeepSeek API (for existing system compatibility)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Browser settings
BROWSER_HEADLESS=false
BROWSER_TIMEOUT=30000

# Remote Agent settings
REMOTE_AGENT_PORT=7790
REMOTE_AGENT_HOST=127.0.0.1

# Existing system settings
WEBUI_PORT=7788
WEBUI_HOST=127.0.0.1

# Logging
LOG_LEVEL=INFO
EOF
        print_status "Created integrated .env configuration"
    else
        print_warning ".env file already exists - not overwriting"
    fi
    
    # Create launcher script for integrated system
    cat > run_integrated_system.sh << 'EOF'
#!/bin/bash
# Integrated System Launcher

echo "🚀 Integrated Simple Universal Web Automation System"
echo "Choose your interface:"
echo
echo "1) Remote Agent Web UI (New - Universal Automation)"
echo "2) Enhanced Web UI (Existing - Browser-Use)"
echo "3) Remote Agent CLI (New - Command Line)"
echo "4) Quick Start Menu (Existing)"
echo

read -p "Enter choice (1-4): " choice

# Activate virtual environment
source venv/bin/activate

case $choice in
    1)
        echo "🌐 Starting Remote Agent Web UI..."
        echo "📍 Access at: http://127.0.0.1:7790"
        python remote_agent_webui.py
        ;;
    2)
        echo "🌐 Starting Enhanced Web UI..."
        echo "📍 Access at: http://127.0.0.1:7788"
        python enhanced-webui.py
        ;;
    3)
        echo "💻 Remote Agent CLI Mode"
        echo "Examples:"
        echo "  python remote_agent.py turing-quizzes"
        echo "  python remote_agent.py 'complete courses' --site https://coursera.org"
        echo
        read -p "Enter command: " cmd
        python remote_agent.py $cmd
        ;;
    4)
        echo "🚀 Starting Quick Start Menu..."
        ./quick-start.sh
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
EOF
    chmod +x run_integrated_system.sh
    
    print_status "Created integrated launcher script"
    echo
}

# Create activation script
create_activation_script() {
    print_header "🔧 Creating Activation Scripts"
    
    # Create activation script
    cat > activate_remote_agent.sh << 'EOF'
#!/bin/bash
# Activate Remote Agent Environment

echo "🐍 Activating Remote Agent Virtual Environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "🎯 Available commands:"
echo "  python remote_agent.py turing-quizzes"
echo "  python remote_agent_webui.py"
echo "  ./run_integrated_system.sh"
echo

# Keep shell open in activated environment
exec bash
EOF
    chmod +x activate_remote_agent.sh
    
    # Create quick test script
    cat > test_integrated_system.py << 'EOF'
#!/usr/bin/env python3
"""Quick test for integrated system"""

def test_imports():
    try:
        import playwright
        print("✅ Playwright available")
    except ImportError:
        print("❌ Playwright not available")
        return False
    
    try:
        import gradio
        print("✅ Gradio available")
    except ImportError:
        print("❌ Gradio not available")
        return False
    
    try:
        from remote_agent import UniversalWebAutomationAgent
        print("✅ Remote Agent available")
    except ImportError:
        print("❌ Remote Agent not available")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Integrated System...")
    if test_imports():
        print("🎉 All systems ready!")
    else:
        print("⚠️ Some components need attention")
EOF
    
    print_status "Created activation and test scripts"
    echo
}

# Run system tests
run_integrated_tests() {
    print_header "🧪 Running Integrated System Tests"
    
    # Test virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Virtual environment not activated"
        return 1
    fi
    
    print_status "Virtual environment: $VIRTUAL_ENV"
    
    # Test Python imports
    python test_integrated_system.py
    
    # Test remote agent verification
    if [ -f "verify_implementation.py" ]; then
        print_status "Running remote agent verification..."
        python verify_implementation.py
    fi
    
    print_status "Integrated system tests completed"
    echo
}

# Show usage instructions
show_integrated_usage() {
    print_header "📖 Integrated System Usage"
    
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo "  ./run_integrated_system.sh"
    echo
    
    echo -e "${CYAN}🎯 Remote Agent (New):${NC}"
    echo "  source venv/bin/activate"
    echo "  python remote_agent.py turing-quizzes"
    echo "  python remote_agent_webui.py"
    echo
    
    echo -e "${CYAN}🌐 Existing System:${NC}"
    echo "  source venv/bin/activate"
    echo "  python enhanced-webui.py"
    echo "  ./quick-start.sh"
    echo
    
    echo -e "${CYAN}⚙️ Configuration:${NC}"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Choose ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY"
    echo "  3. Run ./activate_remote_agent.sh for persistent activation"
    echo
    
    echo -e "${CYAN}🔑 Get API Keys:${NC}"
    echo "  • Anthropic: https://console.anthropic.com/"
    echo "  • OpenAI: https://platform.openai.com/api-keys"
    echo "  • Google: https://makersuite.google.com/app/apikey"
    echo
}

# Main execution
main() {
    show_banner
    
    print_header "🚀 Starting Integrated Remote Agent Setup..."
    echo
    
    setup_virtual_environment
    install_dependencies
    create_integrated_config
    create_activation_script
    run_integrated_tests
    
    echo
    print_header "✅ Integrated Setup Completed Successfully!"
    echo
    
    show_integrated_usage
    
    echo -e "${GREEN}🎉 Integrated Simple Universal Web Automation is ready!${NC}"
    echo -e "${YELLOW}📝 Don't forget to add your API key to the .env file${NC}"
    echo -e "${CYAN}🚀 Run: ./run_integrated_system.sh to get started${NC}"
    echo
}

# Run the main function
main "$@"
