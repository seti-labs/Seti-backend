#!/usr/bin/env python3
"""
Service to automatically create prediction markets from sports games
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from app import db
from app.models import Game, Market
from app.services.contract_service import contract_service

class MarketCreatorService:
    """Service to create prediction markets from games"""
    
    def __init__(self):
        self.creator_address = os.getenv('MARKET_CREATOR_ADDRESS', '0x0000000000000000000000000000000000000000')
    
    def create_market_for_game(self, game: Game) -> Optional[Market]:
        """
        Create a prediction market for a game
        
        Market Question: "Will [Home Team] beat [Away Team]?"
        - YES: Home team wins
        - NO: Away team wins or Draw
        """
        try:
            # Check if market already exists for this game
            if game.market_id:
                existing_market = Market.query.get(game.market_id)
                if existing_market:
                    return existing_market
            
            # Create market ID
            market_id = f"game_{game.fixture_id}_{int(game.kickoff_time.timestamp())}"
            
            # Check if market with this ID already exists
            existing = Market.query.get(market_id)
            if existing:
                return existing
            
            # Create market question
            question = f"Will {game.home_team} beat {game.away_team}?"
            description = f"{game.home_team} vs {game.away_team} in {game.league}. YES = {game.home_team} wins, NO = {game.away_team} wins or Draw"
            
            # Calculate end time (match + 30 minutes extra for resolution)
            end_time = int((game.kickoff_time + timedelta(hours=2)).timestamp())
            
            # Create new market
            market = Market(
                id=market_id,
                question=question,
                description=description,
                end_time=end_time,
                creator=self.creator_address,
                resolved=False,
                winning_outcome=None,
                total_liquidity=0,
                outcome_a_shares=0,  # YES shares (home wins)
                outcome_b_shares=0,  # NO shares (away wins or draw)
                yes_pool=0,
                no_pool=0,
                volume_24h=0,
                created_timestamp=int(datetime.utcnow().timestamp()),
                category='Sports',
                image_url=None,
                tags=['sports', game.league.lower().replace(' ', '-')],
                indexed_at=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(market)
            db.session.commit()
            
            # Link game to market
            game.market_id = market_id
            db.session.commit()
            
            print(f"Created market {market_id} for {game.home_team} vs {game.away_team}")
            return market
            
        except Exception as e:
            print(f"Error creating market for game {game.fixture_id}: {e}")
            db.session.rollback()
            return None
    
    def create_markets_for_all_games(self):
        """Create markets for all games without markets"""
        games_without_markets = Game.query.filter(
            Game.market_id.is_(None),
            Game.kickoff_time > datetime.utcnow() - timedelta(days=1)  # Only upcoming/recent games
        ).all()
        
        created = 0
        for game in games_without_markets:
            market = self.create_market_for_game(game)
            if market:
                created += 1
        
        return created

market_creator_service = MarketCreatorService()
