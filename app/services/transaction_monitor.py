"""
Transaction Monitor Service
Monitors blockchain transactions and syncs them to database
"""
import time
import threading
from typing import Dict, List, Optional
from web3 import Web3
from app import db
from app.models import Prediction, Market
from app.services.contract_service import contract_service

class TransactionMonitor:
    """Monitors blockchain transactions for new predictions"""
    
    def __init__(self):
        self.w3 = contract_service.w3
        self.contract = contract_service.contract
        self.is_running = False
        self.monitor_thread = None
        self.last_processed_block = None
        self.processed_transactions = set()
        
    def start_monitoring(self):
        """Start monitoring transactions"""
        if self.is_running:
            print("Transaction monitor already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Transaction monitor started")
    
    def stop_monitoring(self):
        """Stop monitoring transactions"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("Transaction monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                self._process_new_transactions()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Error in transaction monitor loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _process_new_transactions(self):
        """Process new transactions"""
        try:
            # Get latest block number
            latest_block = self.w3.eth.block_number
            
            if self.last_processed_block is None:
                # Start from 10 blocks ago to catch recent transactions
                self.last_processed_block = max(0, latest_block - 10)
            
            # Process blocks from last processed to latest
            for block_num in range(self.last_processed_block + 1, latest_block + 1):
                self._process_block(block_num)
            
            self.last_processed_block = latest_block
            
        except Exception as e:
            print(f"Error processing new transactions: {e}")
    
    def _process_block(self, block_number: int):
        """Process a specific block for relevant transactions"""
        try:
            block = self.w3.eth.get_block(block_number, full_transactions=True)
            
            for tx in block.transactions:
                # Check if transaction is to our contract
                if (tx.to and 
                    tx.to.lower() == self.contract.address.lower() and
                    tx.hash.hex() not in self.processed_transactions):
                    
                    self._process_transaction(tx)
                    self.processed_transactions.add(tx.hash.hex())
            
        except Exception as e:
            print(f"Error processing block {block_number}: {e}")
    
    def _process_transaction(self, tx):
        """Process a specific transaction"""
        try:
            # Decode transaction input to determine function called
            if not tx.input or len(tx.input) < 10:
                return
            
            # Get function selector (first 4 bytes)
            function_selector = tx.input[:10]
            
            # Check if it's a placeBet transaction
            if function_selector == '0x' + 'placeBet'[:8]:  # Simplified check
                self._process_bet_transaction(tx)
            
        except Exception as e:
            print(f"Error processing transaction {tx.hash.hex()}: {e}")
    
    def _process_bet_transaction(self, tx):
        """Process a bet transaction"""
        try:
            # Decode transaction receipt to get events
            receipt = self.w3.eth.get_transaction_receipt(tx.hash)
            
            # Look for BetPlaced event
            for log in receipt.logs:
                if (log.address.lower() == self.contract.address.lower() and
                    len(log.topics) > 0):
                    
                    # Decode the event
                    event_data = self.contract.events.BetPlaced().process_log(log)
                    
                    if event_data:
                        self._sync_bet_from_event(event_data, tx)
            
        except Exception as e:
            print(f"Error processing bet transaction: {e}")
    
    def _sync_bet_from_event(self, event_data, tx):
        """Sync bet data from event to database"""
        try:
            market_id = str(event_data['args']['marketId'])
            user_address = event_data['args']['user']
            outcome = event_data['args']['outcome']
            amount = event_data['args']['amount']
            
            # Check if prediction already exists
            existing_prediction = Prediction.query.filter_by(
                market_id=market_id,
                user_address=user_address
            ).first()
            
            if existing_prediction:
                print(f"Prediction already exists for market {market_id}, user {user_address}")
                return
            
            # Create new prediction
            prediction = Prediction(
                market_id=market_id,
                user_address=user_address,
                outcome=outcome,
                amount=amount,
                timestamp=int(time.time()),
                transaction_hash=tx.hash.hex()
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            print(f"Synced bet: market {market_id}, user {user_address}, amount {amount}")
            
        except Exception as e:
            print(f"Error syncing bet from event: {e}")
            db.session.rollback()
    
    def get_monitoring_stats(self):
        """Get monitoring statistics"""
        return {
            'is_running': self.is_running,
            'last_processed_block': self.last_processed_block,
            'processed_transactions_count': len(self.processed_transactions)
        }

# Global instance
transaction_monitor = TransactionMonitor()
