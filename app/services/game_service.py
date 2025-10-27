import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Game

class GameService:
    """Service for fetching and managing sports fixtures from Sportsbook API"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = 'https://sportsbook-api2.p.rapidapi.com'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'sportsbook-api2.p.rapidapi.com',
            'Accept': 'application/json'
        } if self.api_key else {}
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            print("Warning: RAPIDAPI_KEY not set")
            return None
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params, 
                timeout=10,
                allow_redirects=True
            )
            
            # Log response for debugging
            if os.getenv('DEBUG_API_REQUESTS'):
                print(f"Request URL: {url}")
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text[:500]}")
            return None
    
    def fetch_upcoming_fixtures(self, days_ahead: int = 7) -> List[Dict]:
        """Fetch upcoming sports events from Sportsbook API"""
        data = self._make_request('v0/advantages', {'type': 'ARBITRAGE'})
        
        if not data or 'advantages' not in data:
            return []
        
        valid_fixtures = []
        seen_events = set()
        
        for advantage in data.get('advantages', []):
            market = advantage.get('market', {})
            event = market.get('event', {})
            
            # Skip if no event data
            if not event:
                continue
            
            # Create unique key for event
            event_key = event.get('key')
            if not event_key or event_key in seen_events:
                continue
            seen_events.add(event_key)
            
            # Parse event data
            try:
                participants = event.get('participants', [])
                if len(participants) < 2:
                    continue
                
                home_team = participants[0].get('name', 'Team 1')
                away_team = participants[1].get('name', 'Team 2')
                
                # Parse start time
                start_time_str = event.get('startTime')
                if not start_time_str:
                    continue
                
                # Parse with timezone
                if start_time_str.endswith('Z'):
                    kickoff_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                else:
                    kickoff_time = datetime.fromisoformat(start_time_str)
                
                # Make sure we're comparing with timezone-aware datetime
                now = datetime.utcnow().replace(tzinfo=kickoff_time.tzinfo)
                
                # Skip past events
                if kickoff_time < now:
                    continue
                
                # Get competition info
                competition = event.get('competitionInstance', {}).get('competition', {})
                league = competition.get('name', 'Unknown League')
                
                # Determine status based on start time
                now = datetime.utcnow().replace(tzinfo=kickoff_time.tzinfo)
                time_diff = kickoff_time - now
                if time_diff.days < 0:
                    status = 'FT'  # Finished
                elif time_diff.total_seconds() < 3600:  # Less than 1 hour
                    status = 'LIVE'
                else:
                    status = 'NS'  # Not started
                
                fixture_data = {
                    'fixture_id': hash(event_key) % 1000000,  # Create unique ID from key
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league,
                    'league_id': hash(competition.get('key', '')) % 100000,
                    'kickoff_time': kickoff_time,
                    'status': status,
                    'home_score': None,
                    'away_score': None,
                    'api_data': advantage
                }
                
                valid_fixtures.append(fixture_data)
                
            except Exception as e:
                print(f"Error parsing event: {e}")
                continue
        
        return valid_fixtures
    
    def get_final_score(self, fixture_id: int) -> Optional[Dict]:
        """Get final score for a completed fixture"""
        # Note: Sportsbook API doesn't provide live scores in this endpoint
        # You would need to use a different endpoint for live scores
        return None
    
    def sync_game_to_db(self, fixture_data: Dict) -> Optional[Game]:
        """Sync fixture to database"""
        try:
            # Convert timezone-aware datetime to naive datetime
            kickoff_time = fixture_data['kickoff_time']
            if kickoff_time.tzinfo is not None:
                kickoff_time = kickoff_time.replace(tzinfo=None)
            
            game = Game.query.filter_by(fixture_id=fixture_data['fixture_id']).first()
            if game:
                # Update existing game
                game.home_score = fixture_data.get('home_score')
                game.away_score = fixture_data.get('away_score')
                game.status = fixture_data['status']
                game.updated_at = datetime.utcnow()
            else:
                # Create new game
                game = Game(
                    fixture_id=fixture_data['fixture_id'],
                    home_team=fixture_data['home_team'],
                    away_team=fixture_data['away_team'],
                    league=fixture_data['league'],
                    league_id=fixture_data.get('league_id'),
                    kickoff_time=kickoff_time,
                    status=fixture_data['status'],
                    home_score=fixture_data.get('home_score'),
                    away_score=fixture_data.get('away_score'),
                    api_data=fixture_data.get('api_data')
                )
                db.session.add(game)
            
            db.session.commit()
            return game
        except Exception as e:
            db.session.rollback()
            print(f"Error syncing game: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def fetch_countries(self) -> List[Dict]:
        """Fetch all countries from API"""
        # Sportsbook API doesn't provide countries endpoint
        # Return empty list or mock data
        return []

game_service = GameService()
