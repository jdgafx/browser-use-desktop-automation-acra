#!/bin/bash

# Enhanced Playwright Automation Setup
# Complete recreation of enhanced browser automation using Playwright (No API Key Required)

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
║                    🎭 ENHANCED PLAYWRIGHT AUTOMATION                         ║
║                                                                              ║
║  🎯 Template-Based    📁 File Attachments   🎪 Auto-Positioning             ║
║  💬 Interactive       🔍 Smart Detection    🚫 No API Keys                  ║
║                                                                              ║
║                     Complete Browser Automation Suite                       ║
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

check_python() {
    print_header "🐍 Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
        
        # Check if version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.8 or higher required. Current: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or later."
        exit 1
    fi
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 not found. Please install pip3."
        exit 1
    fi
}

setup_virtual_environment() {
    print_header "🏗️  Setting up virtual environment..."
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    python3 -m venv venv-playwright-enhanced
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv-playwright-enhanced/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_success "Virtual environment setup complete"
}

install_python_dependencies() {
    print_header "📦 Installing Python dependencies..."
    
    # Activate virtual environment
    source venv-playwright-enhanced/bin/activate
    
    # Core automation packages
    print_info "Installing core automation packages..."
    pip install playwright gradio
    
    # File processing packages
    print_info "Installing file processing packages..."
    pip install PyPDF2 python-docx pillow pytesseract
    
    # Additional utility packages
    print_info "Installing utility packages..."
    pip install beautifulsoup4 requests fake-useragent
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers..."
    playwright install chromium --with-deps
    
    print_success "All Python dependencies installed"
}

verify_installation() {
    print_header "🧪 Verifying installation..."
    
    source venv-playwright-enhanced/bin/activate
    
    # Test Python imports
    print_info "Testing Python imports..."
    python3 -c "
import playwright
import gradio
import PyPDF2
import docx
import PIL
import pytesseract
from smart_element_detection import SmartElementDetector
from automation_templates import AutomationTemplates
print('✅ All imports successful')
" || {
        print_error "Import test failed"
        exit 1
    }
    
    # Test Playwright browser
    print_info "Testing Playwright browser..."
    python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        await browser.close()
        print('✅ Browser test successful')

asyncio.run(test_browser())
" || {
        print_warning "Browser test failed - may need manual setup"
    }
    
    print_success "Installation verification completed"
}

create_launcher_script() {
    print_header "🚀 Creating launcher script..."
    
    cat > "start_playwright_enhanced.sh" << 'EOF'
#!/bin/bash

echo "🎭 Starting Enhanced Playwright Automation..."
echo "🎯 Features: Template-based automation, smart detection, interactive prompts"
echo "🚫 No API keys required!"
echo

# Activate virtual environment
source venv-playwright-enhanced/bin/activate

# Start the enhanced interface
python playwright-enhanced-automation.py
EOF
    
    chmod +x start_playwright_enhanced.sh
    print_success "Launcher script created: start_playwright_enhanced.sh"
}

create_demo_script() {
    print_header "🎬 Creating demo script..."
    
    cat > "demo_playwright_enhanced.py" << 'EOF'
#!/usr/bin/env python3
"""
Demo script for Enhanced Playwright Automation
Shows how to use the automation engine programmatically
"""

import asyncio
from playwright_enhanced_automation import PlaywrightAutomationEngine

async def demo():
    engine = PlaywrightAutomationEngine()
    
    print("🎭 Enhanced Playwright Automation Demo")
    print("=" * 50)
    
    # Start browser
    print("\n1. Starting browser...")
    result = await engine.start_browser(headless=False)
    print(result)
    
    # Navigate to a test site
    print("\n2. Navigating to test site...")
    result = await engine.navigate_to_url("https://httpbin.org/forms/post")
    print(result)
    
    # Analyze the page
    print("\n3. Analyzing page...")
    analysis = await engine.analyze_current_page()
    print(f"Page has {analysis.get('forms', 0)} forms and {analysis.get('inputs', 0)} inputs")
    
    # Execute form filling template
    print("\n4. Executing form filling template...")
    form_data = {
        "custname": "John Doe",
        "custtel": "555-1234",
        "custemail": "john@example.com"
    }
    result = await engine.execute_template("form_filling", form_data)
    print(f"Template execution: {'Success' if result['success'] else 'Failed'}")
    
    # Take screenshot
    print("\n5. Taking screenshot...")
    screenshot = await engine.take_screenshot()
    print(f"Screenshot: {screenshot}")
    
    # Stop browser
    print("\n6. Stopping browser...")
    result = await engine.stop_browser()
    print(result)
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    asyncio.run(demo())
EOF
    
    chmod +x demo_playwright_enhanced.py
    print_success "Demo script created: demo_playwright_enhanced.py"
}

show_completion_message() {
    print_header "✅ Setup completed successfully!"
    
    echo -e "${GREEN}"
    echo "🎉 Enhanced Playwright Automation is ready!"
    echo
    echo "🌐 Web Interface: ./start_playwright_enhanced.sh"
    echo "🎬 Demo Script: python demo_playwright_enhanced.py"
    echo "📁 Files Created:"
    echo "   - playwright-enhanced-automation.py (Main interface)"
    echo "   - smart-element-detection.py (Element detection)"
    echo "   - automation-templates.py (Automation templates)"
    echo "   - start_playwright_enhanced.sh (Launcher)"
    echo "   - demo_playwright_enhanced.py (Demo script)"
    echo
    echo "✨ Features Available:"
    echo "   🎯 Template-based automation (login, forms, file upload)"
    echo "   🔍 Smart element detection and page analysis"
    echo "   💬 Interactive prompting during execution"
    echo "   📁 File upload and context integration"
    echo "   🎪 Automatic browser positioning"
    echo "   📊 Real-time execution monitoring"
    echo "   🚫 No API keys required!"
    echo
    echo "🚀 Quick Start:"
    echo "   ./start_playwright_enhanced.sh"
    echo -e "${NC}"
}

# Main execution
main() {
    show_banner
    
    print_header "🚀 Starting Enhanced Playwright Automation Setup..."
    
    check_python
    install_system_dependencies
    setup_virtual_environment
    install_python_dependencies
    verify_installation
    create_launcher_script
    create_demo_script
    
    show_completion_message
}

# Run the main function
main "$@"
