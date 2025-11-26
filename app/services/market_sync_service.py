import os
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app import create_app, db
from app.models.market import Market
from app.models.game import Game
from app.services.contract_service import contract_service
# Note: game_service removed - fixture syncing deprecated
# from app.services.game_service import game_service

class MarketSyncService:
    """Background service to continuously fetch and sync markets"""
    
    def __init__(self):
        self.app = create_app()
        self.running = False
        self.sync_thread = None
        self.sync_interval = int(os.getenv('MARKET_SYNC_INTERVAL', 300))  # 5 minutes default
        
    def start(self):
        """Start the background sync service"""
        if self.running:
            print("Market sync service already running")
            return
            
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print(f"Market sync service started (interval: {self.sync_interval}s)")
        
    def stop(self):
        """Stop the background sync service"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join()
        print("Market sync service stopped")
        
    def _sync_loop(self):
        """Main sync loop that runs in background"""
        with self.app.app_context():
            while self.running:
                try:
                    self.sync_markets()
                    self.sync_sports_fixtures()
                    time.sleep(self.sync_interval)
                except Exception as e:
                    print(f"Error in market sync loop: {e}")
                    time.sleep(60)  # Wait 1 minute on error
                    
    def sync_markets(self):
        """Sync prediction markets from blockchain"""
        try:
            print(f"[{datetime.now()}] Syncing markets from blockchain...")
            
            # Fetch all markets from contract
            blockchain_markets = contract_service.fetch_all_markets()
            
            if not blockchain_markets:
                print("No markets found on blockchain")
                return
                
            synced_count = 0
            for market_data in blockchain_markets:
                try:
                    # Check if market already exists
                    existing_market = Market.query.filter_by(id=market_data['id']).first()
                    
                    if existing_market:
                        # Update existing market
                        existing_market.question = market_data['question']
                        existing_market.description = market_data['description']
                        existing_market.end_time = market_data['end_time']
                        existing_market.resolved = market_data['resolved']
                        existing_market.winning_outcome = market_data['winning_outcome']
                        existing_market.total_liquidity = market_data['total_liquidity']
                        existing_market.outcome_a_shares = market_data['outcome_a_shares']
                        existing_market.outcome_b_shares = market_data['outcome_b_shares']
                        existing_market.yes_pool = market_data['yes_pool']
                        existing_market.no_pool = market_data['no_pool']
                        existing_market.creator = market_data['creator']
                        existing_market.updated_at = datetime.utcnow()
                    else:
                        # Create new market
                        new_market = Market(
                            id=market_data['id'],
                            question=market_data['question'],
                            description=market_data['description'],
                            end_time=market_data['end_time'],
                            resolved=market_data['resolved'],
                            winning_outcome=market_data['winning_outcome'],
                            total_liquidity=market_data['total_liquidity'],
                            outcome_a_shares=market_data['outcome_a_shares'],
                            outcome_b_shares=market_data['outcome_b_shares'],
                            yes_pool=market_data['yes_pool'],
                            no_pool=market_data['no_pool'],
                            creator=market_data['creator']
                        )
                        db.session.add(new_market)
                        synced_count += 1
                        
                except Exception as e:
                    print(f"Error syncing market {market_data.get('id', 'unknown')}: {e}")
                    continue
                    
            db.session.commit()
            print(f"Synced {synced_count} new markets, updated existing markets")
            
        except Exception as e:
            print(f"Error syncing markets: {e}")
            db.session.rollback()
            
    def sync_sports_fixtures(self):
        """Sync sports fixtures and create markets - DEPRECATED
        
        Note: Fixture syncing is disabled. The old API (RapidAPI Sportsbook)
        required a paid subscription. Use Polymarket Teams API for team data instead.
        """
        print(f"[{datetime.now()}] Sports fixture syncing is disabled (deprecated API)")
        return
            
    def _create_sports_market(self, game: Game) -> Optional[int]:
        """Create a prediction market for a sports game"""
        try:
            # This would call the smart contract to create a market
            # For now, return a mock ID
            question = f"Will {game.home_team} win against {game.away_team}?"
            description = f"Sports prediction for {game.league} match"
            
            # TODO: Implement actual contract call
            # market_id = contract_service.create_market(question, description, end_time)
            
            # Mock implementation
            market_id = hash(f"{game.fixture_id}_{question}") % 1000000
            
            print(f"Created sports market {market_id} for {game.home_team} vs {game.away_team}")
            return market_id
            
        except Exception as e:
            print(f"Error creating sports market: {e}")
            return None
            
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            'running': self.running,
            'sync_interval': self.sync_interval,
            'thread_alive': self.sync_thread.is_alive() if self.sync_thread else False
        }

# Global instance
market_sync_service = MarketSyncService()
