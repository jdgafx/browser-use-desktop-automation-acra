#!/bin/bash

# Simple Universal Web Automation Setup Script
# Sets up the remote agent system based on the PRD requirements

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
    echo "║                    Simple Universal Web Automation Setup                    ║"
    echo "║                   AI that can complete any task on any website              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${CYAN}🎯 Primary Example: 'Log into turing.com with Google, find quizzes, complete all remaining ones'${NC}"
    echo -e "${CYAN}🌐 Universal Support: Works on ANY website with the same pattern${NC}"
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

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Check system dependencies
check_dependencies() {
    print_header "🔍 Checking System Dependencies"
    
    local os=$(detect_os)
    print_status "Detected OS: $os"
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python 3 found: $python_version"
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        print_status "pip3 found"
    else
        print_error "pip3 not found. Please install pip."
        exit 1
    fi
    
    # Check git
    if command_exists git; then
        print_status "Git found"
    else
        print_warning "Git not found. Some features may not work."
    fi
    
    # Install system dependencies based on OS
    case $os in
        "linux")
            print_status "Installing Linux dependencies..."
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python3-dev python3-pip chromium-browser
            elif command_exists yum; then
                sudo yum install -y python3-devel python3-pip chromium
            elif command_exists pacman; then
                sudo pacman -S python python-pip chromium
            fi
            ;;
        "macos")
            print_status "Installing macOS dependencies..."
            if command_exists brew; then
                brew install python3 chromium
            else
                print_warning "Homebrew not found. Please install manually."
            fi
            ;;
        "windows")
            print_status "Windows detected. Please ensure Chrome is installed."
            ;;
    esac
    
    echo
}

# Install Python dependencies
install_python_dependencies() {
    print_header "📦 Installing Python Dependencies"
    
    # Core dependencies
    local core_deps=(
        "playwright>=1.40.0"
        "gradio>=4.0.0"
        "langchain>=0.1.0"
        "langchain-anthropic>=0.1.0"
        "langchain-openai>=0.1.0"
        "langchain-google-genai>=1.0.0"
        "opencv-python>=4.8.0"
        "pillow>=10.0.0"
        "numpy>=1.24.0"
        "asyncio"
        "aiohttp"
        "requests"
    )
    
    print_status "Installing core Python packages..."
    for dep in "${core_deps[@]}"; do
        echo "Installing $dep..."
        pip3 install "$dep" --upgrade
    done
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers..."
    python3 -m playwright install chromium
    python3 -m playwright install-deps
    
    print_status "Python dependencies installed successfully"
    echo
}

# Create configuration files
create_config_files() {
    print_header "⚙️ Creating Configuration Files"
    
    # Create .env file template
    cat > .env << 'EOF'
# Simple Universal Web Automation Configuration
# Add your API keys here

# Anthropic Claude API Key (recommended)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API Key (alternative)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key (alternative)
GOOGLE_API_KEY=your_google_api_key_here

# Browser settings
BROWSER_HEADLESS=false
BROWSER_TIMEOUT=30000

# Logging level
LOG_LEVEL=INFO
EOF
    
    print_status "Created .env configuration file"
    
    # Create requirements.txt
    cat > requirements.txt << 'EOF'
playwright>=1.40.0
gradio>=4.0.0
langchain>=0.1.0
langchain-anthropic>=0.1.0
langchain-openai>=0.1.0
langchain-google-genai>=1.0.0
opencv-python>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
aiohttp
requests
python-dotenv
EOF
    
    print_status "Created requirements.txt"
    echo
}

# Create launcher scripts
create_launcher_scripts() {
    print_header "🚀 Creating Launcher Scripts"
    
    # CLI launcher
    cat > run_cli.sh << 'EOF'
#!/bin/bash
# Simple Universal Web Automation - CLI Launcher

echo "🚀 Simple Universal Web Automation - CLI Mode"
echo "Examples:"
echo "  ./run_cli.sh turing-quizzes"
echo "  ./run_cli.sh 'complete all courses' --site https://coursera.org"
echo

python3 remote_agent.py "$@"
EOF
    chmod +x run_cli.sh
    
    # Web UI launcher
    cat > run_webui.sh << 'EOF'
#!/bin/bash
# Simple Universal Web Automation - Web UI Launcher

echo "🚀 Starting Simple Universal Web Automation Web Interface..."
echo "🌐 Access at: http://127.0.0.1:7790"
echo

python3 remote_agent_webui.py
EOF
    chmod +x run_webui.sh
    
    # Quick start script
    cat > quick_start.sh << 'EOF'
#!/bin/bash
# Quick Start Script

echo "🚀 Simple Universal Web Automation - Quick Start"
echo
echo "Choose an option:"
echo "1) Web Interface (Recommended)"
echo "2) CLI - Turing.com Quizzes"
echo "3) CLI - Universal Automation"
echo

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Starting Web Interface..."
        ./run_webui.sh
        ;;
    2)
        echo "Starting Turing.com automation..."
        ./run_cli.sh turing-quizzes
        ;;
    3)
        read -p "Enter website URL: " site
        read -p "Enter task description: " task
        ./run_cli.sh "$task" --site "$site"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
EOF
    chmod +x quick_start.sh
    
    print_status "Created launcher scripts"
    echo
}

# Run system tests
run_system_tests() {
    print_header "🧪 Running System Tests"
    
    # Test Python imports
    python3 -c "
import sys
try:
    import playwright
    import gradio
    import langchain
    import cv2
    import numpy
    print('✅ All core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    # Test Playwright browser
    python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://example.com')
        title = await page.title()
        await browser.close()
        await playwright.stop()
        print(f'✅ Browser test successful: {title}')
    except Exception as e:
        print(f'❌ Browser test failed: {e}')

asyncio.run(test_browser())
"
    
    print_status "System tests completed"
    echo
}

# Show usage instructions
show_usage() {
    print_header "📖 Usage Instructions"
    
    echo -e "${CYAN}🎯 Turing.com Quiz Automation:${NC}"
    echo "  ./run_cli.sh turing-quizzes"
    echo "  ./run_webui.sh  # Then select Turing.com tab"
    echo
    
    echo -e "${CYAN}🌐 Universal Website Automation:${NC}"
    echo "  ./run_cli.sh 'complete all courses' --site https://coursera.org"
    echo "  ./run_cli.sh 'apply to jobs' --site https://linkedin.com"
    echo "  ./run_webui.sh  # Then use Universal tab"
    echo
    
    echo -e "${CYAN}⚙️ Configuration:${NC}"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY"
    echo "  3. Run ./quick_start.sh for guided setup"
    echo
    
    echo -e "${CYAN}🔑 API Keys:${NC}"
    echo "  • Anthropic: https://console.anthropic.com/"
    echo "  • OpenAI: https://platform.openai.com/api-keys"
    echo "  • Google: https://makersuite.google.com/app/apikey"
    echo
}

# Main execution
main() {
    show_banner
    
    print_header "🚀 Starting Simple Universal Web Automation Setup..."
    echo
    
    check_dependencies
    install_python_dependencies
    create_config_files
    create_launcher_scripts
    run_system_tests
    
    echo
    print_header "✅ Setup completed successfully!"
    echo
    
    show_usage
    
    echo -e "${GREEN}🎉 Simple Universal Web Automation is ready to use!${NC}"
    echo -e "${YELLOW}📝 Don't forget to add your API key to the .env file${NC}"
    echo
}

# Run the main function
main "$@"
