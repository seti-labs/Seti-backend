#!/usr/bin/env python3
"""
Database migration script to add claimed column to predictions table
Run this script to update the existing database schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def migrate_add_claimed_column():
    """Add claimed column to predictions table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'predictions' 
                AND column_name = 'claimed'
            """))
            existing_column = result.fetchone()
            
            if not existing_column:
                print("Adding claimed column to predictions table...")
                db.session.execute(text("ALTER TABLE predictions ADD COLUMN claimed BOOLEAN DEFAULT FALSE"))
                print("✓ claimed column added")
            else:
                print("✓ claimed column already exists")
            
            # Commit the changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    print("🔄 Starting database migration: Add claimed column to predictions table")
    print("=" * 70)
    
    success = migrate_add_claimed_column()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("The predictions table now includes the claimed column.")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
