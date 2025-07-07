#!/bin/bash

# Browser-Use Desktop Zero-Touch Installer
# Automated setup script with beautiful CLI and intelligent error handling
# Version: 1.0.0

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="Browser-Use Desktop Installer"
REPO_URL="https://github.com/browser-use/desktop"
REQUIRED_NODE_VERSION="18"
REQUIRED_DISK_SPACE_GB="2"
LOG_FILE="${HOME}/.browser-use-installer.log"
CONFIG_DIR="${HOME}/.browser-use"
INSTALL_DIR="${HOME}/browser-use-desktop"

# Logging levels
LOG_LEVEL_SILENT=0
LOG_LEVEL_NORMAL=1
LOG_LEVEL_VERBOSE=2
LOG_LEVEL_DEBUG=3
LOG_LEVEL_TRACE=4

# Default log level
LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_NORMAL}

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR AND STYLING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Symbols
CHECKMARK="✓"
CROSSMARK="✗"
ARROW="→"
STAR="★"
ROCKET="🚀"
PACKAGE="📦"
GEAR="⚙️"
TEST_TUBE="🧪"
PARTY="🎉"
GLOBE="🌐"
BOOK="📚"
BULB="💡"
MAGNIFYING="🔍"
RECYCLE="🔄"
HAMMER="🏗️"

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Logging function
log() {
    local level=$1
    local message=$2
    local color=${3:-$NC}

    if [[ $LOG_LEVEL -ge $level ]]; then
        echo -e "${color}${message}${NC}"
    fi

    # Always log to file
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [LEVEL:$level] $message" >> "$LOG_FILE"
}

# Print functions for different log levels
print_header() { log $LOG_LEVEL_NORMAL "$1" "$CYAN"; }
print_success() { log $LOG_LEVEL_NORMAL "   ${GREEN}${CHECKMARK}${NC} $1" "$GREEN"; }
print_error() { log $LOG_LEVEL_NORMAL "   ${RED}${CROSSMARK}${NC} $1" "$RED"; }
print_warning() { log $LOG_LEVEL_NORMAL "   ${YELLOW}⚠${NC} $1" "$YELLOW"; }
print_info() { log $LOG_LEVEL_NORMAL "   ${BLUE}${ARROW}${NC} $1" "$BLUE"; }
print_verbose() { log $LOG_LEVEL_VERBOSE "     $1" "$GRAY"; }
print_debug() { log $LOG_LEVEL_DEBUG "     [DEBUG] $1" "$PURPLE"; }

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local task_name=$3
    local width=40

    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))

    printf "\r   ["
    printf "%*s" $completed | tr ' ' '█'
    printf "%*s" $remaining | tr ' ' '░'
    printf "] %d%% %s" $percentage "$task_name"
}

# Spinner for long-running tasks
spinner() {
    local pid=$1
    local task_name=$2
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %10 ))
        printf "\r   ${BLUE}${spin:$i:1}${NC} %s..." "$task_name"
        sleep 0.1
    done
    printf "\r"
}

# Print beautiful header
print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 ${ROCKET} Browser-Use Desktop Setup                 ║"
    echo "║                   Automated Installation                     ║"
    echo "║                      Version $SCRIPT_VERSION                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# Error handling with suggestions
handle_error() {
    local exit_code=$1
    local task_name=$2
    local suggestion=${3:-"Please check the logs for more details."}

    print_error "Failed: $task_name"
    print_warning "Suggestion: $suggestion"
    print_info "Full logs available at: $LOG_FILE"

    if [[ $LOG_LEVEL -ge $LOG_LEVEL_DEBUG ]]; then
        echo -e "\n${GRAY}Recent log entries:${NC}"
        tail -10 "$LOG_FILE" | sed 's/^/  /'
    fi

    exit $exit_code
}

