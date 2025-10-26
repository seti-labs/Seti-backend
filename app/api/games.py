from flask import Blueprint, jsonify, request
from app import db
from app.models import Game
from app.services.game_service import game_service
from sqlalchemy import func

games_bp = Blueprint('games', __name__)

@games_bp.route('/games', methods=['GET'])
def get_games():
    """Get all games with optional filters"""
    try:
        league = request.args.get('league')
        status = request.args.get('status')  # scheduled, live, finished
        league_id = request.args.get('league_id', type=int)
        
        query = Game.query
        
        if league:
            query = query.filter(func.lower(Game.league).like(f'%{league.lower()}%'))
        
        if league_id:
            query = query.filter(Game.league_id == league_id)
        
        if status:
            if status == 'scheduled':
                query = query.filter(Game.status.in_(['NS', 'TBD']))
            elif status == 'live':
                query = query.filter(Game.status.in_(['LIVE', 'HT', '1H', '2H']))
            elif status == 'finished':
                query = query.filter(Game.status == 'FT')
        
        games = query.order_by(Game.kickoff_time.asc()).all()
        
        return jsonify({
            'games': [game.to_dict() for game in games],
            'count': len(games)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/games/<int:fixture_id>', methods=['GET'])
def get_game(fixture_id):
    """Get specific game by fixture_id"""
    try:
        game = Game.query.filter_by(fixture_id=fixture_id).first()
        
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        return jsonify({'game': game.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/games/leagues', methods=['GET'])
def get_leagues():
    """Get list of available leagues"""
    try:
        leagues = db.session.query(
            Game.league,
            Game.league_id,
            func.count(Game.id).label('count')
        ).group_by(Game.league, Game.league_id).all()
        
        return jsonify({
            'leagues': [
                {
                    'name': league,
                    'id': league_id,
                    'fixture_count': count
                }
                for league, league_id, count in leagues
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/games/sync', methods=['POST'])
def sync_games():
    """Manually trigger game sync from API"""
    try:
        fixtures = game_service.fetch_upcoming_fixtures()
        
        synced = 0
        for fixture in fixtures:
            game = game_service.sync_game_to_db(fixture)
            if game:
                synced += 1
        
        return jsonify({
            'message': f'Synced {synced} fixtures',
            'total': len(fixtures)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
