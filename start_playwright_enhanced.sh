#!/bin/bash

# Enhanced Playwright Automation Launcher
# Activates virtual environment and starts the Gradio interface

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Header
echo
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🎭 ENHANCED PLAYWRIGHT AUTOMATION                         ║"
echo "║                                                                              ║"
echo "║  🎯 Template-Based    📁 File Attachments   🎪 Auto-Positioning             ║"
echo "║  💬 Interactive       🔍 Smart Detection    🚫 No API Keys                  ║"
echo "║                                                                              ║"
echo "║                     Complete Browser Automation Suite                       ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo

# Check if virtual environment exists
if [ ! -d "venv-playwright-enhanced" ]; then
    print_error "Virtual environment not found. Please run setup-playwright-enhanced.sh first."
    exit 1
fi

# Check if main script exists
if [ ! -f "playwright-enhanced-automation.py" ]; then
    print_error "Main automation script not found. Please ensure all files are in place."
    exit 1
fi

print_info "Starting Enhanced Playwright Automation..."

# Activate virtual environment and start the application
source venv-playwright-enhanced/bin/activate

print_info "Virtual environment activated"
print_info "Starting Gradio interface..."

# Start the application
python playwright-enhanced-automation.py

print_success "Application started successfully!"
print_info "Access the interface at: http://localhost:7861"
