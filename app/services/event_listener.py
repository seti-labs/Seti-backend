"""
Smart Contract Event Listener Service
Listens to blockchain events and syncs data to database
"""
import os
import time
import threading
from typing import Dict, List, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from app import db
from app.models import Market, Prediction, User
from app.services.contract_service import contract_service

class EventListener:
    """Listens to smart contract events and syncs to database"""
    
    def __init__(self):
        self.w3 = contract_service.w3
        self.contract = contract_service.contract
        self.is_running = False
        self.sync_thread = None
        self.last_sync_block = None
        
        # Event filters
        self.market_created_filter = None
        self.bet_placed_filter = None
        self.market_resolved_filter = None
        self.payout_claimed_filter = None
        
        self._setup_event_filters()
    
    def _setup_event_filters(self):
        """Setup event filters for listening"""
        if not self.contract:
            print("Contract not available for event listening")
            return
        
        try:
            # Create event filters
            self.market_created_filter = self.contract.events.MarketCreated.create_filter(
                fromBlock='latest'
            )
            self.bet_placed_filter = self.contract.events.BetPlaced.create_filter(
                fromBlock='latest'
            )
            self.market_resolved_filter = self.contract.events.MarketResolved.create_filter(
                fromBlock='latest'
            )
            self.payout_claimed_filter = self.contract.events.PayoutClaimed.create_filter(
                fromBlock='latest'
            )
            
            print("Event filters created successfully")
        except Exception as e:
            print(f"Error setting up event filters: {e}")
    
    def start_listening(self):
        """Start the event listener in a separate thread"""
        if self.is_running:
            print("Event listener already running")
            return
        
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.sync_thread.start()
        print("Event listener started")
    
    def stop_listening(self):
        """Stop the event listener"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("Event listener stopped")
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_running:
            try:
                self._process_events()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in event listener loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _process_events(self):
        """Process all pending events"""
        if not self.contract:
            return
        
        try:
            # Process MarketCreated events
            self._process_market_created_events()
            
            # Process BetPlaced events
            self._process_bet_placed_events()
            
            # Process MarketResolved events
            self._process_market_resolved_events()
            
            # Process PayoutClaimed events
            self._process_payout_claimed_events()
            
        except Exception as e:
            print(f"Error processing events: {e}")
    
    def _process_market_created_events(self):
        """Process MarketCreated events"""
        if not self.market_created_filter:
            return
        
        try:
            events = self.market_created_filter.get_new_entries()
            for event in events:
                self._handle_market_created(event)
        except Exception as e:
            print(f"Error processing MarketCreated events: {e}")
    
    def _process_bet_placed_events(self):
        """Process BetPlaced events"""
        if not self.bet_placed_filter:
            return
        
        try:
            events = self.bet_placed_filter.get_new_entries()
            for event in events:
                self._handle_bet_placed(event)
        except Exception as e:
            print(f"Error processing BetPlaced events: {e}")
    
    def _process_market_resolved_events(self):
        """Process MarketResolved events"""
        if not self.market_resolved_filter:
            return
        
        try:
            events = self.market_resolved_filter.get_new_entries()
            for event in events:
                self._handle_market_resolved(event)
        except Exception as e:
            print(f"Error processing MarketResolved events: {e}")
    
    def _process_payout_claimed_events(self):
        """Process PayoutClaimed events"""
        if not self.payout_claimed_filter:
            return
        
        try:
            events = self.payout_claimed_filter.get_new_entries()
            for event in events:
                self._handle_payout_claimed(event)
        except Exception as e:
            print(f"Error processing PayoutClaimed events: {e}")
    
    def _handle_market_created(self, event):
        """Handle MarketCreated event"""
        try:
            market_id = event['args']['marketId']
            question = event['args']['question']
            end_time = event['args']['endTime']
            creator = event['args']['creator']
            
            # Check if market already exists
            existing_market = Market.query.get(str(market_id))
            if existing_market:
                print(f"Market {market_id} already exists, updating...")
                existing_market.question = question
                existing_market.end_time = end_time
                existing_market.creator = creator
            else:
                # Create new market
                market_data = contract_service.get_market(market_id)
                if market_data:
                    market = Market(**market_data)
                    db.session.add(market)
                    print(f"Created new market {market_id}: {question}")
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error handling MarketCreated event: {e}")
            db.session.rollback()
    
    def _handle_bet_placed(self, event):
        """Handle BetPlaced event"""
        try:
            market_id = event['args']['marketId']
            user_address = event['args']['user']
            outcome = event['args']['outcome']
            amount = event['args']['amount']
            
            # Check if prediction already exists
            existing_prediction = Prediction.query.filter_by(
                market_id=str(market_id),
                user_address=user_address
            ).first()
            
            if existing_prediction:
                print(f"Prediction already exists for market {market_id}, user {user_address}")
                return
            
            # Create new prediction
            prediction = Prediction(
                market_id=str(market_id),
                user_address=user_address,
                outcome=outcome,
                amount=amount,
                timestamp=int(time.time()),
                transaction_hash=event['transactionHash'].hex()
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            print(f"Created prediction for market {market_id}, user {user_address}, amount {amount}")
            
        except Exception as e:
            print(f"Error handling BetPlaced event: {e}")
            db.session.rollback()
    
    def _handle_market_resolved(self, event):
        """Handle MarketResolved event"""
        try:
            market_id = event['args']['marketId']
            winning_outcome = event['args']['winningOutcome']
            
            # Update market
            market = Market.query.get(str(market_id))
            if market:
                market.resolved = True
                market.winning_outcome = winning_outcome
                db.session.commit()
                print(f"Resolved market {market_id} with outcome {winning_outcome}")
            else:
                print(f"Market {market_id} not found in database")
            
        except Exception as e:
            print(f"Error handling MarketResolved event: {e}")
            db.session.rollback()
    
    def _handle_payout_claimed(self, event):
        """Handle PayoutClaimed event"""
        try:
            market_id = event['args']['marketId']
            user_address = event['args']['user']
            payout = event['args']['payout']
            
            # Update prediction
            prediction = Prediction.query.filter_by(
                market_id=str(market_id),
                user_address=user_address
            ).first()
            
            if prediction:
                prediction.claimed = True
                prediction.actual_payout = payout
                db.session.commit()
                print(f"Updated payout claim for market {market_id}, user {user_address}, payout {payout}")
            else:
                print(f"Prediction not found for market {market_id}, user {user_address}")
            
        except Exception as e:
            print(f"Error handling PayoutClaimed event: {e}")
            db.session.rollback()
    
    def manual_sync_all(self):
        """Manually sync all data from blockchain"""
        try:
            print("Starting manual sync of all data...")
            
            # Sync all markets
            markets_data = contract_service.fetch_all_markets()
            synced_markets = 0
            
            for market_data in markets_data:
                market = Market.query.get(market_data['id'])
                if market:
                    # Update existing market
                    for key, value in market_data.items():
                        if hasattr(market, key):
                            setattr(market, key, value)
                else:
                    # Create new market
                    market = Market(**market_data)
                    db.session.add(market)
                
                synced_markets += 1
            
            db.session.commit()
            print(f"Synced {synced_markets} markets")
            
            return {
                'success': True,
                'synced_markets': synced_markets,
                'message': f'Successfully synced {synced_markets} markets'
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in manual sync: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
event_listener = EventListener()
