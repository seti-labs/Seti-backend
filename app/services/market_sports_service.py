import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Market, Game

class MarketSportsService:
    """Service for integrating live sports data with prediction markets"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = 'https://api-football-v1.p.rapidapi.com/v3'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com',
            'Accept': 'application/json'
        } if self.api_key else {}
        
        # Valid leagues for sports markets
        self.allowed_league_ids = [39, 140, 78, 135, 61]  # PL, La Liga, Bundesliga, Serie A, Ligue 1
    
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
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def extract_teams_from_question(self, question: str) -> Optional[Dict[str, str]]:
        """Extract team names from market question"""
        import re
        
        # Common patterns for sports questions
        patterns = [
            r'(?:Will|Will the|Does|Do|Can|Will)\s+([A-Z][a-zA-Z\s]+?)\s+(?:beat|defeat|win against|defeat|vs|v\.|against)\s+([A-Z][a-zA-Z\s]+?)(?:\s|$|\?)',
            r'([A-Z][a-zA-Z\s]+?)\s+(?:vs|v\.|against)\s+([A-Z][a-zA-Z\s]+?)(?:\s|$|\?)',
            r'(?:Will|Will the|Does|Do|Can|Will)\s+([A-Z][a-zA-Z\s]+?)\s+(?:win|beat|defeat)(?:\s|$|\?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                home_team = match.group(1).strip()
                away_team = match.group(2).strip() if len(match.groups()) > 1 else None
                return {
                    'home_team': home_team,
                    'away_team': away_team
                }
        
        return None
    
    def find_matching_fixture(self, market: Market) -> Optional[Dict]:
        """Find matching sports fixture for a market"""
        if not market.category or 'sport' not in market.category.lower():
            return None
        
        teams = self.extract_teams_from_question(market.question)
        if not teams:
            return None
        
        # Search for fixtures today and tomorrow
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        for date in [today, tomorrow]:
            params = {
                'date': date.isoformat(),
                'league': ','.join(map(str, self.allowed_league_ids))
            }
            
            data = self._make_request('fixtures', params)
            if not data or 'response' not in data:
                continue
            
            for fixture in data['response']:
                try:
                    home_team = fixture['teams']['home']['name']
                    away_team = fixture['teams']['away']['name']
                    
                    # Check if teams match (fuzzy matching)
                    if self._teams_match(teams['home_team'], home_team) and \
                       (not teams.get('away_team') or self._teams_match(teams['away_team'], away_team)):
                        
                        return {
                            'fixture_id': fixture['fixture']['id'],
                            'home_team': home_team,
                            'away_team': away_team,
                            'league': fixture['league']['name'],
                            'league_id': fixture['league']['id'],
                            'kickoff_time': datetime.fromisoformat(fixture['fixture']['date'].replace('Z', '+00:00')),
                            'status': fixture['fixture']['status']['short'],
                            'home_score': fixture['goals']['home'],
                            'away_score': fixture['goals']['away'],
                            'period': self._get_period(fixture['fixture']['status']['short']),
                            'elapsed_time': fixture['fixture']['status']['elapsed'],
                            'api_data': fixture
                        }
                except Exception as e:
                    print(f"Error parsing fixture: {e}")
                    continue
        
        return None
    
    def _teams_match(self, team1: str, team2: str) -> bool:
        """Fuzzy matching for team names"""
        team1_clean = team1.lower().replace('fc', '').replace('united', '').replace('city', '').strip()
        team2_clean = team2.lower().replace('fc', '').replace('united', '').replace('city', '').strip()
        
        # Exact match
        if team1_clean == team2_clean:
            return True
        
        # Check if one contains the other
        if team1_clean in team2_clean or team2_clean in team1_clean:
            return True
        
        # Check common abbreviations
        abbreviations = {
            'manchester united': ['man utd', 'manchester utd'],
            'manchester city': ['man city'],
            'real madrid': ['real'],
            'barcelona': ['barca'],
            'bayern munich': ['bayern'],
            'paris saint germain': ['psg'],
            'juventus': ['juve'],
            'inter milan': ['inter'],
            'ac milan': ['milan'],
            'arsenal': ['arsenal fc'],
            'chelsea': ['chelsea fc'],
            'liverpool': ['liverpool fc'],
            'tottenham': ['spurs', 'tottenham hotspur']
        }
        
        for full_name, abbrs in abbreviations.items():
            if (team1_clean == full_name and team2_clean in abbrs) or \
               (team2_clean == full_name and team1_clean in abbrs):
                return True
        
        return False
    
    def _get_period(self, status: str) -> str:
        """Convert API status to readable period"""
        status_map = {
            'NS': 'Not Started',
            'LIVE': 'Live',
            'HT': 'Half Time',
            'FT': 'Full Time',
            '1H': '1st Half',
            '2H': '2nd Half',
            'P': 'Penalties',
            'AET': 'Extra Time',
            'PEN': 'Penalties',
            'SUSP': 'Suspended',
            'CANC': 'Cancelled',
            'ABD': 'Abandoned'
        }
        return status_map.get(status, status)
    
    def get_live_scores_for_markets(self, markets: List[Market]) -> Dict[str, Dict]:
        """Get live scores for a list of markets"""
        live_scores = {}
        
        for market in markets:
            if not market.category or 'sport' not in market.category.lower():
                continue
            
            fixture_data = self.find_matching_fixture(market)
            if fixture_data:
                live_scores[market.id] = {
                    'market_id': market.id,
                    'market_question': market.question,
                    'fixture_id': fixture_data['fixture_id'],
                    'home_team': fixture_data['home_team'],
                    'away_team': fixture_data['away_team'],
                    'home_score': fixture_data['home_score'],
                    'away_score': fixture_data['away_score'],
                    'league': fixture_data['league'],
                    'status': fixture_data['status'],
                    'period': fixture_data['period'],
                    'elapsed_time': fixture_data.get('elapsed_time'),
                    'kickoff_time': fixture_data['kickoff_time'].isoformat(),
                    'is_live': fixture_data['status'] in ['LIVE', 'HT', '1H', '2H'],
                    'is_finished': fixture_data['status'] in ['FT', 'AET', 'PEN'],
                    'last_updated': datetime.utcnow().isoformat()
                }
        
        return live_scores
    
    def update_market_with_live_score(self, market_id: str) -> Optional[Dict]:
        """Update a specific market with live score data"""
        market = Market.query.get(market_id)
        if not market:
            return None
        
        fixture_data = self.find_matching_fixture(market)
        if not fixture_data:
            return None
        
        return {
            'market_id': market_id,
            'market_question': market.question,
            'fixture_id': fixture_data['fixture_id'],
            'home_team': fixture_data['home_team'],
            'away_team': fixture_data['away_team'],
            'home_score': fixture_data['home_score'],
            'away_score': fixture_data['away_score'],
            'league': fixture_data['league'],
            'status': fixture_data['status'],
            'period': fixture_data['period'],
            'elapsed_time': fixture_data.get('elapsed_time'),
            'kickoff_time': fixture_data['kickoff_time'].isoformat(),
            'is_live': fixture_data['status'] in ['LIVE', 'HT', '1H', '2H'],
            'is_finished': fixture_data['status'] in ['FT', 'AET', 'PEN'],
            'last_updated': datetime.utcnow().isoformat()
        }

# Global instance
market_sports_service = MarketSportsService()


