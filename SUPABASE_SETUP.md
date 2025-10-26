# Supabase Setup Guide

## Issue
The backend is getting database connection errors because Supabase credentials are not configured.

## Solution

### 1. Create `.env` file in `/backend/` directory

Create a file called `.env` in the backend directory with the following content:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Database URL (Supabase provides this)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5001

# CORS Origins (Frontend URLs)
CORS_ORIGINS=http://localhost:5173,http://localhost:8080,http://localhost:8081
```

### 2. Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Go to Settings > API
3. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`
   - **service_role** key → `SUPABASE_SERVICE_KEY`

4. Go to Settings > Database
5. Copy the **Connection string** → `DATABASE_URL`
   - Make sure to replace `[YOUR-PASSWORD]` with your actual database password

### 3. Start the Backend

```bash
cd /Users/mac/Works/SetLabs/backend
python run.py
```

### 4. Verify Connection

The backend should start on `http://localhost:5001` and you should see:
- No more database connection errors
- API endpoints working properly
- Markets and predictions loading correctly

## Alternative: Use Local Database

If you prefer to use a local database instead of Supabase:

1. Install PostgreSQL locally
2. Create a database called `seti`
3. Update `.env` with:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/seti
```

## Current Status

- ✅ Frontend is working with smart contract
- ✅ Wallet connection is working
- ❌ Backend needs Supabase credentials
- ❌ Database connection failing

Once you add the Supabase credentials, everything should work perfectly!
