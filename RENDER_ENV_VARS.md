# 🚀 Render Environment Variables

## Required Environment Variables for Render Deployment

Go to your Render dashboard → Select `seti-backend` service → Environment

Add these environment variables:

### 1. Flask Configuration
```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
```

### 2. Supabase Database
```
DATABASE_URL=postgresql://postgres.dggpnwtrvwcecufhbzog:Seti-backend@aws-1-us-east-1.pooler.supabase.com:6543/postgres
```

### 3. Supabase API
```
SUPABASE_URL=https://dggpnwtrvwcecufhbzog.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnZ3Bud3RydndjZWN1Zmhiem9nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1ODMwMTksImV4cCI6MjA3NjE1OTAxOX0.1rR1NLoJ-XV6Ma4VumFedvKNkTnD8gDvb0CBe8FpeiA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnZ3Bud3RydndjZWN1Zmhiem9nIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDU4MzAxOSwiZXhwIjoyMDc2MTU5MDE5fQ.MWxjAgltsSBRjyswNaOoIhv_bq8AQI2Xl2V1J5hqlLg
```

### 4. Sui Blockchain
```
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
```

### 5. CORS Settings (IMPORTANT!)
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080,https://seti-mvp.vercel.app,https://yourdomain.com
```

**⚠️ CRITICAL:** Add ALL your frontend URLs to CORS_ORIGINS separated by commas:
- Development: `http://localhost:8080`
- Production: Your Vercel/deployed frontend URL

### 6. Server Configuration
```
PORT=10000
HOST=0.0.0.0
```

## 🔄 After Adding Environment Variables

1. Save the environment variables
2. Render will automatically redeploy
3. Wait for deployment to complete (~2-3 minutes)
4. Test: `curl https://seti-backend.onrender.com/health`

## ✅ Verification

After deployment, test CORS:
```bash
curl -I -H "Origin: http://localhost:8080" https://seti-backend.onrender.com/api/v1/markets
```

Should see: `Access-Control-Allow-Origin: http://localhost:8080`


