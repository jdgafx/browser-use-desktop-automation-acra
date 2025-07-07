#!/bin/bash

echo "🔧 Browser-Use Quick Fix & Start"
echo "================================="

# Check if we have the core installation
if [[ ! -d "$HOME/browser-use-complete" ]]; then
    echo "❌ Core installation not found. Please run the zero-touch setup first."
    exit 1
fi

echo "✅ Core installation found"

# Navigate to the right directory
cd "$HOME/browser-use-complete/web-ui"

# Activate virtual environment
echo "🐍 Activating Python environment..."
source .venv/bin/activate

# Quick test
echo "🧪 Testing browser-use..."
python -c "from browser_use import Agent; print('✅ Browser-use is working!')"

# Install playwright browsers without system dependencies (simpler approach)
echo "🌐 Installing browsers (simplified)..."
playwright install chromium 2>/dev/null || echo "⚠️  Browser installation may need manual setup later"

# Check for API keys
echo "🔑 Checking API configuration..."
if [[ -f ".env" ]]; then
    if grep -q "your_.*_api_key_here" .env; then
        echo "⚠️  API keys not configured yet"
        echo "📝 Edit $HOME/browser-use-complete/web-ui/.env to add your API keys"
    else
        echo "✅ API keys appear to be configured"
    fi
else
    echo "⚠️  No .env file found"
fi

echo ""
echo "🚀 Starting Browser-Use AI Interface..."
echo "📍 Access at: http://127.0.0.1:7788"
echo "💡 Try commands like: 'Go to google.com and search for AI automation'"
echo ""

# Start the simple interface
cd /home/chris/dev/browser-use-desktop-automation
python3 start-simple.py