from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Prediction, Market
from sqlalchemy import desc
from datetime import datetime

bp = Blueprint('users', __name__)

@bp.route('/<address>', methods=['GET'])
def get_user(address):
    """Get user profile by address"""
    try:
        user = User.query.get(address)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_dict = user.to_dict()
        
        # Add recent predictions
        recent_predictions = Prediction.query.filter_by(
            user_address=address
        ).order_by(desc(Prediction.timestamp)).limit(10).all()
        
        user_dict['recent_predictions'] = [p.to_dict() for p in recent_predictions]
        
        return jsonify({'user': user_dict}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>', methods=['PUT'])
def update_user(address):
    """Update user profile"""
    try:
        user = User.query.get(address)
        
        if not user:
            user = User(address=address)
            db.session.add(user)
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['username', 'avatar_url', 'bio']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>/predictions', methods=['GET'])
def get_user_predictions(address):
    """Get all predictions for a user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination = Prediction.query.filter_by(
            user_address=address
        ).order_by(desc(Prediction.timestamp)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        predictions = []
        for pred in pagination.items:
            pred_dict = pred.to_dict()
            # Include market info
            market = Market.query.get(pred.market_id)
            if market:
                pred_dict['market'] = {
                    'question': market.question,
                    'category': market.category,
                    'resolved': market.resolved,
                    'winning_outcome': market.winning_outcome
                }
            predictions.append(pred_dict)
        
        return jsonify({
            'predictions': predictions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>/stats', methods=['GET'])
def get_user_stats(address):
    """Get user statistics"""
    try:
        user = User.query.get(address)
        
        if not user:
            # Auto-create user for new addresses
            user = User(address=address)
            db.session.add(user)
            db.session.commit()
            
            # Return empty stats for new user
            stats = {
                'address': address,
                'total_predictions': 0,
                'total_volume': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'markets_created': 0,
                'category_breakdown': {},
                'first_seen': user.first_seen.isoformat() if user.first_seen else None,
                'last_active': user.last_active.isoformat() if user.last_active else None
            }
            
            return jsonify({'stats': stats}), 200
        
        # Update last_active timestamp for existing user
        user.last_active = datetime.utcnow()
        db.session.commit()
        
        # Calculate detailed stats
        predictions = Prediction.query.filter_by(user_address=address).all()
        
        total_predictions = len(predictions)
        total_volume = sum([p.amount for p in predictions])
        
        # Calculate wins (predictions on resolved markets)
        wins = 0
        losses = 0
        for pred in predictions:
            market = Market.query.get(pred.market_id)
            if market and market.resolved:
                if market.winning_outcome == pred.outcome:
                    wins += 1
                else:
                    losses += 1
        
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        # Category breakdown
        category_stats = {}
        for pred in predictions:
            market = Market.query.get(pred.market_id)
            if market and market.category:
                if market.category not in category_stats:
                    category_stats[market.category] = 0
                category_stats[market.category] += 1
        
        stats = {
            'address': address,
            'total_predictions': total_predictions,
            'total_volume': total_volume,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'markets_created': user.markets_created,
            'category_breakdown': category_stats,
            'first_seen': user.first_seen.isoformat() if user.first_seen else None,
            'last_active': user.last_active.isoformat() if user.last_active else None
        }
        
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>/activity', methods=['GET'])
def get_user_activity(address):
    """Get comprehensive user activity"""
    try:
        user = User.query.get(address)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update last_active timestamp
        user.last_active = datetime.utcnow()
        db.session.commit()
        
        # Get recent predictions with market info
        recent_predictions = Prediction.query.filter_by(
            user_address=address
        ).order_by(desc(Prediction.timestamp)).limit(20).all()
        
        activity = []
        for pred in recent_predictions:
            market = Market.query.get(pred.market_id)
            activity_item = {
                'type': 'prediction',
                'timestamp': pred.timestamp,
                'amount': pred.amount,
                'outcome': 'YES' if pred.outcome == 1 else 'NO',
                'market': {
                    'id': pred.market_id,
                    'question': market.question if market else 'Unknown Market',
                    'category': market.category if market else 'Unknown'
                },
                'transaction_hash': pred.transaction_hash
            }
            activity.append(activity_item)
        
        # Get created markets
        created_markets = Market.query.filter_by(creator=address).order_by(
            desc(Market.created_timestamp)
        ).limit(10).all()
        
        for market in created_markets:
            activity_item = {
                'type': 'market_created',
                'timestamp': market.created_timestamp,
                'market': {
                    'id': market.id,
                    'question': market.question,
                    'category': market.category,
                    'resolved': market.resolved
                }
            }
            activity.append(activity_item)
        
        # Sort by timestamp (most recent first)
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'user': user.to_dict(),
            'activity': activity[:50],  # Limit to 50 most recent activities
            'summary': {
                'total_predictions': user.total_predictions,
                'total_volume': user.total_volume,
                'markets_created': user.markets_created,
                'win_rate': round((user.win_count / (user.win_count + user.loss_count) * 100) if (user.win_count + user.loss_count) > 0 else 0, 2)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>/session', methods=['POST'])
def create_user_session(address):
    """Create or update user session"""
    try:
        user = User.query.get(address)
        
        if not user:
            # Create new user
            user = User(address=address)
            db.session.add(user)
        else:
            # Update existing user's last_active
            user.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Session created/updated successfully',
            'user': user.to_dict(),
            'is_new_user': user.total_predictions == 0 and user.markets_created == 0
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>/preferences', methods=['GET'])
def get_user_preferences(address):
    """Get user preferences and settings"""
    try:
        user = User.query.get(address)
        
        if not user:
            # Create new user with default preferences
            user = User(address=address)
            db.session.add(user)
            db.session.commit()
        
        preferences = {
            'username': user.username,
            'avatar_url': user.avatar_url,
            'bio': user.bio,
            'notification_settings': user.notification_settings or {},
            'theme_preference': user.theme_preference or 'system',
            'first_seen': user.first_seen.isoformat() if user.first_seen else None,
            'last_active': user.last_active.isoformat() if user.last_active else None
        }
        
        return jsonify({'preferences': preferences}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<address>/preferences', methods=['PUT'])
def update_user_preferences(address):
    """Update user preferences and settings"""
    try:
        user = User.query.get(address)
        
        if not user:
            user = User(address=address)
            db.session.add(user)
        
        data = request.get_json()
        
        # Update preferences
        if 'username' in data:
            user.username = data['username']
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        if 'bio' in data:
            user.bio = data['bio']
        
        if 'notification_settings' in data:
            user.notification_settings = data['notification_settings']
        
        if 'theme_preference' in data:
            user.theme_preference = data['theme_preference']
        
        # Update last_active timestamp
        user.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': {
                'username': user.username,
                'avatar_url': user.avatar_url,
                'bio': user.bio,
                'notification_settings': user.notification_settings,
                'theme_preference': user.theme_preference
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get user leaderboard"""
    try:
        sort_by = request.args.get('sort_by', 'total_volume')  # total_volume, total_predictions
        limit = min(request.args.get('limit', 50, type=int), 100)
        
        if sort_by == 'total_predictions':
            users = User.query.order_by(desc(User.total_predictions)).limit(limit).all()
        else:
            users = User.query.order_by(desc(User.total_volume)).limit(limit).all()
        
        leaderboard = [user.to_dict() for user in users]
        
        return jsonify({'leaderboard': leaderboard}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

