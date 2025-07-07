#!/bin/bash

# Quick Start Script for Browser-Use AI
# Minimal setup and immediate launch

set -e

echo "🚀 Browser-Use AI Quick Start"
echo "================================"

# Check if we're in the right directory
if [[ ! -f "browser-use-zero-touch-setup.sh" ]]; then
    echo "❌ Please run this from the browser-use-desktop-automation directory"
    exit 1
fi

# Quick dependency check
echo "🔍 Checking dependencies..."

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Basic dependencies found"

# Install browser-use quickly
echo "📦 Installing browser-use..."
pip3 install browser-use gradio speechrecognition pyaudio 2>/dev/null || echo "⚠️  Some packages may need manual installation"

# Install playwright browsers
echo "🌐 Installing browsers..."
python3 -m playwright install chromium --with-deps 2>/dev/null || echo "⚠️  Browser installation may need manual setup"

# Create minimal .env if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "⚙️  Creating basic configuration..."
    cat > .env << 'EOF'
# Add your API keys here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
EOF
    echo "📝 Created .env file - please add your API keys"
fi

# Make scripts executable
chmod +x browser-use-zero-touch-setup.sh
chmod +x enhanced-webui.py

echo ""
echo "🎉 Quick setup complete!"
echo ""
echo "🚀 Choose your startup option:"
echo ""
echo "1. Quick Launch (enhanced web interface):"
echo "   python3 enhanced-webui.py"
echo ""
echo "2. Full Setup (complete installation):"
echo "   ./browser-use-zero-touch-setup.sh"
echo ""
echo "3. Test Command:"
echo "   python3 -c \"from browser_use import Agent; print('✅ Browser-use ready!')\""
echo ""

# Offer immediate launch
read -p "🚀 Launch enhanced web interface now? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "👍 You can launch later with: python3 enhanced-webui.py"
else
    echo "🌐 Starting enhanced web interface..."
    echo "📍 Access at: http://127.0.0.1:7788"
    echo "🎙️  Voice commands will be available once started"
    echo ""
    python3 enhanced-webui.py
fi