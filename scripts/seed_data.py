#!/usr/bin/env python
"""Seed database with sample data for testing"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Market, Prediction, User

def seed_database():
    """Seed database with sample data"""
    app = create_app()
    
    with app.app_context():
        print("Seeding database with sample data...")
        
        # Create sample users
        users = [
            User(
                address='0x' + '1' * 64,
                username='alice',
                email='alice@example.com',
                bio='Crypto enthusiast'
            ),
            User(
                address='0x' + '2' * 64,
                username='bob',
                email='bob@example.com',
                bio='Market trader'
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        # Create sample markets
        now = int(datetime.now().timestamp())
        future = int((datetime.now() + timedelta(days=30)).timestamp())
        
        markets = [
            Market(
                id='0x' + 'a' * 64,
                question='Will Bitcoin reach $100k by end of 2025?',
                description='This market resolves YES if Bitcoin (BTC) reaches $100,000 USD on any major exchange by December 31, 2025.',
                end_time=future,
                creator='0x' + '1' * 64,
                resolved=False,
                total_liquidity=10000000000,
                outcome_a_shares=5000000000,
                outcome_b_shares=5000000000,
                volume_24h=1000000000,
                created_timestamp=now,
                category='Crypto',
                image_url='https://example.com/btc.png',
                tags=['bitcoin', 'crypto', 'price']
            ),
            Market(
                id='0x' + 'b' * 64,
                question='Will Ethereum complete the merge successfully?',
                description='This market resolves YES if Ethereum successfully transitions to proof-of-stake.',
                end_time=future,
                creator='0x' + '2' * 64,
                resolved=True,
                winning_outcome=1,
                total_liquidity=5000000000,
                outcome_a_shares=2000000000,
                outcome_b_shares=3000000000,
                volume_24h=500000000,
                created_timestamp=now - 86400,
                category='Crypto',
                image_url='https://example.com/eth.png',
                tags=['ethereum', 'merge', 'pos']
            ),
            Market(
                id='0x' + 'c' * 64,
                question='Will Tesla stock reach $300 in 2025?',
                description='This market resolves YES if Tesla (TSLA) stock reaches $300 per share on any trading day in 2025.',
                end_time=future,
                creator='0x' + '1' * 64,
                resolved=False,
                total_liquidity=8000000000,
                outcome_a_shares=4500000000,
                outcome_b_shares=3500000000,
                volume_24h=800000000,
                created_timestamp=now,
                category='Stocks',
                image_url='https://example.com/tsla.png',
                tags=['tesla', 'stocks', 'price']
            )
        ]
        
        for market in markets:
            db.session.add(market)
        
        # Create sample predictions
        predictions = [
            Prediction(
                transaction_hash='0x' + 'tx1' + '0' * 60,
                market_id='0x' + 'a' * 64,
                user_address='0x' + '1' * 64,
                outcome=1,
                amount=1000000000,
                price=550000000,
                shares=500000000,
                timestamp=now
            ),
            Prediction(
                transaction_hash='0x' + 'tx2' + '0' * 60,
                market_id='0x' + 'a' * 64,
                user_address='0x' + '2' * 64,
                outcome=0,
                amount=500000000,
                price=450000000,
                shares=550000000,
                timestamp=now
            )
        ]
        
        for prediction in predictions:
            db.session.add(prediction)
        
        # Update user stats
        for user in users:
            user.update_stats()
        
        db.session.commit()
        
        print("Sample data seeded successfully!")
        print(f"- Created {len(users)} users")
        print(f"- Created {len(markets)} markets")
        print(f"- Created {len(predictions)} predictions")

if __name__ == '__main__':
    seed_database()

