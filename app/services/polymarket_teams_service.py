import requests
from typing import List, Dict, Optional
from datetime import datetime
import os

class PolymarketTeamsService:
    """Service for fetching teams data from Polymarket Gamma API"""
    
    def __init__(self):
        self.base_url = 'https://gamma-api.polymarket.com'
        self.teams_endpoint = f'{self.base_url}/teams'
        
    def fetch_teams(self, league: Optional[str] = None) -> List[Dict]:
        """
        Fetch teams from Polymarket Gamma API
        
        Args:
            league: Optional league filter (e.g., 'nfl', 'nba', 'mlb')
            
        Returns:
            List of team dictionaries with structure:
            {
                'id': int,
                'name': str,
                'league': str,
                'record': str,
                'logo': str,
                'abbreviation': str,
                'alias': str,
                'createdAt': str,
                'updatedAt': str,
                'providerId': int,
                'color': str
            }
        """
        try:
            response = requests.get(self.teams_endpoint, timeout=10)
            response.raise_for_status()
            teams = response.json()
            
            # Filter by league if specified
            if league:
                teams = [team for team in teams if team.get('league', '').lower() == league.lower()]
            
            print(f"✅ Fetched {len(teams)} teams from Polymarket API")
            return teams
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching teams from Polymarket API: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
    
    def get_teams_by_league(self) -> Dict[str, List[Dict]]:
        """
        Fetch all teams and group them by league
        
        Returns:
            Dictionary with league as key and list of teams as value
        """
        teams = self.fetch_teams()
        teams_by_league = {}
        
        for team in teams:
            league = team.get('league', 'unknown')
            if league not in teams_by_league:
                teams_by_league[league] = []
            teams_by_league[league].append(team)
        
        return teams_by_league
    
    def get_leagues_summary(self) -> List[Dict]:
        """
        Get a summary of all leagues with team counts
        
        Returns:
            List of dictionaries with league info:
            {
                'league': str,
                'team_count': int,
                'teams': List[str]
            }
        """
        teams_by_league = self.get_teams_by_league()
        
        summary = []
        for league, teams in teams_by_league.items():
            summary.append({
                'league': league,
                'league_full_name': self._get_league_full_name(league),
                'team_count': len(teams),
                'teams': [team['name'] for team in teams]
            })
        
        # Sort by team count descending
        summary.sort(key=lambda x: x['team_count'], reverse=True)
        return summary
    
    def _get_league_full_name(self, league_code: str) -> str:
        """Convert league code to full name"""
        league_names = {
            'nfl': 'National Football League',
            'nba': 'National Basketball Association',
            'mlb': 'Major League Baseball',
            'nhl': 'National Hockey League',
            'mls': 'Major League Soccer',
            'epl': 'English Premier League',
            'lal': 'La Liga',
            'bun': 'Bundesliga',
            'ser': 'Serie A',
            'fl1': 'Ligue 1',
            'ucl': 'UEFA Champions League',
            'uel': 'UEFA Europa League',
            'cfb': 'College Football',
            'cbb': 'College Basketball',
            'atp': 'ATP Tennis',
            'wta': 'WTA Tennis',
            'lol': 'League of Legends',
            'csgo': 'Counter-Strike',
            'dota2': 'Dota 2',
            'mma': 'Mixed Martial Arts',
            'odi': 'One Day International Cricket',
            'abb': 'Australian Big Bash',
        }
        return league_names.get(league_code.lower(), league_code.upper())
    
    def create_potential_matchups(self, league: str, limit: int = 10) -> List[Dict]:
        """
        Create potential matchups from teams in a league
        This can be used to generate prediction markets
        
        Args:
            league: League code (e.g., 'nfl', 'nba')
            limit: Maximum number of matchups to create
            
        Returns:
            List of potential matchups with team info
        """
        teams = self.fetch_teams(league=league)
        
        if len(teams) < 2:
            return []
        
        matchups = []
        for i in range(0, min(len(teams) - 1, limit * 2), 2):
            if i + 1 < len(teams):
                home_team = teams[i]
                away_team = teams[i + 1]
                
                matchups.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league,
                    'league_full_name': self._get_league_full_name(league),
                    'question': f"Will {home_team['name']} beat {away_team['name']}?",
                    'description': f"{home_team['record']} vs {away_team['record']} in {self._get_league_full_name(league)}"
                })
        
        return matchups[:limit]
    
    def search_teams(self, query: str) -> List[Dict]:
        """
        Search teams by name
        
        Args:
            query: Search query string
            
        Returns:
            List of matching teams
        """
        teams = self.fetch_teams()
        query_lower = query.lower()
        
        matching_teams = [
            team for team in teams
            if query_lower in team.get('name', '').lower() or
               query_lower in team.get('abbreviation', '').lower() or
               query_lower in team.get('league', '').lower()
        ]
        
        return matching_teams

# Global instance
polymarket_teams_service = PolymarketTeamsService()

