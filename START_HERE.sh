#!/bin/bash
# Easy setup script for Seti Backend

echo "🚀 Seti Backend Setup"
echo "====================="
echo ""

# Step 1: Create virtual environment
echo "📦 Step 1: Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created!"
echo ""

# Step 2: Activate and setup
echo "📦 Step 2: Setting up Python environment..."
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo ""

# Step 3: Upgrade pip
echo "⬆️  Step 3: Upgrading pip..."
pip install --upgrade pip
echo ""

# Step 4: Install dependencies
echo "📥 Step 4: Installing dependencies (this may take a minute)..."
pip install -r requirements.txt
echo "✅ All dependencies installed!"
echo ""

# Step 5: Create basic .env
if [ ! -f .env ]; then
    echo "📝 Step 5: Creating .env file..."
    cat > .env << 'EOF'
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-later
DATABASE_URL=sqlite:///seti.db
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
CORS_ORIGINS=http://localhost:5173
EOF
    echo "✅ .env file created!"
else
    echo "⚠️  .env file already exists, skipping..."
fi
echo ""

# Step 6: Initialize database
echo "🗄️  Step 6: Initializing database..."
python scripts/init_db.py
echo "✅ Database initialized!"
echo ""

echo "🎉 Setup Complete!"
echo ""
echo "To start the backend:"
echo "  1. source venv/bin/activate"
echo "  2. python run.py"
echo ""
echo "The API will be available at: http://localhost:5000"
echo ""

