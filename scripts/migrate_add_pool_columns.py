#!/usr/bin/env python3
"""
Database migration script to add yes_pool and no_pool columns to markets table
Run this script to update the existing database schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def migrate_add_pool_columns():
    """Add yes_pool and no_pool columns to markets table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'markets' 
                AND column_name IN ('yes_pool', 'no_pool')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'yes_pool' not in existing_columns:
                print("Adding yes_pool column...")
                db.session.execute(text("ALTER TABLE markets ADD COLUMN yes_pool BIGINT DEFAULT 0"))
                print("✓ yes_pool column added")
            else:
                print("✓ yes_pool column already exists")
                
            if 'no_pool' not in existing_columns:
                print("Adding no_pool column...")
                db.session.execute(text("ALTER TABLE markets ADD COLUMN no_pool BIGINT DEFAULT 0"))
                print("✓ no_pool column added")
            else:
                print("✓ no_pool column already exists")
            
            # Commit the changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    print("🔄 Starting database migration: Add pool columns to markets table")
    print("=" * 60)
    
    success = migrate_add_pool_columns()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("The markets table now includes yes_pool and no_pool columns.")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
