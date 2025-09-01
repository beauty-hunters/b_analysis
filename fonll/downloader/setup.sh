#!/bin/bash
# FONLL Automation Setup Script

echo "🚀 Setting up FONLL Web Form Automation..."

# Check Python version
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ Python3 not found. Please install Python 3.7 or higher."
    exit 1
fi
echo "✅ Found Python: $python_version"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install selenium webdriver-manager PyYAML pathlib

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo "✅ Python dependencies installed"

# Check for Chrome/Chromium
echo "🔍 Checking for Chrome browser..."
chrome_found=false

# Check common Chrome/Chromium locations
chrome_paths=(
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium-browser"
    "/usr/bin/chromium"
    "/snap/bin/chromium"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)

for path in "${chrome_paths[@]}"; do
    if [[ -x "$path" ]]; then
        echo "✅ Found Chrome browser: $path"
        chrome_found=true
        break
    fi
done

if [[ "$chrome_found" == false ]]; then
    echo "⚠️  Chrome browser not found in standard locations."
    echo "🔧 Installing Chrome..."
    
    # Detect OS and install Chrome
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            # Ubuntu/Debian
            echo "📥 Installing Chrome on Ubuntu/Debian..."
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
        elif command -v yum >/dev/null 2>&1; then
            # CentOS/RHEL/Fedora
            echo "📥 Installing Chrome on CentOS/RHEL/Fedora..."
            sudo yum install -y wget
            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            sudo yum localinstall -y google-chrome-stable_current_x86_64.rpm
        else
            echo "❌ Unsupported Linux distribution. Please install Chrome manually:"
            echo "   https://www.google.com/chrome/"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            echo "📥 Installing Chrome on macOS with Homebrew..."
            brew install --cask google-chrome
        else
            echo "❌ Homebrew not found. Please install Chrome manually:"
            echo "   https://www.google.com/chrome/"
        fi
    else
        echo "❌ Unsupported OS. Please install Chrome manually:"
        echo "   https://www.google.com/chrome/"
    fi
fi

# Test the setup
echo "🧪 Testing setup..."
python3 -c "
import sys
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    print('✅ All Python packages imported successfully')
    
    # Test ChromeDriver initialization
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.google.com')
    driver.quit()
    print('✅ ChromeDriver test successful')
    
except Exception as e:
    print(f'❌ Setup test failed: {e}')
    sys.exit(1)
"

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Create config: python3 fonll_automation.py --create-config"
    echo "   2. Inspect form:  python3 fonll_automation.py --inspect-form"
    echo "   3. Run automation: python3 fonll_automation.py"
    echo ""
else
    echo "❌ Setup test failed. Please check error messages above."
    exit 1
fi