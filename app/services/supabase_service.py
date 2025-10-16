import os
from typing import Optional, Dict, List
from supabase import create_client, Client

class SupabaseService:
    """Service for Supabase realtime and storage features"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL', '')
        self.key = os.getenv('SUPABASE_KEY', '')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY', '')
        
        self.client: Optional[Client] = None
        if self.url and self.key:
            self.client = create_client(self.url, self.key)
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return bool(self.url and self.key and self.client)
    
    def get_client(self) -> Optional[Client]:
        """Get Supabase client instance"""
        return self.client
    
    # Realtime subscriptions
    def subscribe_to_markets(self, callback):
        """Subscribe to market changes in realtime"""
        if not self.client:
            return None
        
        try:
            return self.client.table('markets').on('*', callback).subscribe()
        except Exception as e:
            print(f"Error subscribing to markets: {e}")
            return None
    
    def subscribe_to_predictions(self, callback):
        """Subscribe to prediction changes in realtime"""
        if not self.client:
            return None
        
        try:
            return self.client.table('predictions').on('*', callback).subscribe()
        except Exception as e:
            print(f"Error subscribing to predictions: {e}")
            return None
    
    # Storage operations (for market images, user avatars, etc.)
    def upload_file(self, bucket: str, path: str, file_data: bytes) -> Optional[str]:
        """Upload file to Supabase storage"""
        if not self.client:
            return None
        
        try:
            result = self.client.storage.from_(bucket).upload(path, file_data)
            public_url = self.client.storage.from_(bucket).get_public_url(path)
            return public_url
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from Supabase storage"""
        if not self.client:
            return False
        
        try:
            self.client.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_public_url(self, bucket: str, path: str) -> Optional[str]:
        """Get public URL for a file"""
        if not self.client:
            return None
        
        try:
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            print(f"Error getting public URL: {e}")
            return None
    
    # Direct table operations (alternative to SQLAlchemy)
    def query_table(self, table: str, filters: Dict = None) -> List[Dict]:
        """Query a table directly using Supabase client"""
        if not self.client:
            return []
        
        try:
            query = self.client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error querying table {table}: {e}")
            return []
    
    def insert_row(self, table: str, data: Dict) -> Optional[Dict]:
        """Insert a row into a table"""
        if not self.client:
            return None
        
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error inserting into {table}: {e}")
            return None
    
    def update_row(self, table: str, row_id: str, data: Dict) -> Optional[Dict]:
        """Update a row in a table"""
        if not self.client:
            return None
        
        try:
            result = self.client.table(table).update(data).eq('id', row_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating {table}: {e}")
            return None

