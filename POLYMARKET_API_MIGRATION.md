# Polymarket Teams API - Migration Guide

## Overview

We have migrated from the **RapidAPI Sportsbook API** to the **Polymarket Gamma API** for fetching sports team data. This change eliminates the need for paid API subscriptions and provides better integration with the Polymarket ecosystem.

---

## What Changed?

### ❌ **Removed (Old Implementation)**
- **Service**: `app/services/game_service.py`
- **API**: RapidAPI Sportsbook API (`sportsbook-api2.p.rapidapi.com`)
- **Requirements**: Paid RapidAPI subscription
- **Features**: Game fixtures, live scores, match schedules
- **Limitations**: Expensive, rate-limited, subscription required

### ✅ **Added (New Implementation)**
- **Service**: `app/services/polymarket_teams_service.py`
- **API**: Polymarket Gamma API (`gamma-api.polymarket.com/teams`)
- **Requirements**: None (public API)
- **Features**: Team metadata, league grouping, team colors, logos, records
- **Benefits**: Free, fast, reliable, no authentication needed

---

## New API Endpoints

### Base URL
```
/api/v1/polymarket
```

### 1. Get All Teams
```http
GET /api/v1/polymarket/teams
```

**Query Parameters:**
- `league` (optional): Filter by league code (e.g., `nfl`, `nba`, `mlb`)
- `search` (optional): Search by team name or abbreviation

**Response:**
```json
{
  "success": true,
  "teams": [
    {
      "id": 101095,
      "name": "Valencia",
      "league": "lal",
      "record": "2-4-5",
      "logo": "https://polymarket-upload.s3.us-east-2.amazonaws.com/lal_valencia.png",
      "abbreviation": "val",
      "alias": null,
      "createdAt": "2025-01-21T21:29:24.355969Z",
      "updatedAt": "2025-11-09T19:25:37.20218Z",
      "providerId": 614,
      "color": "#E0C000"
    }
  ],
  "count": 100
}
```

### 2. Get Teams Grouped by League
```http
GET /api/v1/polymarket/teams/by-league
```

**Response:**
```json
{
  "success": true,
  "teams_by_league": {
    "nfl": [...],
    "nba": [...],
    "mlb": [...]
  },
  "league_count": 22
}
```

### 3. Get Leagues Summary
```http
GET /api/v1/polymarket/teams/leagues
```

**Response:**
```json
{
  "success": true,
  "leagues": [
    {
      "league": "lol",
      "league_full_name": "League of Legends",
      "team_count": 22,
      "teams": ["Team A", "Team B", ...]
    }
  ],
  "total_leagues": 22
}
```

### 4. Get Potential Matchups
```http
GET /api/v1/polymarket/teams/matchups/:league
```

**Query Parameters:**
- `limit` (optional): Maximum number of matchups (default: 10)

**Example:**
```http
GET /api/v1/polymarket/teams/matchups/nfl?limit=5
```

**Response:**
```json
{
  "success": true,
  "league": "nfl",
  "matchups": [
    {
      "home_team": {...},
      "away_team": {...},
      "league": "nfl",
      "league_full_name": "National Football League",
      "question": "Will Team A beat Team B?",
      "description": "5-3 vs 4-4 in National Football League"
    }
  ],
  "count": 5
}
```

---

## Python Service API

### Import
```python
from app.services.polymarket_teams_service import polymarket_teams_service
```

### Methods

#### 1. Fetch All Teams
```python
teams = polymarket_teams_service.fetch_teams(league='nfl')
# Returns: List[Dict]
```

#### 2. Get Teams by League
```python
teams_by_league = polymarket_teams_service.get_teams_by_league()
# Returns: Dict[str, List[Dict]]
```

#### 3. Get Leagues Summary
```python
summary = polymarket_teams_service.get_leagues_summary()
# Returns: List[Dict] with league info and team counts
```

#### 4. Search Teams
```python
results = polymarket_teams_service.search_teams('lakers')
# Returns: List[Dict] of matching teams
```

#### 5. Create Potential Matchups
```python
matchups = polymarket_teams_service.create_potential_matchups('nba', limit=10)
# Returns: List[Dict] with matchup data
```

---

## Deprecated Endpoints

The following endpoints are now deprecated:

### ❌ `/api/v1/games/sync` (POST)
**Replacement**: Use `/api/v1/polymarket/teams`

### ❌ `/api/v1/countries` (GET)
**Replacement**: Use `/api/v1/polymarket/teams/leagues`

