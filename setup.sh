#!/bin/bash

echo "🚀 Setting up Seti Backend..."
echo ""

# Check Python version
echo "📍 Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Configure your .env file (copy from .env.supabase.example)"
echo "3. Initialize database: flask db init && flask db migrate && flask db upgrade"
echo "4. Run the server: python run.py"
echo ""

