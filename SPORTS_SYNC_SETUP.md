# Sports Scores Integration Setup

This system automatically syncs live football scores from API-Sports and creates/resolves prediction markets.

## Architecture

1. **Game Model** (`app/models/game.py`): Stores fixture data linked to prediction markets
2. **GameService** (`app/services/game_service.py`): Fetches fixtures from API-Sports API
3. **Sync Scheduler** (`scripts/sync_scheduler.py`): Coordinates market creation and resolution
4. **Contract Service** (`app/services/contract_service.py`): Handles blockchain interactions

## Environment Variables

Add to your `.env` file:

```bash
# RapidAPI Configuration (Get from https://rapidapi.com/api-sports/api/api-football)
RAPIDAPI_KEY=your_rapidapi_key_here

# Existing contract configuration
ETH_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY
CONTRACT_ADDRESS=0x63c0c19a282a1B52b07dD5a65b58948A07DAE32B
```

## Database Migration

```bash
# Run migration to create games table
flask db migrate -m "Add games table for sports fixtures"
flask db upgrade
```

## Running the Sync Job

### Manual Run
```bash
cd backend
python scripts/sync_scheduler.py
```

### Cron Job (Hourly)
```bash
# Add to crontab
0 * * * * cd /path/to/SetLabs/backend && python scripts/sync_scheduler.py >> /var/log/sync_sports.log 2>&1
```

### Systemd Service
Create `/etc/systemd/system/sports-sync.service`:

```ini
[Unit]
Description=Sports Fixtures Sync Service
After=network.target

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/SetLabs/backend
ExecStart=/usr/bin/python3 scripts/sync_scheduler.py
Environment="RAPIDAPI_KEY=your_key"

[Install]
WantedBy=multi-user.target
```

Then create a timer at `/etc/systemd/system/sports-sync.timer`:

```ini
[Unit]
Description=Run Sports Sync Every Hour
Requires=sports-sync.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
```

Enable with:
```bash
sudo systemctl enable sports-sync.timer
sudo systemctl start sports-sync.timer
```

## How It Works

1. **Fetch Fixtures**: Every hour, fetch upcoming fixtures from supported leagues (Premier League, La Liga, etc.)
2. **Create Markets**: For each new fixture, create a "Will home team win?" market on-chain
3. **Store Mapping**: Link `fixture_id` (from API) to `market_id` (from blockchain) in database
4. **Auto-Resolve**: When a game finishes, automatically resolve the market based on final score

## Supported Leagues

- Premier League (ID: 39)
- La Liga (ID: 140)
- Bundesliga (ID: 78)
- Serie A (ID: 135)
- Ligue 1 (ID: 61)

## Error Handling

- API rate limits: Logged but won't crash
- Missing data: Skips invalid fixtures
- Contract errors: Graceful degradation
- Database errors: Rollback and retry

## TODO

- [ ] Implement actual contract write transactions (requires funded admin wallet)
- [ ] Add more leagues
- [ ] Handle draws separately
- [ ] Add live score updates during games
- [ ] Add notifications for finished games
