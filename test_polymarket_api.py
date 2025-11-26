#!/usr/bin/env python3
"""
Test script for Polymarket Teams API integration
Tests both direct API access and Flask endpoints
"""

import requests
import json
from app.services.polymarket_teams_service import polymarket_teams_service

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_direct_api():
    """Test direct access to Polymarket Gamma API"""
    print_section("1. TESTING DIRECT POLYMARKET API ACCESS")
    
    try:
        response = requests.get('https://gamma-api.polymarket.com/teams', timeout=10)
        response.raise_for_status()
        teams = response.json()
        
        print(f"✅ Successfully fetched {len(teams)} teams")
        print(f"\nFirst 3 teams:")
        for team in teams[:3]:
            print(f"  - {team.get('name')} ({team.get('league').upper()}) - {team.get('record')}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_service_layer():
    """Test PolymarketTeamsService"""
    print_section("2. TESTING SERVICE LAYER")
    
    # Test 1: Fetch all teams
    print("Test 2.1: Fetch all teams")
    teams = polymarket_teams_service.fetch_teams()
    print(f"✅ Fetched {len(teams)} teams")
    
    # Test 2: Fetch teams by league
    print("\nTest 2.2: Fetch NBA teams")
    nba_teams = polymarket_teams_service.fetch_teams(league='nba')
    print(f"✅ Fetched {len(nba_teams)} NBA teams")
    if nba_teams:
        print("Sample NBA teams:")
        for team in nba_teams[:5]:
            print(f"  - {team.get('name')} ({team.get('abbreviation')}) - {team.get('record')}")
    
    # Test 3: Get teams grouped by league
    print("\nTest 2.3: Get teams by league")
    teams_by_league = polymarket_teams_service.get_teams_by_league()
    print(f"✅ Found {len(teams_by_league)} leagues")
    for league, league_teams in list(teams_by_league.items())[:5]:
        print(f"  - {league.upper()}: {len(league_teams)} teams")
    
    # Test 4: Get leagues summary
    print("\nTest 2.4: Get leagues summary")
    summary = polymarket_teams_service.get_leagues_summary()
    print(f"✅ League summary (Top 10):")
    for league_info in summary[:10]:
        print(f"  - {league_info['league_full_name']} ({league_info['league']}): {league_info['team_count']} teams")
    
    # Test 5: Create potential matchups
    print("\nTest 2.5: Create potential NBA matchups")
    matchups = polymarket_teams_service.create_potential_matchups('nba', limit=5)
    print(f"✅ Created {len(matchups)} potential matchups:")
    for matchup in matchups:
        print(f"  - {matchup['question']}")
        print(f"    {matchup['description']}")
    
    # Test 6: Search teams
    print("\nTest 2.6: Search for 'Lakers' teams")
    search_results = polymarket_teams_service.search_teams('lakers')
    print(f"✅ Found {len(search_results)} matching teams:")
    for team in search_results:
        print(f"  - {team.get('name')} ({team.get('league').upper()})")

def test_flask_endpoints():
    """Test Flask API endpoints (requires Flask app to be running)"""
    print_section("3. TESTING FLASK API ENDPOINTS")
    
    # Check if server is running
    base_url = "http://localhost:5000/api/v1/polymarket"
    
    try:
        # Test health endpoint first
        health_response = requests.get("http://localhost:5000/health", timeout=2)
        if health_response.status_code != 200:
            print("❌ Backend server is not running!")
            print("   Start the server with: python run.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Backend server is not running!")
        print("   Start the server with: python run.py")
        return
    
    print("✅ Backend server is running\n")
    
    # Test 1: Get all teams
    print("Test 3.1: GET /api/v1/polymarket/teams")
    try:
        response = requests.get(f"{base_url}/teams", timeout=10)
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Fetched {data['count']} teams")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get teams by league
    print("\nTest 3.2: GET /api/v1/polymarket/teams?league=nfl")
    try:
        response = requests.get(f"{base_url}/teams", params={'league': 'nfl'}, timeout=10)
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Fetched {data['count']} NFL teams")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get leagues summary
    print("\nTest 3.3: GET /api/v1/polymarket/teams/leagues")
    try:
        response = requests.get(f"{base_url}/teams/leagues", timeout=10)
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Found {data['total_leagues']} leagues")
            print("Top 5 leagues:")
            for league in data['leagues'][:5]:
                print(f"  - {league['league_full_name']}: {league['team_count']} teams")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get potential matchups
    print("\nTest 3.4: GET /api/v1/polymarket/teams/matchups/nba")
    try:
        response = requests.get(f"{base_url}/teams/matchups/nba", params={'limit': 3}, timeout=10)
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Created {data['count']} matchups")
            for matchup in data['matchups']:
                print(f"  - {matchup['question']}")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Search teams
    print("\nTest 3.5: GET /api/v1/polymarket/teams?search=warriors")
    try:
        response = requests.get(f"{base_url}/teams", params={'search': 'warriors'}, timeout=10)
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Found {data['count']} matching teams")
            for team in data['teams']:
                print(f"  - {team['name']} ({team['league'].upper()})")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")

def compare_with_current_implementation():
    """Compare new API with current implementation"""
    print_section("4. COMPARISON WITH CURRENT IMPLEMENTATION")
    
    print("CURRENT IMPLEMENTATION (Sportsbook API):")
    print("  - Source: sportsbook-api2.p.rapidapi.com")
    print("  - Data: Game fixtures with home/away teams, kickoff times, scores")
    print("  - Requires: RapidAPI key")
    print("  - Features: Live scores, match status, real fixtures")
    print("  - Limitations: API subscription required, rate limits")
    
    print("\nNEW IMPLEMENTATION (Polymarket Gamma API):")
    print("  - Source: gamma-api.polymarket.com/teams")
    print("  - Data: Teams with league, record, logo, colors")
    print("  - Requires: No API key needed (public)")
    print("  - Features: Team metadata, league grouping, easy to use")
    print("  - Limitations: No fixture/schedule data, no live scores")
    
    print("\nRECOMMENDATION:")
    print("  1. Use Polymarket API for:")
    print("     - Team information and metadata")
    print("     - League listings")
    print("     - Creating potential prediction markets")
    print("     - No API key hassle")
    
    print("\n  2. Keep current Sportsbook API for:")
    print("     - Actual game schedules and fixtures")
    print("     - Live scores and match updates")
    print("     - Real-time game status")
    
    print("\n  3. Hybrid approach:")
    print("     - Use Polymarket API to get teams and create markets")
    print("     - Use Sportsbook API to track live scores (when API key available)")
    print("     - Fallback to Polymarket when Sportsbook API unavailable")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  POLYMARKET TEAMS API - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Run tests
    test_direct_api()
    test_service_layer()
    test_flask_endpoints()
    compare_with_current_implementation()
    
    print("\n" + "="*80)
    print("  TEST SUITE COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()

