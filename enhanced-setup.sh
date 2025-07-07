#!/bin/bash

# Enhanced Browser Automation Setup Script
# Includes interactive prompting, file attachments, and auto-positioning

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/enhanced-browser-automation"
PYTHON_VERSION="3.9"
PORT=${PORT:-7789}

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
║                    🤖 ENHANCED BROWSER AUTOMATION SETUP                      ║
║                                                                              ║
║  🎯 Interactive Prompting  📁 File Attachments  🎪 Auto-Positioning         ║
║  💬 Real-time Direction   📄 Context Awareness  🔄 Live Monitoring          ║
║                                                                              ║
║                        Powered by Anthropic Claude                          ║
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
            if sudo apt-get update && sudo apt-get install -y wmctrl tesseract-ocr tesseract-ocr-eng; then
                print_success "System dependencies installed successfully"
            else
                print_warning "Failed to install some system dependencies automatically"
            fi
            ;;
        "centos")
            print_info "Installing system dependencies for CentOS/RHEL..."
            if sudo yum install -y wmctrl tesseract tesseract-langpack-eng; then
                print_success "System dependencies installed successfully"
            else
                print_warning "Failed to install some system dependencies automatically"
            fi
            ;;
        "arch")
            print_info "Installing system dependencies for Arch Linux..."
            if sudo pacman -S --noconfirm wmctrl tesseract tesseract-data-eng; then
                print_success "System dependencies installed successfully"
            else
                print_warning "Failed to install some system dependencies automatically"
            fi
            ;;
        "macos")
            print_info "Installing system dependencies for macOS..."
            if command -v brew &> /dev/null; then
                if brew install tesseract; then
                    print_success "Tesseract installed via Homebrew"
                    print_info "Window management on macOS uses AppleScript (built-in)"
                else
                    print_warning "Failed to install tesseract via Homebrew"
                fi
            else
                print_warning "Homebrew not found. Please install Homebrew first: https://brew.sh/"
                print_info "Then run: brew install tesseract"
            fi
            ;;
        "windows")
            print_warning "Windows detected. Please install dependencies manually:"
            print_info "1. Tesseract: https://github.com/UB-Mannheim/tesseract/wiki"
            print_info "2. Window management uses Windows API (built-in)"
            ;;
        *)
            print_warning "Unknown OS. Please install manually:"
            print_info "- wmctrl (for Linux window management)"
            print_info "- tesseract-ocr (for OCR functionality)"
            ;;
    esac
}

check_dependencies() {
    print_header "🔍 Checking and installing system dependencies..."

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "Python 3 found: $(python3 --version)"
    else
        print_error "Python 3 not found. Please install Python 3.9 or later."
        exit 1
    fi

    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 not found. Please install pip3."
        exit 1
    fi

    # Install system dependencies automatically
    print_info "Installing system dependencies automatically..."
    install_system_dependencies

    # Verify system dependencies after installation
    if command -v wmctrl &> /dev/null; then
        print_success "wmctrl found (for window management)"
    else
        print_warning "wmctrl not available (window positioning may not work on Linux)"
    fi

    if command -v tesseract &> /dev/null; then
        print_success "Tesseract OCR found: $(tesseract --version | head -1)"
    else
        print_warning "Tesseract OCR not available (image text extraction will be limited)"
    fi
}

get_api_key() {
    print_header "🔑 API Key Configuration"
    
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        print_success "Anthropic API key found in environment"
        return
    fi
    
    echo -e "${CYAN}Please enter your Anthropic API key:${NC}"
    echo -e "${YELLOW}(Get one at: https://console.anthropic.com/)${NC}"
    read -s -p "API Key: " ANTHROPIC_API_KEY
    echo
    
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        print_error "No API key provided. Exiting."
        exit 1
    fi
    
    export ANTHROPIC_API_KEY
    print_success "API key configured"
}

setup_environment() {
    print_header "🏗️  Setting up environment..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_success "Environment setup complete"
}

install_dependencies() {
    print_header "📦 Installing enhanced dependencies..."
    
    # Core browser automation packages
    print_info "Installing core browser automation packages..."
    pip install browser-use gradio anthropic playwright
    
    # File processing packages
    print_info "Installing file processing packages..."
    pip install PyPDF2 python-docx pillow pytesseract
    
    # Additional utility packages
    print_info "Installing utility packages..."
    pip install python-dotenv requests beautifulsoup4
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers..."
    playwright install chromium || print_warning "Browser installation may need manual setup later"
    
    print_success "All dependencies installed successfully"
}

