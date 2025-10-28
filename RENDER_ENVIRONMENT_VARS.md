# Production Deployment Configuration for Render
# This file contains all the necessary settings for deploying Seti Backend to Render

# Environment Variables for Production
# Copy these to your Render environment variables

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key-here-change-this
ADMIN_KEY=your-strong-admin-key-here-change-this

# Database (Supabase)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_REF.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR_REF.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SERVICE_KEY

# Base Blockchain
BASE_NETWORK=sepolia
BASE_RPC_URL=https://base-sepolia.api.onfinality.io/public
PREDICTION_MARKET_CONTRACT_ADDRESS=0x63c0c19a282a1B52b07dD5a65b58948A07DAE32B

# CORS - Production domains
CORS_ORIGINS=https://seti-live.vercel.app,https://seti-mvp.vercel.app,https://seti-backend.onrender.com

# Security Settings
SECURITY_HEADERS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=3600
BLOCK_SUSPICIOUS_REQUESTS=true
CORS_STRICT=true

# External APIs
RAPIDAPI_KEY=your_rapidapi_key_here

# Server Configuration
PORT=5000
HOST=0.0.0.0
