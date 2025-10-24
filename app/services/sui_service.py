import os
import requests
from typing import List, Dict, Optional

class SuiService:
    """Service for interacting with Sui blockchain"""
    
    def __init__(self):
        self.rpc_url = os.getenv('SUI_RPC_URL', 'https://fullnode.devnet.sui.io:443')
        self.package_id = os.getenv('SUI_PACKAGE_ID')
        self.module = 'polymarket'
    
    def _rpc_call(self, method: str, params: List) -> Dict:
        """Make a JSON-RPC call to Sui node"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                raise Exception(f"RPC Error: {result['error']}")
            
            return result.get('result', {})
        except Exception as e:
            print(f"RPC call failed: {e}")
            return {}
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """Fetch a single market from blockchain"""
        try:
            result = self._rpc_call('sui_getObject', [
                market_id,
                {
                    "showType": True,
                    "showOwner": True,
                    "showPreviousTransaction": True,
                    "showDisplay": False,
                    "showContent": True,
                    "showBcs": False,
                    "showStorageRebate": False
                }
            ])
            
            if not result or 'data' not in result:
                return None
            
            content = result['data'].get('content', {})
            fields = content.get('fields', {})
            
            return self._parse_market_data(fields, market_id)
        except Exception as e:
            print(f"Error fetching market {market_id}: {e}")
            return None
    
    def fetch_all_markets(self) -> List[Dict]:
        """Fetch all markets from blockchain"""
        try:
            # Query for all objects of type Market
            result = self._rpc_call('suix_queryObjects', [{
                "filter": {
                    "StructType": f"{self.package_id}::{self.module}::Market"
                },
                "options": {
                    "showType": True,
                    "showOwner": True,
                    "showPreviousTransaction": True,
                    "showDisplay": False,
                    "showContent": True,
                    "showBcs": False,
                    "showStorageRebate": False
                }
            }])
            
            markets = []
            if result and 'data' in result:
                for obj in result['data']:
                    if 'data' in obj and 'content' in obj['data']:
                        fields = obj['data']['content'].get('fields', {})
                        market_id = obj['data']['objectId']
                        market_data = self._parse_market_data(fields, market_id)
                        if market_data:
                            markets.append(market_data)
            
            return markets
        except Exception as e:
            print(f"Error fetching all markets: {e}")
            return []
    
    def _parse_market_data(self, fields: Dict, market_id: str) -> Dict:
        """Parse market data from blockchain response"""
        try:
            return {
                'id': market_id,
                'question': fields.get('question', ''),
                'description': fields.get('description', ''),
                'end_time': int(fields.get('end_time', 0)),
                'creator': fields.get('creator', ''),
                'resolved': fields.get('resolved', False),
                'winning_outcome': int(fields.get('winning_outcome', 0)),
                'total_liquidity': int(fields.get('total_liquidity', 0)),
                'outcome_a_shares': int(fields.get('outcome_a_shares', 0)),
                'outcome_b_shares': int(fields.get('outcome_b_shares', 0)),
                'volume_24h': int(fields.get('volume_24h', 0)),
                'created_timestamp': int(fields.get('created_timestamp', 0)),
                'category': fields.get('category', ''),
                'image_url': fields.get('image_url', ''),
                'tags': fields.get('tags', [])
            }
        except Exception as e:
            print(f"Error parsing market data: {e}")
            return {}
    
    def get_market_events(self, market_id: str) -> List[Dict]:
        """Get events for a specific market"""
        try:
            result = self._rpc_call('suix_queryEvents', [{
                "MoveEventType": f"{self.package_id}::{self.module}::TradeExecuted"
            }, None, 100, False])
            
            events = result.get('data', [])
            
            # Filter events for this market
            market_events = []
            for event in events:
                parsed = event.get('parsedJson', {})
                if parsed.get('market_id') == market_id:
                    market_events.append(parsed)
            
            return market_events
        except Exception as e:
            print(f"Error fetching market events: {e}")
            return []
    
    def get_user_predictions(self, user_address: str) -> List[Dict]:
        """Get all predictions for a user (placeholder)"""
        # This would require indexing TradeExecuted events by user
        print(f"get_user_predictions: Not implemented for {user_address}")
        return []

