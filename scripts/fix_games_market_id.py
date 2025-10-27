#!/usr/bin/env python3
"""
Migration script to fix the market_id column type in the games table.
Run with: python scripts/fix_games_market_id.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def fix_games_market_id():
    """Fix the market_id column type to match the markets table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Fixing games table market_id column...")
            
            # Check if market_id column exists and its current type
            result = db.session.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name='games' AND column_name='market_id'
            """))
            
            row = result.fetchone()
            if not row:
                print("❌ market_id column not found in games table")
                return
            
            current_type = row[0]
            print(f"Current market_id type: {current_type}")
            
            # If it's integer, alter it to VARCHAR(66)
            if current_type == 'integer':
                print("Altering market_id column to VARCHAR(66)...")
                db.session.execute(text("""
                    ALTER TABLE games 
                    ALTER COLUMN market_id TYPE VARCHAR(66) USING market_id::text
                """))
                
                db.session.commit()
                print("✅ market_id column type fixed successfully!")
            else:
                print(f"ℹ️  market_id is already {current_type}, no changes needed")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing games table: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    fix_games_market_id()
