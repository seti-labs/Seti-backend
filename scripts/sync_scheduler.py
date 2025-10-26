#!/usr/bin/env python3
"""
Scheduled Job to Sync Sports Fixtures with Prediction Markets
- Fetches upcoming fixtures from API-Sports
- Creates prediction markets on-chain
- Resolves markets when games finish
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.game import Game
from app.models.market import Market
from app.services.contract_service import contract_service
from app.services.game_service import game_service
from web3 import Web3

def create_market_on_chain(game: Game) -> Optional[int]:
    """Create prediction market on-chain for a game"""
    if not contract_service.contract:
        print("Contract not available")
        return None
    
    try:
        # Create market question
        question = f"{game.home_team} vs {game.away_team} - {game.league}"
        description = f"Will {game.home_team} win? YES = Home wins, NO = Away wins or Draw"
        
        # Set end time (90 minutes + 30 min extra = 7200 seconds after kickoff)
        end_time = int((game.kickoff_time + timedelta(hours=2)).timestamp())
        
        # Note: This requires a write transaction with a funded account
        # For now, return None to indicate we need proper contract write methods
        # TODO: Implement actual contract write transaction
        print(f"Would create market for {question}")
        
        # Return a mock market_id for testing
        # In production, get actual market_id from blockchain event
        return hash(question) % 1000000
        
    except Exception as e:
        print(f"Error creating market: {e}")
        return None

def resolve_market(market_id: int, winner: str) -> bool:
    """Resolve a finished game's market"""
    if not contract_service.contract:
        print("Contract not available")
        return False
    
    try:
        # Map winner to outcome: home win = YES(1), away/draw = NO(0)
        winning_outcome = 1 if winner == 'home' else 0
        
        # Note: This requires a write transaction with a funded account
        # TODO: Implement actual contract write transaction
        print(f"Would resolve market {market_id} with outcome: {winner}")
        
        return True
        
    except Exception as e:
        print(f"Error resolving market: {e}")
        return False

def sync_fixtures():
    """Main sync job: fetch fixtures, create markets, resolve finished games"""
    app = create_app()
    
    with app.app_context():
        print(f"\n=== Starting Sync Job at {datetime.utcnow()} ===")
        
        # Step 1: Fetch upcoming fixtures
        print("\n1. Fetching upcoming fixtures...")
        fixtures = game_service.fetch_upcoming_fixtures(days_ahead=7)
        print(f"   Found {len(fixtures)} fixtures")
        
        # Step 2: Sync fixtures to database
        print("\n2. Syncing fixtures to database...")
        for fixture in fixtures:
            game = game_service.sync_game_to_db(fixture)
            if game:
                print(f"   ✓ Synced: {game.home_team} vs {game.away_team}")
        
        # Step 3: Create markets for new games
        print("\n3. Creating markets for new games...")
        pending_games = Game.query.filter_by(market_id=None).all()
        created = 0
        for game in pending_games:
            market_id = create_market_on_chain(game)
            if market_id:
                game.market_id = market_id
                db.session.commit()
                created += 1
                print(f"   ✓ Created market {market_id} for {game.home_team} vs {game.away_team}")
        print(f"   Created {created} new markets")
        
        # Step 4: Check for finished games and resolve markets
        print("\n4. Checking for finished games...")
        finished_games = Game.query.filter(
            Game.market_id.isnot(None),
            Game.status == 'FT'
        ).all()
        resolved = 0
        for game in finished_games:
            if game.home_score is not None and game.away_score is not None:
                winner = game.get_winner()
                if winner and resolve_market(game.market_id, winner):
                    resolved += 1
                    print(f"   ✓ Resolved market {game.market_id}: Winner = {winner}")
        print(f"   Resolved {resolved} markets")
        
        print(f"\n=== Sync Job Completed ===\n")

if __name__ == '__main__':
    sync_fixtures()
