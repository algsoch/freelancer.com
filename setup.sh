#!/bin/bash

# AI Bid Writer - Setup Script

echo "🚀 Setting up AI Bid Writer..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Setup Backend
echo ""
echo "📦 Setting up backend..."
cd "$(dirname "$0")"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
echo "✅ Backend dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created - PLEASE CONFIGURE YOUR API KEYS!"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your OpenAI or Anthropic API key"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Setup Frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend dependencies already installed"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI or Anthropic API key"
echo "2. Run './start.sh' to start the application"
echo ""