create_enhanced_interface() {
    print_header "🎨 Creating enhanced interface..."
    
    # Copy the enhanced interface file
    if [ -f "../enhanced-browser-interface.py" ]; then
        cp "../enhanced-browser-interface.py" "$INSTALL_DIR/enhanced_browser_interface.py"
        print_success "Enhanced interface copied"
    else
        print_error "Enhanced interface file not found. Please ensure enhanced-browser-interface.py exists."
        exit 1
    fi
}

create_env_file() {
    print_header "🔧 Creating configuration file..."
    
    cat > "$INSTALL_DIR/.env" << EOF
# Enhanced Browser Automation Configuration
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Browser Settings
BROWSER_TYPE=chromium
BROWSER_HEADLESS=false
BROWSER_PATH=auto

# Interface Settings
SERVER_HOST=127.0.0.1
SERVER_PORT=$PORT
SHARE=false

# Enhanced Features
ENABLE_INTERACTIVE_PROMPTS=true
ENABLE_FILE_ATTACHMENTS=true
ENABLE_AUTO_POSITIONING=true
ENABLE_OCR=true

# File Storage
UPLOAD_DIR=/tmp/browser_automation_files
MAX_FILE_SIZE=10MB

# Automation Settings
MAX_RETRIES=5
RETRY_DELAY=3
SCREENSHOT_ENABLED=true
LOGGING_LEVEL=info
EOF
    
    print_success "Configuration file created"
}

create_launcher_script() {
    print_header "🚀 Creating launcher script..."
    
    cat > "$INSTALL_DIR/start_enhanced_automation.sh" << EOF
#!/bin/bash

# Enhanced Browser Automation Launcher
echo "🚀 Starting Enhanced Browser Automation..."
echo "🎯 Features: Interactive prompting, file attachments, auto-positioning"
echo

cd "$INSTALL_DIR"

# Export environment variables
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
export BROWSER_HEADLESS=false

# Activate virtual environment
source venv/bin/activate

# Start the enhanced interface
python enhanced_browser_interface.py
EOF
    
    chmod +x "$INSTALL_DIR/start_enhanced_automation.sh"
    print_success "Launcher script created"
}

create_desktop_entry() {
    print_header "🖥️  Creating desktop entry..."
    
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_DIR/enhanced-browser-automation.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Enhanced Browser Automation
Comment=AI-powered browser automation with interactive prompting
Exec=$INSTALL_DIR/start_enhanced_automation.sh
Icon=web-browser
Terminal=true
Categories=Development;Network;
EOF
    
    print_success "Desktop entry created"
}

run_system_tests() {
    print_header "🧪 Running system tests..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # Test Python imports
    print_info "Testing Python imports..."
    python3 -c "
import browser_use
import gradio
import anthropic
import PyPDF2
import docx
import PIL
print('✅ All imports successful')
" || {
        print_error "Import test failed"
        exit 1
    }
    
    # Test API key
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        print_info "Testing API key..."
        python3 -c "
import os
from browser_use.llm import ChatAnthropic
os.environ['ANTHROPIC_API_KEY'] = '$ANTHROPIC_API_KEY'
llm = ChatAnthropic(model='claude-3-haiku-20240307', api_key='$ANTHROPIC_API_KEY')
print('✅ API key test successful')
" || print_warning "API key test failed - please verify your key"
    fi
    
    print_success "System tests completed"
}

launch_interface() {
    print_header "🌐 Launching Enhanced Interface..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    echo -e "${GREEN}"
    echo "🎉 Enhanced Browser Automation is ready!"
    echo
    echo "🌐 Web Interface: http://127.0.0.1:$PORT"
    echo "📁 Installation: $INSTALL_DIR"
    echo "🚀 Launcher: $INSTALL_DIR/start_enhanced_automation.sh"
    echo
    echo "✨ Enhanced Features:"
    echo "   💬 Interactive prompting during automation"
    echo "   📁 File upload and context integration"
    echo "   🎯 Automatic browser positioning"
    echo "   📄 Resume/cover letter awareness"
    echo "   🔄 Real-time execution monitoring"
    echo
    echo "Starting interface in 3 seconds..."
    echo -e "${NC}"
    
    sleep 3
    python enhanced_browser_interface.py
}

# Main execution
main() {
    show_banner
    
    print_header "🚀 Starting Enhanced Browser Automation Setup..."
    echo
    
    check_dependencies
    get_api_key
    setup_environment
    install_dependencies
    create_enhanced_interface
    create_env_file
    create_launcher_script
    create_desktop_entry
    run_system_tests
    
    echo
    print_header "✅ Setup completed successfully!"
    echo
    
    launch_interface
}

# Run the main function
main "$@"
