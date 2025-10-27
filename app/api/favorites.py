from flask import Blueprint, request, jsonify
from app import db
from app.models import Favorite, Market, User
from sqlalchemy import desc
from datetime import datetime

bp = Blueprint('favorites', __name__)

@bp.route('/<user_address>', methods=['GET'])
def get_user_favorites(user_address):
    """Get all favorites for a user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get user's favorites with market details
        pagination = db.session.query(Favorite, Market).join(
            Market, Favorite.market_id == Market.id
        ).filter(
            Favorite.user_address == user_address
        ).order_by(desc(Favorite.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        favorites = []
        for favorite, market in pagination.items:
            favorites.append({
                'id': favorite.id,
                'market_id': favorite.market_id,
                'created_at': favorite.created_at.isoformat() if favorite.created_at else None,
                'market': {
                    'id': market.id,
                    'question': market.question,
                    'description': market.description,
                    'category': market.category,
                    'end_time': market.end_time,
                    'resolved': market.resolved,
                    'total_liquidity': market.total_liquidity,
                    'outcome_a_shares': market.outcome_a_shares,
                    'outcome_b_shares': market.outcome_b_shares,
                    'volume_24h': market.volume_24h,
                    'image_url': market.image_url,
                    'tags': market.tags
                }
            })
        
        return jsonify({
            'favorites': favorites,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<user_address>/<market_id>', methods=['POST'])
def add_favorite(user_address, market_id):
    """Add a market to user's favorites"""
    try:
        # Check if market exists
        market = Market.query.get(market_id)
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        # Check if already favorited
        existing = Favorite.query.filter_by(
            user_address=user_address,
            market_id=market_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Market already in favorites'}), 409
        
        # Create new favorite
        favorite = Favorite(
            user_address=user_address,
            market_id=market_id
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'message': 'Market added to favorites',
            'favorite': favorite.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<user_address>/<market_id>', methods=['DELETE'])
def remove_favorite(user_address, market_id):
    """Remove a market from user's favorites"""
    try:
        favorite = Favorite.query.filter_by(
            user_address=user_address,
            market_id=market_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Market removed from favorites'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<user_address>/<market_id>', methods=['GET'])
def check_favorite(user_address, market_id):
    """Check if a market is favorited by user"""
    try:
        favorite = Favorite.query.filter_by(
            user_address=user_address,
            market_id=market_id
        ).first()
        
        return jsonify({
            'is_favorite': favorite is not None,
            'favorite_id': favorite.id if favorite else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<user_address>/toggle', methods=['POST'])
def toggle_favorite(user_address):
    """Toggle favorite status for a market"""
    try:
        data = request.get_json()
        market_id = data.get('market_id')
        
        if not market_id:
            return jsonify({'error': 'market_id is required'}), 400
        
        # Check if market exists
        market = Market.query.get(market_id)
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        # Check current status
        favorite = Favorite.query.filter_by(
            user_address=user_address,
            market_id=market_id
        ).first()
        
        if favorite:
            # Remove from favorites
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({
                'message': 'Market removed from favorites',
                'is_favorite': False
            }), 200
        else:
            # Add to favorites
            favorite = Favorite(
                user_address=user_address,
                market_id=market_id
            )
            db.session.add(favorite)
            db.session.commit()
            return jsonify({
                'message': 'Market added to favorites',
                'is_favorite': True,
                'favorite': favorite.to_dict()
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
