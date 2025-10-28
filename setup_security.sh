#!/bin/bash
# Security Environment Setup Script for Seti Backend

echo "🔒 Setting up secure environment for Seti Backend..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-$(date +%s)
ADMIN_KEY=admin-secret-key-change-in-production-$(date +%s)

# Database
DATABASE_URL=sqlite:///seti.db

# Supabase (optional)
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=

# Base Blockchain
BASE_NETWORK=sepolia
BASE_RPC_URL=https://base-sepolia.api.onfinality.io/public
PREDICTION_MARKET_CONTRACT_ADDRESS=0x63c0c19a282a1B52b07dD5a65b58948a07DAE32B

# CORS - Development settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# Security Settings
SECURITY_HEADERS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
BLOCK_SUSPICIOUS_REQUESTS=false
CORS_STRICT=false

# External APIs
RAPIDAPI_KEY=

# Server Configuration
PORT=5001
HOST=0.0.0.0
EOF
    echo "✅ .env file created with secure defaults"
else
    echo "⚠️  .env file already exists, skipping creation"
fi

# Generate secure keys if not set
if ! grep -q "SECRET_KEY=.*[0-9]" .env; then
    echo "Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    echo "✅ SECRET_KEY generated"
fi

if ! grep -q "ADMIN_KEY=.*[0-9]" .env; then
    echo "Generating secure ADMIN_KEY..."
    ADMIN_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i.bak "s/ADMIN_KEY=.*/ADMIN_KEY=$ADMIN_KEY/" .env
    echo "✅ ADMIN_KEY generated"
fi

# Clean up backup files
rm -f .env.bak

echo ""
echo "🔐 Security Configuration Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Review and update .env file with your specific settings"
echo "2. For production, set strong SECRET_KEY and ADMIN_KEY"
echo "3. Configure CORS_ORIGINS with your frontend domains"
echo "4. Set up Supabase credentials if using Supabase"
echo "5. Run: python3 run.py"
echo ""
echo "⚠️  Security Notes:"
echo "- Never commit .env file to version control"
echo "- Use strong, unique keys in production"
echo "- Regularly rotate your keys"
echo "- Monitor logs for suspicious activity"
echo ""
echo "🚀 Ready to start the secure backend!"
