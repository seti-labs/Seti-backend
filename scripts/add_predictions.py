#!/usr/bin/env python
"""Add 10 sample predictions to the database"""

import sys
import os
from datetime import datetime
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Prediction, Market, User

def add_predictions():
    """Add 10 diverse predictions"""
    app = create_app()
    
    with app.app_context():
        print("Adding 10 sample predictions...")
        
        # Get existing markets
        markets = Market.query.all()
        if not markets:
            print("❌ No markets found! Run seed_data.py first.")
            return
        
        print(f"Found {len(markets)} markets")
        
        # Create sample users if they don't exist
        user_addresses = [
            '0x' + '1' * 64,
            '0x' + '2' * 64,
            '0x' + '3' * 64,
            '0x' + '4' * 64,
            '0x' + '5' * 64,
        ]
        
        for address in user_addresses:
            user = User.query.get(address)
            if not user:
                user = User(
                    address=address,
                    username=f'trader{address[2:5]}',
                    bio='Active prediction market trader'
                )
                db.session.add(user)
        
        db.session.commit()
        print(f"Ensured {len(user_addresses)} users exist")
        
        # Create 10 predictions with varied amounts and outcomes
        now = int(datetime.now().timestamp())
        predictions_data = [
            # Bitcoin market predictions
            {
                'tx': '0x' + 'pred001' + '0' * 56,
                'market': markets[0].id,
                'user': user_addresses[0],
                'outcome': 1,  # YES
                'amount': 5000000000,  # 5 SUI
                'timestamp': now - 86400,  # 1 day ago
            },
            {
                'tx': '0x' + 'pred002' + '0' * 56,
                'market': markets[0].id,
                'user': user_addresses[1],
                'outcome': 0,  # NO
                'amount': 3000000000,  # 3 SUI
                'timestamp': now - 82000,
            },
            {
                'tx': '0x' + 'pred003' + '0' * 56,
                'market': markets[0].id,
                'user': user_addresses[2],
                'outcome': 1,  # YES
                'amount': 10000000000,  # 10 SUI
                'timestamp': now - 43200,  # 12 hours ago
            },
            # Tesla market predictions
            {
                'tx': '0x' + 'pred004' + '0' * 56,
                'market': markets[1].id if len(markets) > 1 else markets[0].id,
                'user': user_addresses[0],
                'outcome': 0,  # NO
                'amount': 2000000000,  # 2 SUI
                'timestamp': now - 72000,
            },
            {
                'tx': '0x' + 'pred005' + '0' * 56,
                'market': markets[1].id if len(markets) > 1 else markets[0].id,
                'user': user_addresses[3],
                'outcome': 1,  # YES
                'amount': 7500000000,  # 7.5 SUI
                'timestamp': now - 50000,
            },
            {
                'tx': '0x' + 'pred006' + '0' * 56,
                'market': markets[1].id if len(markets) > 1 else markets[0].id,
                'user': user_addresses[4],
                'outcome': 0,  # NO
                'amount': 4000000000,  # 4 SUI
                'timestamp': now - 36000,  # 10 hours ago
            },
            # Ethereum market predictions (if exists)
            {
                'tx': '0x' + 'pred007' + '0' * 56,
                'market': markets[2].id if len(markets) > 2 else markets[0].id,
                'user': user_addresses[1],
                'outcome': 1,  # YES
                'amount': 15000000000,  # 15 SUI
                'timestamp': now - 25000,
            },
            {
                'tx': '0x' + 'pred008' + '0' * 56,
                'market': markets[2].id if len(markets) > 2 else markets[0].id,
                'user': user_addresses[2],
                'outcome': 1,  # YES
                'amount': 6000000000,  # 6 SUI
                'timestamp': now - 18000,  # 5 hours ago
            },
            # More diverse predictions
            {
                'tx': '0x' + 'pred009' + '0' * 56,
                'market': markets[0].id,
                'user': user_addresses[3],
                'outcome': 1,  # YES
                'amount': 8000000000,  # 8 SUI
                'timestamp': now - 10800,  # 3 hours ago
            },
            {
                'tx': '0x' + 'pred010' + '0' * 56,
                'market': markets[1].id if len(markets) > 1 else markets[0].id,
                'user': user_addresses[4],
                'outcome': 1,  # YES
                'amount': 12000000000,  # 12 SUI
                'timestamp': now - 3600,  # 1 hour ago
            },
        ]
        
        added_count = 0
        for pred_data in predictions_data:
            # Check if prediction already exists
            existing = Prediction.query.filter_by(
                transaction_hash=pred_data['tx']
            ).first()
            
            if existing:
                print(f"⚠️  Prediction {pred_data['tx'][:12]}... already exists, skipping")
                continue
            
            # Create prediction
            prediction = Prediction(
                transaction_hash=pred_data['tx'],
                market_id=pred_data['market'],
                user_address=pred_data['user'],
                outcome=pred_data['outcome'],
                amount=pred_data['amount'],
                price=pred_data['amount'],  # Simplified
                shares=pred_data['amount'],
                timestamp=pred_data['timestamp']
            )
            
            db.session.add(prediction)
            added_count += 1
            
            # Update user stats
            user = User.query.get(pred_data['user'])
            if user:
                user.update_stats()
        
        db.session.commit()
        
        print(f"\n✅ Added {added_count} predictions successfully!")
        
        # Show summary
        total_predictions = Prediction.query.count()
        print(f"📊 Total predictions in database: {total_predictions}")
        
        # Show predictions by market
        for market in markets:
            pred_count = Prediction.query.filter_by(market_id=market.id).count()
            print(f"   - {market.question[:50]}...: {pred_count} predictions")
        
        # Show user stats
        print(f"\n👥 User Stats:")
        for address in user_addresses:
            user = User.query.get(address)
            if user:
                print(f"   - {user.username}: {user.total_predictions} predictions, {user.total_volume / 1000000000:.2f} SUI volume")

if __name__ == '__main__':
    add_predictions()

