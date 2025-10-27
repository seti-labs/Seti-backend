# Display Markets in Frontend

## Current Status
- ✅ Games table created in database
- ✅ API endpoints working
- ⚠️ Backend needs to be restarted

## What You Need to Do

### Step 1: Restart the Backend
```bash
cd /Users/mac/Works/SetLabs/backend
# Kill any existing processes
lsof -ti :5001 | xargs kill -9

# Start the backend
python3 run.py
```

### Step 2: Verify Markets are Loading
The frontend should automatically fetch markets from:
- `/api/v1/markets` - All prediction markets
- `/api/v1/games` - Sports fixtures

### Step 3: Check Frontend
Open your browser to: `http://localhost:8080`

The markets should display including:
1. **Existing markets** from the database
2. **Sports markets** (once RapidAPI is fixed)

## Available Markets Endpoints

### Get All Markets
```bash
curl 'http://localhost:5001/api/v1/markets'
```

### Get Active Markets
```bash
curl 'http://localhost:5001/api/v1/markets?resolved=false'
```

### Get Sports Fixtures
```bash
curl 'http://localhost:5001/api/v1/games'
```

## Frontend Components

The frontend already has components to display markets:
- `src/pages/Index.tsx` - Main marketplace
- `src/components/MarketCard.tsx` - Individual market card
- `src/hooks/useMarkets.ts` - Market data fetching

## Expected Result

You should see:
1. All existing prediction markets from your database
2. Sports fixtures (when RapidAPI key issue is resolved)
3. Market cards with:
   - Question/title
   - Prediction options (Yes/No)
   - Total liquidity
   - Time remaining
   - Creator info

## Troubleshooting

If markets don't show:
1. Check browser console for errors
2. Verify backend is running: `curl http://localhost:5001/health`
3. Check API response: `curl http://localhost:5001/api/v1/markets`
4. Ensure CORS is configured correctly (already done)

## Next Steps

Once backend is running and markets display:
1. Fix RapidAPI key to show sports data
2. Test market creation
3. Test predictions
4. Verify smart contract integration
