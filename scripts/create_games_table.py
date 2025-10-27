#!/usr/bin/env python3
"""
Migration script to create the games table in the database.
Run with: python scripts/create_games_table.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def create_games_table():
    """Create the games table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating games table...")
            
            # Create games table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS games (
                    id SERIAL PRIMARY KEY,
                    fixture_id INTEGER UNIQUE NOT NULL,
                    home_team VARCHAR(200) NOT NULL,
                    away_team VARCHAR(200) NOT NULL,
                    league VARCHAR(100) NOT NULL,
                    league_id INTEGER,
                    kickoff_time TIMESTAMP NOT NULL,
                    status VARCHAR(50) DEFAULT 'scheduled',
                    home_score INTEGER,
                    away_score INTEGER,
                    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE SET NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    api_data JSONB
                )
            """))
            
            # Create indexes
            print("Creating indexes...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_games_fixture_id ON games(fixture_id)
            """))
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_games_kickoff_time ON games(kickoff_time)
            """))
            
            # Enable RLS
            print("Enabling RLS...")
            db.session.execute(text("ALTER TABLE games ENABLE ROW LEVEL SECURITY"))
            
            # Create RLS policy
            print("Creating RLS policy...")
            db.session.execute(text("""
                DROP POLICY IF EXISTS "Allow public read access on games" ON games
            """))
            
            db.session.execute(text("""
                CREATE POLICY "Allow public read access on games" ON games FOR SELECT USING (true)
            """))
            
            # Commit changes
            db.session.commit()
            
            print("✅ Games table created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating games table: {e}")
            sys.exit(1)

if __name__ == '__main__':
    create_games_table()
