# Quick Start: Sports Integration

## 1. Set Up Environment

Add to `.env`:
```bash
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get your key from: https://rapidapi.com/api-sports/api/api-football

## 2. Test the Integration

```bash
cd backend

# Test API fetch
python -c "from app.services.game_service import game_service; fixtures = game_service.fetch_upcoming_fixtures(); print(f'Found {len(fixtures)} fixtures')"

# Run sync job manually
python scripts/sync_scheduler.py
```

## 3. Use the API

```bash
# Get all games
curl http://localhost:5000/api/v1/games

# Get games by league
curl http://localhost:5000/api/v1/games?league=Premier%20League

# Get live games
curl http://localhost:5000/api/v1/games?status=live

# Manually sync games
curl -X POST http://localhost:5000/api/v1/games/sync
```

## 4. Automatic Sync

Add to crontab (runs every hour):
```bash
0 * * * * cd /path/to/SetLabs/backend && python scripts/sync_scheduler.py
```

## Files Created

- `app/models/game.py` - Game database model
- `app/services/game_service.py` - API integration service  
- `app/api/games.py` - REST API endpoints
- `scripts/sync_scheduler.py` - Automated sync job

## What It Does

1. Fetches upcoming Premier League, La Liga, etc. fixtures
2. Stores them in database with team names, kickoff times
3. Creates "Will home team win?" prediction markets
4. Auto-resolves markets when games finish based on final score
