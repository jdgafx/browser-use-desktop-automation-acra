#!/bin/bash

# No API Key Browser Automation Setup
# Sets up browser automation options that don't require cloud API keys

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚫 NO API KEY BROWSER AUTOMATION                          ║
║                                                                              ║
║  🎯 Direct Control    📱 Manual Interface    🤖 Local AI (Ollama)           ║
║  🔧 Playwright        🎪 Step-by-step       🏠 Privacy-focused              ║
║                                                                              ║
║                        No Cloud Dependencies Required                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "ubuntu"
        elif command -v yum &> /dev/null; then
            echo "centos"
        elif command -v pacman &> /dev/null; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

install_system_dependencies() {
    local os=$(detect_os)
    print_info "Detected OS: $os"
    
    case $os in
        "ubuntu")
            print_info "Installing system dependencies for Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y wmctrl tesseract-ocr tesseract-ocr-eng curl
            ;;
        "centos")
            print_info "Installing system dependencies for CentOS/RHEL..."
            sudo yum install -y wmctrl tesseract tesseract-langpack-eng curl
            ;;
        "arch")
            print_info "Installing system dependencies for Arch Linux..."
            sudo pacman -S --noconfirm wmctrl tesseract tesseract-data-eng curl
            ;;
        "macos")
            print_info "Installing system dependencies for macOS..."
            if command -v brew &> /dev/null; then
                brew install tesseract curl
                print_info "Window management on macOS uses AppleScript (built-in)"
            else
                print_warning "Homebrew not found. Please install: https://brew.sh/"
            fi
            ;;
        "windows")
            print_warning "Windows detected. Please install manually:"
            print_info "1. Tesseract: https://github.com/UB-Mannheim/tesseract/wiki"
            ;;
        *)
            print_warning "Unknown OS. Please install manually."
            ;;
    esac
}

setup_basic_automation() {
    print_header "🔧 Setting up basic browser automation..."
    
    # Create virtual environment
    python3 -m venv venv-no-api
    source venv-no-api/bin/activate
    
    # Install basic packages
    pip install --upgrade pip
    pip install playwright gradio
    
    # Install Playwright browsers
    playwright install chromium
    
    print_success "Basic automation setup complete"
}

setup_ollama() {
    print_header "🤖 Setting up Ollama (Local AI)..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama already installed"
    else
        print_info "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
    
    # Check if Ollama is running
    if pgrep -x "ollama" > /dev/null; then
        print_success "Ollama is running"
    else
        print_info "Starting Ollama..."
        ollama serve &
        sleep 5
    fi
    
    # Pull a lightweight model
    print_info "Pulling Qwen2.5:7b model (this may take a while)..."
    ollama pull qwen2.5:7b
    
    # Install additional packages for Ollama
    source venv-no-api/bin/activate
    pip install langchain-ollama browser-use
    
    print_success "Ollama setup complete"
}

create_launcher_scripts() {
    print_header "🚀 Creating launcher scripts..."
    
    # Manual controller launcher
    cat > "start_manual_controller.sh" << 'EOF'
#!/bin/bash
echo "🎯 Starting Manual Browser Controller..."
source venv-no-api/bin/activate
python manual-browser-control.py
EOF
    chmod +x start_manual_controller.sh
    
    # Direct Playwright launcher
    cat > "start_direct_automation.sh" << 'EOF'
#!/bin/bash
echo "🔧 Starting Direct Playwright Automation..."
source venv-no-api/bin/activate
python playwright-direct-example.py
EOF
    chmod +x start_direct_automation.sh
    
    # Ollama automation launcher
    cat > "start_ollama_automation.sh" << 'EOF'
#!/bin/bash
echo "🤖 Starting Ollama Browser Automation..."

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

source venv-no-api/bin/activate
python browser-use-with-ollama.py
EOF
    chmod +x start_ollama_automation.sh
    
    print_success "Launcher scripts created"
}

show_usage_instructions() {
    print_header "📖 Usage Instructions"
    
    echo -e "${GREEN}Available automation options:${NC}"
    echo
    echo -e "${CYAN}1. Manual Browser Controller:${NC}"
    echo -e "   ${YELLOW}./start_manual_controller.sh${NC}"
    echo -e "   Step-by-step browser control with web interface"
    echo
    echo -e "${CYAN}2. Direct Playwright Automation:${NC}"
    echo -e "   ${YELLOW}./start_direct_automation.sh${NC}"
    echo -e "   Scripted automation examples"
    echo
    echo -e "${CYAN}3. Local AI with Ollama:${NC}"
    echo -e "   ${YELLOW}./start_ollama_automation.sh${NC}"
    echo -e "   AI-powered automation using local models"
    echo
    echo -e "${GREEN}Files created:${NC}"
    echo -e "   📄 manual-browser-control.py - Manual control interface"
    echo -e "   📄 playwright-direct-example.py - Direct automation examples"
    echo -e "   📄 browser-use-with-ollama.py - Local AI automation"
    echo -e "   📄 BROWSER_AUTOMATION_OPTIONS.md - Complete documentation"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "   1. Choose your preferred automation method"
    echo -e "   2. Run the corresponding launcher script"
    echo -e "   3. Read BROWSER_AUTOMATION_OPTIONS.md for detailed info"
}

# Main execution
main() {
    show_banner
    
    print_header "🚀 Setting up No-API-Key Browser Automation..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.8 or later."
        exit 1
    fi
    
    print_success "Python 3 found: $(python3 --version)"
    
    # Install system dependencies
    install_system_dependencies
    
    # Setup basic automation
    setup_basic_automation
    
    # Ask user about Ollama
    echo
    read -p "Do you want to install Ollama for local AI automation? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_ollama
    else
        print_info "Skipping Ollama installation"
    fi
    
    # Create launcher scripts
    create_launcher_scripts
    
    echo
    print_header "✅ Setup completed successfully!"
    echo
    
    show_usage_instructions
}

# Run the main function
main "$@"
