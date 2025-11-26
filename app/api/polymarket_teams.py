from flask import Blueprint, jsonify, request
from app.services.polymarket_teams_service import polymarket_teams_service

bp = Blueprint('polymarket_teams', __name__)

@bp.route('/teams', methods=['GET'])
def get_teams():
    """
    Get teams from Polymarket Gamma API
    Query params:
        - league: Filter by league (optional)
        - search: Search by team name (optional)
    """
    try:
        league = request.args.get('league')
        search = request.args.get('search')
        
        if search:
            teams = polymarket_teams_service.search_teams(search)
        else:
            teams = polymarket_teams_service.fetch_teams(league=league)
        
        return jsonify({
            'success': True,
            'teams': teams,
            'count': len(teams)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/teams/by-league', methods=['GET'])
def get_teams_by_league():
    """Get teams grouped by league"""
    try:
        teams_by_league = polymarket_teams_service.get_teams_by_league()
        
        return jsonify({
            'success': True,
            'teams_by_league': teams_by_league,
            'league_count': len(teams_by_league)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/teams/leagues', methods=['GET'])
def get_leagues_summary():
    """Get summary of all leagues with team counts"""
    try:
        summary = polymarket_teams_service.get_leagues_summary()
        
        return jsonify({
            'success': True,
            'leagues': summary,
            'total_leagues': len(summary)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/teams/matchups/<league>', methods=['GET'])
def get_potential_matchups(league):
    """
    Get potential matchups for a league
    Query params:
        - limit: Max number of matchups (default: 10)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        matchups = polymarket_teams_service.create_potential_matchups(league, limit=limit)
        
        return jsonify({
            'success': True,
            'league': league,
            'matchups': matchups,
            'count': len(matchups)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