---

## Migration Examples

### Before (Old API)
```python
from app.services.game_service import game_service

# Fetch fixtures (required paid API key)
fixtures = game_service.fetch_upcoming_fixtures()
```

### After (New API)
```python
from app.services.polymarket_teams_service import polymarket_teams_service

# Fetch teams (no API key needed)
teams = polymarket_teams_service.fetch_teams(league='nfl')

# Create matchups for prediction markets
matchups = polymarket_teams_service.create_potential_matchups('nfl', limit=10)
```

---

## Testing

### Run the test suite:
```bash
cd /Users/mac/Works/SetLabs/backend
source venv/bin/activate
python test_polymarket_api.py
```

### Test individual endpoints with curl:
```bash
# Get all teams
curl http://localhost:5000/api/v1/polymarket/teams

# Filter by league
curl http://localhost:5000/api/v1/polymarket/teams?league=nfl

# Get leagues summary
curl http://localhost:5000/api/v1/polymarket/teams/leagues

# Get matchups
curl http://localhost:5000/api/v1/polymarket/teams/matchups/nba?limit=5

# Search teams
curl http://localhost:5000/api/v1/polymarket/teams?search=lakers
```

---

## Supported Leagues

The Polymarket API supports 20+ leagues including:

| Code | Full Name |
|------|-----------|
| `nfl` | National Football League |
| `nba` | National Basketball Association |
| `mlb` | Major League Baseball |
| `nhl` | National Hockey League |
| `mls` | Major League Soccer |
| `epl` | English Premier League |
| `lal` | La Liga |
| `bun` | Bundesliga |
| `ser` | Serie A |
| `fl1` | Ligue 1 |
| `ucl` | UEFA Champions League |
| `uel` | UEFA Europa League |
| `cfb` | College Football |
| `cbb` | College Basketball |
| `atp` | ATP Tennis |
| `wta` | WTA Tennis |
| `lol` | League of Legends |
| `csgo` | Counter-Strike |
| `dota2` | Dota 2 |
| `mma` | Mixed Martial Arts |

---

## Benefits

### 🆓 **Free & Open**
- No API key required
- No subscription fees
- No rate limits (reasonable use)

### ⚡ **Fast & Reliable**
- Direct access to Polymarket data
- Low latency
- High availability

### 🎯 **Better Integration**
- Native Polymarket ecosystem
- Team metadata optimized for predictions
- Consistent data format

### 🛠️ **Easy to Use**
- Simple REST API
- Clean JSON responses
- Well-documented

---

## Python 3.14 Compatibility

This migration also includes updates for Python 3.14 compatibility:

### Database Driver
- **Old**: `psycopg2-binary==2.9.9` (not Python 3.14 compatible)
- **New**: `psycopg[binary]>=3.1.0` (Python 3.14 compatible)

### SQLAlchemy
- **Old**: `SQLAlchemy==2.0.23`
- **New**: `SQLAlchemy>=2.0.36`

---

## Next Steps

### For Developers
1. Update any frontend code to use new endpoints
2. Remove references to old `/games/sync` endpoint
3. Update documentation and API references
4. Consider integrating Polymarket Builder Program (see below)

### For Production
1. Deploy updated backend with new dependencies
2. Test endpoints thoroughly
3. Monitor API usage and performance
4. Update environment variables (remove `RAPIDAPI_KEY`)

---

## Polymarket Builder Program

Consider integrating with the [Polymarket Builder Program](https://docs.polymarket.com/#builders-program) for additional benefits:

### Benefits
1. **Polygon Relayer Access** - Gasless transactions for users
2. **Trading Attribution** - Get credit for orders from your platform
3. **Builder Leaderboard** - Compete for grants from Polymarket

### Getting Started
- [Builder Keys Documentation](https://docs.polymarket.com/#builder-keys)
- [Order Attribution Guide](https://docs.polymarket.com/#order-attribution)
- [Relayer Client (TypeScript)](https://www.npmjs.com/package/@polymarket/builder-relayer-client)
- [Relayer Client (Python)](https://pypi.org/project/py-builder-relayer-client/)

---

## Support

For issues or questions:
- Check `/backend/test_polymarket_api.py` for examples
- Review Polymarket API docs: https://docs.polymarket.com/
- GitHub Issues: Your repository issues

---

**Last Updated**: November 10, 2025
**Python Version**: 3.14.0
**Compatible**: Yes ✅

