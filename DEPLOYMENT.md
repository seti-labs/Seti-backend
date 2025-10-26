# Seti Backend Deployment Guide

## Deploy to Render

### Prerequisites
1. GitHub repository with the backend code
2. Render account (free tier available)
3. Supabase project with database

### Step 1: Prepare Repository
1. Push your backend code to GitHub
2. Ensure all dependencies are in `requirements.txt`
3. Verify `render.yaml` configuration

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the backend folder as the root directory
5. Render will automatically detect the `render.yaml` configuration

### Step 3: Environment Variables
Set these environment variables in Render dashboard:

**Required:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key
- `SECRET_KEY`: A secure random string for Flask sessions

**Optional (already set in render.yaml):**
- `CORS_ORIGINS`: "*" (allows all origins)
- `BASE_NETWORK`: "sepolia"
- `BASE_RPC_URL`: "https://base-sepolia.g.alchemy.com/v2/demo"
- `PREDICTION_MARKET_CONTRACT_ADDRESS`: "0x63c0c19a282a1b52b07dd5a65b58948a07dae32b"
- `ENABLE_AUTO_SYNC`: "false"

### Step 4: Database Setup
1. Run database migrations on first deployment
2. The backend will automatically create tables on first run

### Step 5: Update Frontend
Once deployed, update your frontend to use the deployed backend URL:

```typescript
// In your frontend API configuration
const API_BASE_URL = 'https://your-render-app-name.onrender.com'
```

### Health Check
Your deployed backend will be available at:
- `https://your-render-app-name.onrender.com/health`
- `https://your-render-app-name.onrender.com/api/v1/markets`

### Troubleshooting
- Check Render logs for deployment issues
- Ensure all environment variables are set
- Verify Supabase connection
- Check CORS configuration if frontend can't connect

### Free Tier Limitations
- Service sleeps after 15 minutes of inactivity
- Cold start takes ~30 seconds
- 750 hours/month free usage
