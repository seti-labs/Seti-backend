import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Market, Game
from .rate_limited_api import RateLimitedAPI

class MarketSportsService:
    """Service for integrating live sports data with prediction markets"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = 'https://sportsbook-api2.p.rapidapi.com/v0'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'sportsbook-api2.p.rapidapi.com',
            'Accept': 'application/json'
        } if self.api_key else {}
        
        # Initialize rate-limited API client
        self.api_client = RateLimitedAPI(
            api_key=self.api_key or '',
            base_url=self.base_url,
            headers=self.headers
        )
        
        # Valid sports for markets
        self.allowed_sports = ['AMERICAN_FOOTBALL', 'ICE_HOCKEY', 'BASKETBALL', 'BASEBALL', 'SOCCER']
        
        # Test API availability (lazy initialization)
        self.api_available = False
        self.last_api_check = datetime.now()
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """Lazy initialization of API availability"""
        try:
            self.api_available = self._test_api_availability()
        except Exception as e:
            print(f"API initialization failed: {e}")
            self.api_available = False
    
    def _test_api_availability(self) -> bool:
        """Test if the API is available and subscribed"""
        if not self.api_key:
            return False
        
        try:
            # Test with the advantages endpoint
            response = requests.get(
                f"{self.base_url}/advantages/?type=ARBITRAGE",
                headers=self.headers, 
                timeout=5
            )
            
            if response.status_code == 200:
                print("Sportsbook API is available and working")
                return True
            elif response.status_code == 403:
                print("API key not subscribed to Sportsbook service")
                return False
            else:
                print(f"API test failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"API availability test failed: {e}")
            return False
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting and caching"""
        # Check API availability periodically
        if datetime.now() - self.last_api_check > timedelta(minutes=5):
            self.api_available = self._test_api_availability()
            self.last_api_check = datetime.now()
        
        if not self.api_available:
            print("Sportsbook API not available")
            return None
            
        return self.api_client.get(endpoint, params)
    
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
                    'home': home_team,
                    'away': away_team
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
        """Get live scores for a list of markets using sportsbook API"""
        live_scores = {}
        
        if not self.api_available:
            print("Sportsbook API not available")
            return live_scores
        
        # Get current advantages/arbitrage opportunities
        try:
            advantages_data = self._make_request('advantages/', {'type': 'ARBITRAGE'})
            if not advantages_data or 'advantages' not in advantages_data:
                return live_scores
            
            advantages = advantages_data['advantages']
        
        for market in markets:
            if not market.category or 'sport' not in market.category.lower():
                continue
            
                # Try to match market with sportsbook data
                market_data = self._find_matching_sportsbook_market(market, advantages)
                if market_data:
                    live_scores[market.id] = market_data
                    
        except Exception as e:
            print(f"Error fetching sportsbook data: {e}")
        
        return live_scores
    
    def _find_matching_sportsbook_market(self, market: Market, advantages: List[Dict]) -> Optional[Dict]:
        """Find matching sportsbook market for a prediction market"""
        teams = self.extract_teams_from_question(market.question)
        if not teams:
            return None
        
        for advantage in advantages:
            event = advantage.get('market', {}).get('event', {})
            participants = event.get('participants', [])
            
            if len(participants) >= 2:
                home_team = participants[0]['name']
                away_team = participants[1]['name']
                
                # Check if teams match (only if both teams are extracted)
                if teams['away'] and (
                    (teams['home'].lower() in home_team.lower() and teams['away'].lower() in away_team.lower()) or
                    (teams['home'].lower() in away_team.lower() and teams['away'].lower() in home_team.lower())
                ):
                    
                    # Extract odds from outcomes
                    outcomes = advantage.get('outcomes', [])
                    home_odds = None
                    away_odds = None
                    
                    for outcome in outcomes:
                        participant_key = outcome.get('participantKey')
                        payout = outcome.get('payout', 1.0)
                        
                        if participant_key == participants[0]['key']:
                            home_odds = payout
                        elif participant_key == participants[1]['key']:
                            away_odds = payout
                    
                    return {
                        'market_id': market.id,
                        'market_question': market.question,
                        'event_name': event.get('name', ''),
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_odds': home_odds,
                        'away_odds': away_odds,
                        'sport': event.get('participants', [{}])[0].get('sport', ''),
                        'competition': event.get('competitionInstance', {}).get('competition', {}).get('name', ''),
                        'start_time': event.get('startTime', ''),
                        'is_live': False,  # Sportsbook API doesn't provide live status
                        'last_updated': datetime.utcnow().isoformat(),
                        'data_source': 'sportsbook_api'
                    }
        
        return None
    
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
    
    def get_rate_limit_status(self) -> Dict:
        """Get current API rate limit status"""
        status = self.api_client.get_rate_limit_status()
        status['api_available'] = self.api_available
        status['api_type'] = 'sportsbook'
        status['last_api_check'] = self.last_api_check.isoformat()
        return status
    
    def clear_api_cache(self) -> None:
        """Clear API cache"""
        self.api_client.clear_cache()

# Global instance
market_sports_service = MarketSportsService()


