#!/bin/bash

# House Listing Scraper Setup Script
# This script sets up the environment and installs dependencies

echo "🏠 Setting up House Listing Scraper..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Chrome browser not found. Please install Google Chrome for web scraping."
    echo "   Download from: https://www.google.com/chrome/"
else
    echo "✅ Chrome browser found"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📧 Creating .env file for email configuration..."
    cp env_example.txt .env
    echo "✅ .env file created. Please edit it with your email credentials."
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
chmod +x setup.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit config.py to set your desired zip codes and filters"
echo "2. Edit .env file with your email credentials (optional)"
echo "3. Test the scraper: python3 scheduler.py --once"
echo "4. Start the daily scheduler: python3 scheduler.py"
echo ""
echo "For more information, see README.md"
