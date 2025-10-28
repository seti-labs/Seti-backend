#!/bin/bash
# Production Deployment Script for Seti Backend on Render

echo "🚀 Deploying Seti Backend to Production..."

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Error: run.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Make sure to set environment variables in Render dashboard."
fi

echo "✅ Pre-deployment checks passed!"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations (if needed)
echo "🗄️  Running database migrations..."
python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    try:
        db.create_all()
        print('✅ Database tables created/updated successfully')
    except Exception as e:
        print(f'⚠️  Database migration warning: {e}')
"

# Test the application
echo "🧪 Testing application..."
python -c "
from app import create_app
try:
    app = create_app('production')
    print('✅ Application created successfully')
except Exception as e:
    print(f'❌ Application test failed: {e}')
    exit(1)
"

echo "🎉 Deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render"
echo "3. Set the environment variables in Render dashboard"
echo "4. Deploy!"
echo ""
echo "🔗 Render Dashboard: https://dashboard.render.com"
echo "🌐 Your app will be available at: https://seti-backend.onrender.com"
