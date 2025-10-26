"""
Background Sync Scheduler
Periodically syncs data between smart contract and database
"""
import time
import threading
from datetime import datetime, timedelta
from app import db, cache
from app.models import Market, Prediction
from app.services.contract_service import contract_service
from app.services.event_listener import event_listener

class SyncScheduler:
    """Schedules periodic sync operations"""
    
    def __init__(self):
        self.is_running = False
        self.sync_thread = None
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync_duration': 0
        }
    
    def start(self):
        """Start the sync scheduler"""
        if self.is_running:
            print("Sync scheduler already running")
            return
        
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("Sync scheduler started")
    
    def stop(self):
        """Stop the sync scheduler"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=10)
        print("Sync scheduler stopped")
    
    def _sync_loop(self):
        """Main sync loop"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Perform sync operations
                self._sync_markets()
                self._sync_predictions()
                self._cleanup_old_data()
                
                # Update stats
                duration = time.time() - start_time
                self.sync_stats['total_syncs'] += 1
                self.sync_stats['successful_syncs'] += 1
                self.sync_stats['last_sync_duration'] = duration
                self.last_sync_time = datetime.utcnow()
                
                print(f"Sync completed in {duration:.2f} seconds")
                
                # Wait for next sync
                time.sleep(self.sync_interval)
                
            except Exception as e:
                print(f"Error in sync loop: {e}")
                self.sync_stats['failed_syncs'] += 1
                time.sleep(60)  # Wait 1 minute on error
    
    def _sync_markets(self):
        """Sync markets from blockchain to database"""
        try:
            # Get all markets from blockchain
            blockchain_markets = contract_service.fetch_all_markets()
            
            for market_data in blockchain_markets:
                market_id = market_data['id']
                
                # Check if market exists in database
                db_market = Market.query.get(market_id)
                
                if db_market:
                    # Update existing market
                    updated = False
                    for key, value in market_data.items():
                        if hasattr(db_market, key) and getattr(db_market, key) != value:
                            setattr(db_market, key, value)
                            updated = True
                    
                    if updated:
                        print(f"Updated market {market_id}")
                else:
                    # Create new market
                    new_market = Market(**market_data)
                    db.session.add(new_market)
                    print(f"Created new market {market_id}: {market_data.get('question', 'Unknown')}")
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error syncing markets: {e}")
            db.session.rollback()
    
    def _sync_predictions(self):
        """Sync predictions from blockchain to database"""
        try:
            # Get all markets to check for predictions
            markets = Market.query.all()
            
            for market in markets:
                market_id = int(market.id)
                
                # Get all predictions for this market from blockchain
                # Note: This is a simplified approach - in production you'd want to track
                # which addresses have placed bets more efficiently
                
                # For now, we'll rely on the event listener to catch new predictions
                # This method can be enhanced to do bulk syncs if needed
                pass
            
        except Exception as e:
            print(f"Error syncing predictions: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old or invalid data"""
        try:
            # Remove markets that don't exist on blockchain anymore
            blockchain_markets = contract_service.fetch_all_markets()
            blockchain_market_ids = {str(m['id']) for m in blockchain_markets}
            
            # Find markets in DB that don't exist on blockchain
            db_markets = Market.query.all()
            for db_market in db_markets:
                if db_market.id not in blockchain_market_ids:
                    print(f"Removing orphaned market {db_market.id}")
                    db.session.delete(db_market)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error cleaning up data: {e}")
            db.session.rollback()
    
    def force_sync(self):
        """Force an immediate sync"""
        try:
            print("Starting forced sync...")
            start_time = time.time()
            
            # Use the event listener's manual sync
            result = event_listener.manual_sync_all()
            
            duration = time.time() - start_time
            self.sync_stats['last_sync_duration'] = duration
            self.last_sync_time = datetime.utcnow()
            
            if result['success']:
                self.sync_stats['successful_syncs'] += 1
                print(f"Forced sync completed successfully in {duration:.2f} seconds")
            else:
                self.sync_stats['failed_syncs'] += 1
                print(f"Forced sync failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"Error in forced sync: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_stats(self):
        """Get sync statistics"""
        return {
            'is_running': self.is_running,
            'sync_interval': self.sync_interval,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'stats': self.sync_stats
        }
    
    def set_sync_interval(self, interval_seconds):
        """Set the sync interval"""
        if interval_seconds < 60:  # Minimum 1 minute
            raise ValueError("Sync interval must be at least 60 seconds")
        
        self.sync_interval = interval_seconds
        print(f"Sync interval set to {interval_seconds} seconds")

# Global instance
sync_scheduler = SyncScheduler()