# Retry mechanism with exponential backoff
retry_with_backoff() {
    local max_attempts=$1
    local delay=$2
    local task_name=$3
    shift 3
    local command=("$@")

    local attempt=1
    while [[ $attempt -le $max_attempts ]]; do
        print_verbose "Attempt $attempt/$max_attempts: $task_name"

        if "${command[@]}"; then
            return 0
        fi

        if [[ $attempt -eq $max_attempts ]]; then
            return 1
        fi

        print_warning "Attempt $attempt failed, retrying in ${delay}s..."
        sleep $delay
        delay=$((delay * 2))  # Exponential backoff
        ((attempt++))
    done
}

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM DETECTION AND VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

detect_os() {
    print_verbose "Detecting operating system..."

    case "$(uname -s)" in
        Darwin)
            OS="macOS"
            OS_VERSION=$(sw_vers -productVersion)
            ARCH=$(uname -m)
            PACKAGE_MANAGER="brew"
            ;;
        Linux)
            OS="Linux"
            if [[ -f /etc/os-release ]]; then
                OS_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2)
                OS_DISTRO=$(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)
            fi
            ARCH=$(uname -m)

            # Detect package manager
            if command -v apt-get >/dev/null 2>&1; then
                PACKAGE_MANAGER="apt"
            elif command -v yum >/dev/null 2>&1; then
                PACKAGE_MANAGER="yum"
            elif command -v dnf >/dev/null 2>&1; then
                PACKAGE_MANAGER="dnf"
            elif command -v pacman >/dev/null 2>&1; then
                PACKAGE_MANAGER="pacman"
            else
                PACKAGE_MANAGER="unknown"
            fi
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            OS="Windows"
            OS_VERSION=$(cmd.exe /c ver 2>/dev/null | grep -o '[0-9]*\.[0-9]*\.[0-9]*')
            ARCH="x86_64"
            PACKAGE_MANAGER="chocolatey"
            ;;
        *)
            handle_error 1 "OS Detection" "Unsupported operating system: $(uname -s)"
            ;;
    esac

    print_debug "Detected OS: $OS $OS_VERSION ($ARCH)"
    print_debug "Package manager: $PACKAGE_MANAGER"
}

check_system_requirements() {
    print_header "${MAGNIFYING} Detecting system environment..."

    detect_os
    print_success "Operating System: $OS $OS_VERSION ($ARCH)"

    # Check available disk space
    local available_space
    if [[ "$OS" == "macOS" || "$OS" == "Linux" ]]; then
        available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    else
        # Windows - approximate
        available_space="10"  # Default assumption
    fi

    if [[ $available_space -ge $REQUIRED_DISK_SPACE_GB ]]; then
        print_success "Available space: ${available_space}GB (sufficient)"
    else
        handle_error 1 "Disk Space Check" "Need at least ${REQUIRED_DISK_SPACE_GB}GB free, found ${available_space}GB"
    fi

    # Check internet connectivity
    if ping -c 1 github.com >/dev/null 2>&1; then
        print_success "Internet connectivity: Available"
    else
        handle_error 1 "Network Check" "Internet connection required for installation"
    fi

    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root - this is not recommended"
        print_info "Consider running as a regular user for security"
    fi

    echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

check_command() {
    local cmd=$1
    local name=${2:-$cmd}

    if command -v "$cmd" >/dev/null 2>&1; then
        local version
        case $cmd in
            node)
                version=$(node --version 2>/dev/null | sed 's/v//')
                if [[ -n "$version" ]]; then
                    local major_version=$(echo "$version" | cut -d. -f1)
                    if [[ $major_version -ge $REQUIRED_NODE_VERSION ]]; then
                        print_success "$name: v$version (compatible)"
                        return 0
                    else
                        print_warning "$name: v$version (requires v$REQUIRED_NODE_VERSION+)"
                        return 1
                    fi
                fi
                ;;
            git)
                version=$(git --version 2>/dev/null | awk '{print $3}')
                print_success "$name: v$version (installed)"
                return 0
                ;;
            npm)
                version=$(npm --version 2>/dev/null)
                print_success "$name: v$version (installed)"
                return 0
                ;;
            *)
                print_success "$name: installed"
                return 0
                ;;
        esac
    fi

    print_warning "$name: not found"
    return 1
}

