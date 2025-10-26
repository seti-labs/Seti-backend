# Deployment Checklist

## Environment Variables to Set in Render

### Required for Sports Integration:
```bash
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get your key from: https://rapidapi.com/api-sports/api/api-football

### Existing Variables:
- `DATABASE_URL` - Already set
- `SECRET_KEY` - Already set
- `ETH_RPC_URL` - Already set
- `CONTRACT_ADDRESS` - Already set

## Test the Deployment

1. Check health: https://seti-backend.onrender.com/health
2. List games: https://seti-backend.onrender.com/api/v1/games
3. Manual sync: POST to https://seti-backend.onrender.com/api/v1/games/sync

## Enable Automated Sync

Add to Render's Cron Jobs:
- Command: `python scripts/sync_scheduler.py`
- Schedule: `0 * * * *` (every hour)
