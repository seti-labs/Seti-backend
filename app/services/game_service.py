import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app import db
from app.models.game import Game

class GameService:
    """Service for fetching and managing sports fixtures from API-Sports"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = 'https://api-football-v1.p.rapidapi.com/v3'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
        } if self.api_key else {}
        
        # Valid leagues for auto-creation
        self.allowed_league_ids = [39, 140, 78, 135, 61]  # PL, La Liga, Bundesliga, Serie A, Ligue 1
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            print("Warning: RAPIDAPI_KEY not set")
            return None
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def fetch_upcoming_fixtures(self, days_ahead: int = 7) -> List[Dict]:
        """Fetch upcoming football fixtures"""
        today = datetime.utcnow().date()
        params = {'date': today.isoformat(), 'league': ','.join(map(str, self.allowed_league_ids))}
        data = self._make_request('fixtures', params)
        if not data or 'response' not in data:
            return []
        
        valid_fixtures = []
        for fixture in data['response']:
            try:
                fixture_data = {
                    'fixture_id': fixture['fixture']['id'],
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'league': fixture['league']['name'],
                    'league_id': fixture['league']['id'],
                    'kickoff_time': datetime.fromisoformat(fixture['fixture']['date'].replace('Z', '+00:00')),
                    'status': fixture['fixture']['status']['short'],
                    'home_score': fixture['goals']['home'],
                    'away_score': fixture['goals']['away'],
                    'api_data': fixture
                }
                if fixture_data['status'] in ['NS', 'LIVE', 'HT', 'FT']:
                    valid_fixtures.append(fixture_data)
            except Exception as e:
                print(f"Error parsing fixture: {e}")
        return valid_fixtures
    
    def get_final_score(self, fixture_id: int) -> Optional[Dict]:
        """Get final score for a completed fixture"""
        params = {'id': fixture_id}
        data = self._make_request('fixtures', params)
        if not data or 'response' not in data:
            return None
        
        fixture = data['response'][0]
        if fixture['fixture']['status']['short'] != 'FT':
            return None
        
        home_score = fixture['goals']['home']
        away_score = fixture['goals']['away']
        winner = 'home' if home_score > away_score else ('away' if away_score > home_score else 'draw')
        
        return {'fixture_id': fixture_id, 'home_score': home_score, 'away_score': away_score, 'winner': winner}
    
    def sync_game_to_db(self, fixture_data: Dict) -> Optional[Game]:
        """Sync fixture to database"""
        try:
            game = Game.query.filter_by(fixture_id=fixture_data['fixture_id']).first()
            if game:
                game.home_score = fixture_data.get('home_score')
                game.away_score = fixture_data.get('away_score')
                game.status = fixture_data['status']
            else:
                game = Game(**{k: v for k, v in fixture_data.items() if k != 'api_data'})
                db.session.add(game)
            db.session.commit()
            return game
        except Exception as e:
            db.session.rollback()
            print(f"Error syncing game: {e}")
            return None

game_service = GameService()
