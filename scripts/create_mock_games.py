#!/usr/bin/env python3
"""
Create mock games in the database for testing
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Game

def create_mock_games():
    """Create mock games for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if games already exist
            existing_count = Game.query.count()
            if existing_count > 0:
                print(f"Already have {existing_count} games in database")
                return
            
            # Create mock games
            mock_games = [
                {
                    'fixture_id': 1001,
                    'home_team': 'Arsenal',
                    'away_team': 'Chelsea',
                    'league': 'Premier League',
                    'league_id': 39,
                    'kickoff_time': datetime.utcnow() + timedelta(hours=2),
                    'status': 'NS',
                    'home_score': None,
                    'away_score': None
                },
                {
                    'fixture_id': 1002,
                    'home_team': 'Liverpool',
                    'away_team': 'Manchester City',
                    'league': 'Premier League',
                    'league_id': 39,
                    'kickoff_time': datetime.utcnow() + timedelta(hours=4),
                    'status': 'NS',
                    'home_score': None,
                    'away_score': None
                },
                {
                    'fixture_id': 1003,
                    'home_team': 'Lakers',
                    'away_team': 'Warriors',
                    'league': 'NBA',
                    'league_id': 39,
                    'kickoff_time': datetime.utcnow() + timedelta(hours=6),
                    'status': 'LIVE',
                    'home_score': 98,
                    'away_score': 102
                },
                {
                    'fixture_id': 1004,
                    'home_team': 'Barcelona',
                    'away_team': 'Real Madrid',
                    'league': 'La Liga',
                    'league_id': 140,
                    'kickoff_time': datetime.utcnow() + timedelta(hours=8),
                    'status': 'NS',
                    'home_score': None,
                    'away_score': None
                }
            ]
            
            for game_data in mock_games:
                game = Game(**game_data)
                db.session.add(game)
            
            db.session.commit()
            print(f"Created {len(mock_games)} mock games")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating mock games: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    create_mock_games()