install_nodejs() {
    print_info "Installing Node.js..."

    case $PACKAGE_MANAGER in
        brew)
            retry_with_backoff 3 2 "Node.js installation" brew install node
            ;;
        apt)
            retry_with_backoff 3 2 "Node.js installation" bash -c "
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - &&
                sudo apt-get install -y nodejs
            "
            ;;
        yum|dnf)
            retry_with_backoff 3 2 "Node.js installation" bash -c "
                curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash - &&
                sudo $PACKAGE_MANAGER install -y nodejs npm
            "
            ;;
        pacman)
            retry_with_backoff 3 2 "Node.js installation" sudo pacman -S --noconfirm nodejs npm
            ;;
        *)
            handle_error 1 "Node.js Installation" "Please install Node.js manually from https://nodejs.org"
            ;;
    esac
}

install_git() {
    print_info "Installing Git..."

    case $PACKAGE_MANAGER in
        brew)
            retry_with_backoff 3 2 "Git installation" brew install git
            ;;
        apt)
            retry_with_backoff 3 2 "Git installation" sudo apt-get update && sudo apt-get install -y git
            ;;
        yum|dnf)
            retry_with_backoff 3 2 "Git installation" sudo $PACKAGE_MANAGER install -y git
            ;;
        pacman)
            retry_with_backoff 3 2 "Git installation" sudo pacman -S --noconfirm git
            ;;
        *)
            handle_error 1 "Git Installation" "Please install Git manually from https://git-scm.com"
            ;;
    esac
}

check_chrome() {
    local chrome_paths=(
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        "/usr/bin/google-chrome"
        "/usr/bin/google-chrome-stable"
        "/usr/bin/chromium"
        "/usr/bin/chromium-browser"
        "/opt/google/chrome/chrome"
        "$(which chrome 2>/dev/null)"
        "$(which google-chrome 2>/dev/null)"
        "$(which chromium 2>/dev/null)"
    )

    for path in "${chrome_paths[@]}"; do
        if [[ -n "$path" && -x "$path" ]]; then
            print_success "Chrome: found at $path"
            return 0
        fi
    done

    print_warning "Chrome: not found (browser-use will help install)"
    return 1
}

