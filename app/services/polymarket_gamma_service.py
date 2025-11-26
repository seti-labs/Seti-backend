"""
Service for fetching markets and events from Polymarket Gamma API
Replaces RapidAPI integration
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
from app.models import Market
from app import db


class PolymarketGammaService:
    """Service for integrating with Polymarket Gamma API"""
    
    def __init__(self):
        self.base_url = 'https://gamma-api.polymarket.com'
        self.events_endpoint = f'{self.base_url}/events'
        self.markets_endpoint = f'{self.base_url}/markets'
        self.teams_endpoint = f'{self.base_url}/teams'
        self.sports_endpoint = f'{self.base_url}/sports'
        self.tags_endpoint = f'{self.base_url}/tags'
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            response = requests.get(
                endpoint,
                params=params,
                timeout=10,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Polymarket API request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in Polymarket API request: {e}")
            return None
    
    def get_events(self, params: Dict = None) -> List[Dict]:
        """
        Fetch events from Polymarket Gamma API
        
        Args:
            params: Query parameters (limit, offset, order, ascending, closed, tag_id, etc.)
            
        Returns:
            List of event dictionaries
        """
        default_params = {
            'order': 'id',
            'ascending': False,
            'closed': False,
            'limit': 100
        }
        
        if params:
            default_params.update(params)
        
        data = self._make_request(self.events_endpoint, default_params)
        return data if isinstance(data, list) else []
    
    def get_markets(self, params: Dict = None) -> List[Dict]:
        """
        Fetch markets from Polymarket Gamma API
        
        Args:
            params: Query parameters (limit, offset, order, ascending, closed, tag_id, etc.)
            
        Returns:
            List of market dictionaries
        """
        default_params = {
            'order': 'id',
            'ascending': False,
            'closed': False,
            'limit': 100
        }
        
        if params:
            default_params.update(params)
        
        data = self._make_request(self.markets_endpoint, default_params)
        return data if isinstance(data, list) else []
    
    def get_event_by_slug(self, slug: str) -> Optional[Dict]:
        """
        Fetch a specific event by slug
        
        Args:
            slug: Event slug from Polymarket URL
            
        Returns:
            Event dictionary or None
        """
        endpoint = f'{self.events_endpoint}/slug/{slug}'
        return self._make_request(endpoint)
    
    def get_market_by_slug(self, slug: str) -> Optional[Dict]:
        """
        Fetch a specific market by slug
        
        Args:
            slug: Market slug from Polymarket URL
            
        Returns:
            Market dictionary or None
        """
        endpoint = f'{self.markets_endpoint}/slug/{slug}'
        return self._make_request(endpoint)
    
    def get_events_by_tag(self, tag_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Fetch events filtered by tag
        
        Args:
            tag_id: Tag ID to filter by
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of event dictionaries
        """
        params = {
            'tag_id': tag_id,
            'closed': False,
            'limit': limit,
            'offset': offset
        }
        return self.get_events(params)
    
    def get_markets_by_tag(self, tag_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Fetch markets filtered by tag
        
        Args:
            tag_id: Tag ID to filter by
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of market dictionaries
        """
        params = {
            'tag_id': tag_id,
            'closed': False,
            'limit': limit,
            'offset': offset
        }
        return self.get_markets(params)
    
    def get_sports_metadata(self) -> List[Dict]:
        """
        Get sports metadata including tags, images, and resolution sources
        
        Returns:
            List of sports metadata dictionaries
        """
        data = self._make_request(self.sports_endpoint)
        return data if isinstance(data, list) else []
    
    def get_tags(self) -> List[Dict]:
        """
        Get all available tags
        
        Returns:
            List of tag dictionaries
        """
        data = self._make_request(self.tags_endpoint)
        return data if isinstance(data, list) else []
    
    def sync_markets_to_database(self, limit: int = 50) -> int:
        """
        Sync active markets from Polymarket to local database
        
        Args:
            limit: Maximum number of markets to sync
            
        Returns:
            Number of markets synced
        """
        events = self.get_events({
            'limit': limit,
            'closed': False,
            'order': 'id',
            'ascending': False
        })
        
        synced_count = 0
        
        for event in events:
            try:
                # Extract event data
                event_id = event.get('id')
                slug = event.get('slug')
                title = event.get('title', '')
                description = event.get('description', '')
                end_date = event.get('endDate')
                tags = event.get('tags', [])
                
                # Check if market already exists
                existing_market = Market.query.filter_by(id=f"polymarket_{event_id}").first()
                if existing_market:
                    continue
                
                # Determine category from tags
                category = 'Sports'
                if tags:
                    # Try to find sport tag
                    sport_tags = [t for t in tags if isinstance(t, dict) and 'sport' in str(t).lower()]
                    if sport_tags:
                        category = f"sports-{sport_tags[0].get('name', 'general').lower()}"
                
                # Calculate end_time
                if end_date:
                    try:
                        end_time = int(datetime.fromisoformat(end_date.replace('Z', '+00:00')).timestamp())
                    except:
                        end_time = int(datetime.utcnow().timestamp()) + 86400  # Default to 24h from now
                else:
                    end_time = int(datetime.utcnow().timestamp()) + 86400
                
                # Create market
                market = Market(
                    id=f"polymarket_{event_id}",
                    question=title or f"Polymarket Event {event_id}",
                    description=description or '',
                    end_time=end_time,
                    creator="0x0000000000000000000000000000000000000000",
                    resolved=False,
                    created_timestamp=int(datetime.utcnow().timestamp()),
                    category=category,
                    tags=tags if isinstance(tags, list) else []
                )
                
                db.session.add(market)
                synced_count += 1
                
            except Exception as e:
                print(f"Error syncing event {event.get('id')}: {e}")
                continue
        
        try:
            db.session.commit()
            print(f"✅ Synced {synced_count} markets from Polymarket")
        except Exception as e:
            print(f"❌ Error committing synced markets: {e}")
            db.session.rollback()
            return 0
        
        return synced_count
    
    def get_live_scores_for_markets(self, markets: List[Market]) -> Dict[str, Dict]:
        """
        Get live data for markets from Polymarket events
        
        Args:
            markets: List of Market objects
            
        Returns:
            Dictionary mapping market_id to live data
        """
        live_data = {}
        
        # Fetch active events
        events = self.get_events({
            'closed': False,
            'limit': 200
        })
        
        # Create a mapping of event titles to events
        event_map = {}
        for event in events:
            title = event.get('title', '').lower()
            event_map[title] = event
        
        # Match markets to events
        for market in markets:
            if not market.category or 'sport' not in market.category.lower():
                continue
            
            # Try to match by question/title
            market_question = market.question.lower()
            
            for event_title, event in event_map.items():
                if market_question in event_title or event_title in market_question:
                    # Extract event data
                    markets_data = event.get('markets', [])
                    if markets_data:
                        # Get the first market's outcome prices
                        first_market = markets_data[0]
                        outcomes = first_market.get('outcomes', [])
                        
                        live_data[market.id] = {
                            'market_id': market.id,
                            'market_question': market.question,
                            'event_title': event.get('title', ''),
                            'event_slug': event.get('slug', ''),
                            'is_closed': event.get('closed', False),
                            'end_date': event.get('endDate', ''),
                            'outcomes': outcomes,
                            'last_updated': datetime.utcnow().isoformat(),
                            'data_source': 'polymarket_gamma_api'
                        }
                    break
        
        return live_data
    
    def update_market_with_live_data(self, market_id: str) -> Optional[Dict]:
        """
        Update a specific market with live data from Polymarket
        
        Args:
            market_id: Market ID to update
            
        Returns:
            Live data dictionary or None
        """
        market = Market.query.get(market_id)
        if not market:
            return None
        
        # Try to find matching event
        events = self.get_events({
            'closed': False,
            'limit': 100
        })
        
        market_question = market.question.lower()
        
        for event in events:
            event_title = event.get('title', '').lower()
            if market_question in event_title or event_title in market_question:
                markets_data = event.get('markets', [])
                if markets_data:
                    first_market = markets_data[0]
                    return {
                        'market_id': market_id,
                        'market_question': market.question,
                        'event_title': event.get('title', ''),
                        'event_slug': event.get('slug', ''),
                        'is_closed': event.get('closed', False),
                        'end_date': event.get('endDate', ''),
                        'outcomes': first_market.get('outcomes', []),
                        'last_updated': datetime.utcnow().isoformat()
                    }
        
        return None


# Global instance
polymarket_gamma_service = PolymarketGammaService()

