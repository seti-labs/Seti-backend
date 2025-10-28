import os
import json
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Market, Game

class MockSportsService:
    """Mock sports service for development when API is unavailable"""
    
    def __init__(self):
        self.mock_teams = [
            "Manchester United", "Liverpool", "Arsenal", "Chelsea", "Manchester City",
            "Tottenham", "Real Madrid", "Barcelona", "Atletico Madrid", "Bayern Munich",
            "Borussia Dortmund", "Juventus", "AC Milan", "Inter Milan", "PSG",
            "Lyon", "Marseille", "Napoli", "Roma", "Lazio"
        ]
        
        self.mock_leagues = [
            {"id": 39, "name": "Premier League", "country": "England"},
            {"id": 140, "name": "La Liga", "country": "Spain"},
            {"id": 78, "name": "Bundesliga", "country": "Germany"},
            {"id": 135, "name": "Serie A", "country": "Italy"},
            {"id": 61, "name": "Ligue 1", "country": "France"}
        ]
        
        self.mock_statuses = ["NS", "LIVE", "HT", "1H", "2H", "FT"]
        
    def generate_mock_fixtures(self, days_ahead: int = 7) -> List[Dict]:
        """Generate mock fixtures for the next few days"""
        fixtures = []
        base_date = datetime.now()
        
        for i in range(days_ahead):
            date = base_date + timedelta(days=i)
            
            # Generate 5-10 fixtures per day
            num_fixtures = random.randint(5, 10)
            
            for j in range(num_fixtures):
                home_team = random.choice(self.mock_teams)
                away_team = random.choice([t for t in self.mock_teams if t != home_team])
                league = random.choice(self.mock_leagues)
                
                # Random status based on date
                if date.date() < datetime.now().date():
                    status = random.choice(["FT", "AET", "PEN"])
                    home_score = random.randint(0, 4)
                    away_score = random.randint(0, 4)
                elif date.date() == datetime.now().date():
                    status = random.choice(["NS", "LIVE", "HT", "1H", "2H", "FT"])
                    home_score = random.randint(0, 3) if status in ["LIVE", "HT", "1H", "2H", "FT"] else None
                    away_score = random.randint(0, 3) if status in ["LIVE", "HT", "1H", "2H", "FT"] else None
                else:
                    status = "NS"
                    home_score = None
                    away_score = None
                
                fixture = {
                    "fixture_id": random.randint(1000, 9999),
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "league": league["name"],
                    "league_id": league["id"],
                    "status": status,
                    "period": "1H" if status in ["1H", "LIVE"] else "2H" if status in ["2H"] else "HT" if status == "HT" else "FT" if status == "FT" else "NS",
                    "kickoff_time": date.replace(hour=random.randint(14, 22), minute=0, second=0, microsecond=0),
                    "elapsed_time": random.randint(0, 90) if status in ["LIVE", "1H", "2H"] else None
                }
                
                fixtures.append(fixture)
        
        return fixtures
    
    def find_matching_fixture(self, market: Market) -> Optional[Dict]:
        """Find matching fixture for a market (mock implementation)"""
        # Extract teams from market question
        teams = self.extract_teams_from_question(market.question)
        if not teams:
            return None
        
        # Generate mock fixtures and find match
        fixtures = self.generate_mock_fixtures()
        
        for fixture in fixtures:
            if (fixture["home_team"].lower() in teams["home"].lower() and 
                fixture["away_team"].lower() in teams["away"].lower()):
                return fixture
        
        return None
    
    def extract_teams_from_question(self, question: str) -> Optional[Dict[str, str]]:
        """Extract team names from market question"""
        import re
        
        # Common patterns for team extraction
        patterns = [
            r'(.+?)\s+vs?\s+(.+)',
            r'(.+?)\s+v\s+(.+)',
            r'(.+?)\s+@\s+(.+)',
            r'(.+?)\s+-\s+(.+)',
            r'(.+?)\s+vs\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return {
                    "home": match.group(1).strip(),
                    "away": match.group(2).strip()
                }
        
        return None
    
    def get_live_scores(self, market_id: int) -> Optional[Dict]:
        """Get live scores for a market (mock implementation)"""
        market = Market.query.get(market_id)
        if not market:
            return None
        
        fixture = self.find_matching_fixture(market)
        if not fixture:
            return None
        
        return {
            'market_id': market_id,
            'market_question': market.question,
            'fixture_id': fixture['fixture_id'],
            'home_team': fixture['home_team'],
            'away_team': fixture['away_team'],
            'home_score': fixture['home_score'],
            'away_score': fixture['away_score'],
            'league': fixture['league'],
            'status': fixture['status'],
            'period': fixture['period'],
            'elapsed_time': fixture.get('elapsed_time'),
            'kickoff_time': fixture['kickoff_time'].isoformat(),
            'is_live': fixture['status'] in ['LIVE', 'HT', '1H', '2H'],
            'is_finished': fixture['status'] in ['FT', 'AET', 'PEN'],
            'last_updated': datetime.utcnow().isoformat(),
            'is_mock_data': True
        }
    
    def get_rate_limit_status(self) -> Dict:
        """Mock rate limit status"""
        return {
            'requests_last_minute': 0,
            'requests_today': 0,
            'max_per_minute': 100,
            'max_per_day': 1000,
            'cache_size': 0,
            'is_rate_limited': False,
            'is_mock_service': True
        }
    
    def clear_api_cache(self) -> None:
        """Mock cache clear"""
        pass
