# 🗄️ Supabase Database Setup Guide

This guide will help you set up Supabase as the database for the Seti backend.

## 📋 Prerequisites

- Supabase account (sign up at https://supabase.com)
- Backend code installed

## 🚀 Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in project details:
   - **Name**: `seti-prediction-markets`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier works for development
4. Click "Create new project"
5. Wait for project to initialize (~2 minutes)

## 🔑 Step 2: Get Supabase Credentials

### Database Connection String

1. In your Supabase project dashboard
2. Go to **Settings** > **Database**
3. Scroll to "Connection string"
4. Select **URI** tab
5. Copy the connection string (it looks like this):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with your actual database password

### API Keys

1. Go to **Settings** > **API**
2. You'll see:
   - **Project URL**: `https://[YOUR-PROJECT-REF].supabase.co`
   - **anon public key**: For client-side use
   - **service_role key**: For server-side use (keep secret!)

## 🔧 Step 3: Configure Backend

Create a `.env` file in the backend directory:

```bash
cd /Users/mac/Works/SetLabs/backend

# Copy the Supabase example
cp .env.supabase.example .env
```

Edit `.env` with your Supabase credentials:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=change-this-to-a-random-string

# Supabase Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Supabase API
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY

# Sui Blockchain Configuration
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Server Configuration
PORT=5000
```

## 🗃️ Step 4: Create Database Tables

### Option A: Using Flask-Migrate (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial tables for markets, users, predictions"

# Apply migration
flask db upgrade
```

### Option B: Using Supabase SQL Editor

1. Go to your Supabase dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New query**
4. Copy and paste the SQL below:

```sql
-- Markets table
CREATE TABLE markets (
    id VARCHAR(66) PRIMARY KEY,
    question VARCHAR(500) NOT NULL,
    description TEXT,
    end_time BIGINT NOT NULL,
    creator VARCHAR(66) NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    winning_outcome INTEGER,
    total_liquidity BIGINT DEFAULT 0,
    outcome_a_shares BIGINT DEFAULT 0,
    outcome_b_shares BIGINT DEFAULT 0,
    volume_24h BIGINT DEFAULT 0,
    created_timestamp BIGINT NOT NULL,
    category VARCHAR(50),
    image_url VARCHAR(500),
    tags JSONB,
    last_updated TIMESTAMP DEFAULT NOW(),
    indexed_at TIMESTAMP DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    address VARCHAR(66) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    total_predictions INTEGER DEFAULT 0,
    total_volume BIGINT DEFAULT 0,
    markets_created INTEGER DEFAULT 0,
    first_seen TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW()
);

-- Predictions table
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE CASCADE,
    user_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    outcome INTEGER NOT NULL CHECK (outcome IN (0, 1)),
    amount BIGINT NOT NULL,
    price BIGINT,
    shares BIGINT,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_markets_category ON markets(category);
CREATE INDEX idx_markets_resolved ON markets(resolved);
CREATE INDEX idx_markets_created_timestamp ON markets(created_timestamp DESC);
CREATE INDEX idx_markets_volume ON markets(volume_24h DESC);
CREATE INDEX idx_predictions_market_id ON predictions(market_id);
CREATE INDEX idx_predictions_user_address ON predictions(user_address);
CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE markets ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now, adjust as needed)
CREATE POLICY "Allow public read access on markets" ON markets FOR SELECT USING (true);
CREATE POLICY "Allow public read access on users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow public read access on predictions" ON predictions FOR SELECT USING (true);

-- For write access, you'll need authenticated policies or use service role key
```

5. Click **Run** to execute

## ✅ Step 5: Verify Setup

```bash
# Test database connection
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('✅ Database connected!')"

# Run the backend
python run.py
```

Test the API:
```bash
curl http://localhost:5000/health
```

## 📊 Step 6: Seed Sample Data (Optional)

```bash
python scripts/seed_data.py
```

## 🎯 Supabase Features

### Realtime Subscriptions

Your backend includes Supabase realtime support. To use it in your frontend:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://YOUR_PROJECT_REF.supabase.co',
  'YOUR_ANON_KEY'
)

// Subscribe to market changes
supabase
  .channel('markets')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'markets' }, 
    payload => console.log('Market changed:', payload)
  )
  .subscribe()
```

### Storage for Images

Create storage buckets for market images and user avatars:

1. Go to **Storage** in Supabase dashboard
2. Click **Create a new bucket**
3. Create buckets:
   - `market-images` (public)
   - `user-avatars` (public)

Upload images using the backend API:
```python
from app.services.supabase_service import SupabaseService

supabase_service = SupabaseService()
image_url = supabase_service.upload_file('market-images', 'btc-market.png', image_data)
```

### Built-in Auth (Optional)

If you want to add authentication:

1. Go to **Authentication** in Supabase dashboard
2. Configure providers (Email, Google, etc.)
3. Use Supabase Auth in your frontend

## 🔒 Security Best Practices

### Row Level Security (RLS)

Update RLS policies for production:

```sql
-- Only allow backend (service role) to write
CREATE POLICY "Backend can insert markets" ON markets 
  FOR INSERT 
  WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users 
  FOR UPDATE 
  USING (auth.uid()::text = address);
```

### Environment Variables

- ✅ Use `.env` for local development
- ✅ Store `SUPABASE_SERVICE_KEY` securely (never commit to git)
- ✅ Use environment variables in production (Vercel, Railway, etc.)

## 📈 Monitoring

### View Logs
1. Go to **Logs** > **Postgres Logs** in Supabase dashboard
2. Monitor queries and errors

### Database Size
1. Go to **Settings** > **Database**
2. Check "Database size" and "Tables" sections

### API Usage
1. Go to **Settings** > **API**
2. Check request counts and quotas

## 🚀 Production Deployment

When deploying to production:

```env
# Production .env
FLASK_ENV=production
DATABASE_URL=postgresql://postgres:PROD_PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_KEY=PROD_ANON_KEY
SUPABASE_SERVICE_KEY=PROD_SERVICE_KEY
SECRET_KEY=use-a-strong-random-secret-key
CORS_ORIGINS=https://yourdomain.com
```

## 🆘 Troubleshooting

### Connection Error
```
Error: could not connect to server
```
**Solution**: Check DATABASE_URL is correct and contains your actual password

### SSL Required
```
Error: SSL connection required
```
**Solution**: Add `?sslmode=require` to your DATABASE_URL

### Permission Denied
```
Error: permission denied for table
```
**Solution**: Check RLS policies or use SUPABASE_SERVICE_KEY for backend operations

### Migration Fails
```
Error: relation already exists
```
**Solution**: Drop tables in Supabase SQL Editor and run migration again

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Flask-SQLAlchemy Docs](https://flask-sqlalchemy.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🎉 You're Ready!

Your Supabase database is now configured and ready to use with the Seti backend!

Next steps:
1. Run the backend: `python run.py`
2. Test the API endpoints
3. Connect your frontend
4. Start building! 🚀

---

Need help? Check the main [README.md](./README.md) or create an issue on GitHub.