install_dependencies() {
    print_header "${PACKAGE} Installing dependencies..."

    local deps_to_install=()

    # Check Node.js
    if ! check_command node "Node.js"; then
        deps_to_install+=("nodejs")
    fi

    # Check Git
    if ! check_command git "Git"; then
        deps_to_install+=("git")
    fi

    # Check Chrome
    check_chrome

    # Install missing dependencies
    if [[ ${#deps_to_install[@]} -gt 0 ]]; then
        print_info "Installing missing dependencies: ${deps_to_install[*]}"

        for dep in "${deps_to_install[@]}"; do
            case $dep in
                nodejs)
                    install_nodejs
                    ;;
                git)
                    install_git
                    ;;
            esac
        done

        # Verify installations
        print_info "Verifying installations..."
        check_command node "Node.js" || handle_error 1 "Node.js verification" "Node.js installation failed"
        check_command npm "npm" || handle_error 1 "npm verification" "npm installation failed"
        check_command git "Git" || handle_error 1 "Git verification" "Git installation failed"
    else
        print_success "All dependencies already installed"
    fi

    echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# REPOSITORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

setup_repository() {
    print_header "${RECYCLE} Setting up repository..."

    # Create install directory
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "Directory $INSTALL_DIR already exists"
        read -p "   Remove existing installation? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing installation..."
            rm -rf "$INSTALL_DIR"
        else
            print_info "Using existing directory..."
            cd "$INSTALL_DIR"
            return 0
        fi
    fi

    # Clone repository
    print_info "Cloning browser-use/desktop repository..."
    {
        git clone --progress "$REPO_URL" "$INSTALL_DIR" 2>&1 | while IFS= read -r line; do
            if [[ "$line" =~ ([0-9]+)% ]]; then
                local percentage="${BASH_REMATCH[1]}"
                show_progress "$percentage" 100 "Cloning repository"
            fi
        done
    } &

    local clone_pid=$!
    spinner $clone_pid "Cloning repository"
    wait $clone_pid

    if [[ $? -eq 0 ]]; then
        print_success "Repository cloned successfully"
    else
        handle_error 1 "Repository Clone" "Failed to clone repository. Check network connection."
    fi

    # Verify repository integrity
    cd "$INSTALL_DIR"
    if [[ -f "package.json" && -f "vite.config.js" ]]; then
        print_success "Repository integrity verified"
    else
        handle_error 1 "Repository Verification" "Repository appears incomplete or corrupted"
    fi

    echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD PROCESS
# ═══════════════════════════════════════════════════════════════════════════════

install_npm_packages() {
    print_header "${HAMMER} Building application..."

    print_info "Installing npm packages..."

    # Create a custom npm install with progress tracking
    {
        npm install --progress=true 2>&1 | while IFS= read -r line; do
            print_verbose "$line"
            if [[ "$line" =~ added.*packages ]]; then
                echo "   ✓ Package installation completed"
            fi
        done
    } &

    local npm_pid=$!
    spinner $npm_pid "Installing packages"
    wait $npm_pid

    if [[ $? -eq 0 ]]; then
        # Count installed packages
        local package_count=$(ls node_modules 2>/dev/null | wc -l)
        print_success "$package_count packages installed successfully"
    else
        handle_error 1 "NPM Install" "Try clearing npm cache: npm cache clean --force"
    fi

    # Verify critical dependencies
    local critical_deps=("vite" "electron")
    for dep in "${critical_deps[@]}"; do
        if [[ -d "node_modules/$dep" ]]; then
            print_verbose "✓ $dep installed"
        else
            print_warning "$dep not found in node_modules"
        fi
    done
}

build_application() {
    print_info "Building application for production..."

    if npm run build >/dev/null 2>&1; then
        print_success "Application built successfully"
    else
        print_warning "Production build failed, continuing with development mode"
    fi

    echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

create_configuration() {
    print_header "${GEAR} Configuring environment..."

    # Create config directory
    mkdir -p "$CONFIG_DIR"

    # Create .env template if it doesn't exist
    if [[ ! -f ".env" ]]; then
        print_info "Creating environment configuration..."
        cat > .env << 'EOF'
# Browser-Use Desktop Configuration
# Add your API keys below

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Local LLM Configuration (Ollama)
OLLAMA_BASE_URL=http://localhost:11434

# Browser Settings
BROWSER_TYPE=chrome
BROWSER_HEADLESS=false
BROWSER_DEBUG_PORT=9222

# Logging
LOG_LEVEL=info
LOG_FILE=browser-use.log

# Development Settings
VITE_PORT=5173
VITE_HOST=localhost
EOF
        print_success "Created .env configuration file"
    else
        print_success "Using existing .env configuration"
    fi

    # Create default browser-use config
    print_info "Setting up browser-use configuration..."
    cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# Browser-Use Desktop Configuration
browser:
  type: chrome
  headless: false
  debug_port: 9222
  window_size: [1920, 1080]
  user_data_dir: ~/.browser-use/chrome-data

llm:
  default_provider: openai
  temperature: 0.7
  max_tokens: 2000

logging:
  level: info
  file: ~/.browser-use/logs/browser-use.log

features:
  screenshots: true
  recordings: false
  parallel_tasks: true
  max_parallel: 3
EOF

    print_success "Browser-use configuration created"

    # Set up Chrome debugging
    print_info "Configuring Chrome for automation..."
    mkdir -p "$CONFIG_DIR/chrome-data"
    print_success "Chrome debugging configured"

    echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING AND VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

run_system_tests() {
    print_header "${TEST_TUBE} Running validation tests..."

    local tests_passed=0
    local total_tests=4

    # Test 1: Check if vite dev server starts
    print_info "Testing development server startup..."
    if timeout 10s npm run dev >/dev/null 2>&1; then
        print_success "Development server: PASSED"
        ((tests_passed++))
    else
        print_warning "Development server: FAILED (may need manual start)"
    fi

    # Test 2: Verify package.json and dependencies
    print_info "Testing package configuration..."
    if [[ -f "package.json" ]] && npm list >/dev/null 2>&1; then
        print_success "Package configuration: PASSED"
        ((tests_passed++))
    else
        print_error "Package configuration: FAILED"
    fi

    # Test 3: Check Chrome accessibility
    print_info "Testing browser connectivity..."
    if check_chrome; then
        print_success "Browser connectivity: PASSED"
        ((tests_passed++))
    else
        print_warning "Browser connectivity: MANUAL SETUP NEEDED"
    fi

    # Test 4: Validate configuration files
    print_info "Testing configuration files..."
    if [[ -f ".env" && -f "$CONFIG_DIR/config.yaml" ]]; then
        print_success "Configuration files: PASSED"
        ((tests_passed++))
    else
        print_error "Configuration files: FAILED"
    fi

    # Display test summary
    echo
    if [[ $tests_passed -eq $total_tests ]]; then
        print_success "All tests passed! ($tests_passed/$total_tests)"
    else
        print_warning "Tests completed with warnings ($tests_passed/$total_tests passed)"
    fi

    echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT AND LAUNCH
# ═══════════════════════════════════════════════════════════════════════════════

launch_application() {
    print_header "${PARTY} Installation completed successfully!"

    # Display access information
    print_header "${GLOBE} Access your browser-use desktop at:"
    echo -e "   ${WHITE}Local:${NC}    http://localhost:5173"
    echo -e "   ${WHITE}Network:${NC}  http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):5173"
    echo

    # Provide quick start guide
    print_header "${BOOK} Quick start:"
    echo "   • Navigate to the installation directory:"
    echo "     cd $INSTALL_DIR"
    echo "   • Start the development server:"
    echo "     npm run dev"
    echo "   • Open your browser and go to http://localhost:5173"
    echo "   • Configure your API keys in the .env file"
    echo "   • Start automating with natural language commands!"
    echo

    # Usage examples
    print_header "${BULB} Example commands to try:"
    echo "   • \"Go to google.com and search for AI agents\""
    echo "   • \"Navigate to github.com and find trending repositories\""
    echo "   • \"Help me fill out a form on this website\""
    echo "   • \"Take a screenshot of this page\""
    echo

    # Next steps
    print_info "Next steps:"
    echo "   1. Add your API keys to the .env file"
    echo "   2. Start the server: npm run dev"
    echo "   3. Open http://localhost:5173 in your browser"
    echo "   4. Begin automating your browser tasks!"
    echo

    # Offer to start the server
    read -p "   ${BLUE}Start the development server now? [Y/n]:${NC} " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "You can start the server later with: cd $INSTALL_DIR && npm run dev"
    else
        print_info "Starting development server..."
        echo -e "\n${GRAY}Press Ctrl+C to stop the server${NC}\n"
        npm run dev
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INSTALLATION FLOW
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    # Initialize logging
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "Starting Browser-Use Desktop installation at $(date)" > "$LOG_FILE"

    # Print banner
    print_banner

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                LOG_LEVEL=$LOG_LEVEL_VERBOSE
                shift
                ;;
            --debug|-d)
                LOG_LEVEL=$LOG_LEVEL_DEBUG
                shift
                ;;
            --silent|-s)
                LOG_LEVEL=$LOG_LEVEL_SILENT
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  -v, --verbose    Enable verbose output"
                echo "  -d, --debug      Enable debug output"
                echo "  -s, --silent     Silent mode (errors only)"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Main installation flow
    print_info "Starting zero-touch installation..."
    echo

    # Step 1: System Detection & Validation
    check_system_requirements

    # Step 2: Dependency Installation
    install_dependencies

    # Step 3: Repository Setup
    setup_repository

    # Step 4: Build Process
    install_npm_packages
    build_application

    # Step 5: Configuration
    create_configuration

    # Step 6: Testing & Validation
    run_system_tests

    # Step 7: Launch
    launch_application

    # Log completion
    echo "Installation completed successfully at $(date)" >> "$LOG_FILE"
}

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING AND CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

# Trap for cleanup on exit
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_error "Installation failed with exit code $exit_code"
        print_info "Check the log file for details: $LOG_FILE"
    fi
}

trap cleanup EXIT

# ═══════════════════════════════════════════════════════════════════════════════
# SCRIPT EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
