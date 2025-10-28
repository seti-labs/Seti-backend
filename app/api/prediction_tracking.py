from flask import Blueprint, request, jsonify
from app import db
from app.models import Prediction, Market, User
from app.services.prediction_tracking_service import prediction_tracking_service

bp = Blueprint('prediction_tracking', __name__)

@bp.route('/predictions/<int:prediction_id>/status', methods=['GET'])
def get_prediction_status(prediction_id):
    """Get current status of a specific prediction"""
    try:
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        status = prediction_tracking_service.get_prediction_status(prediction)
        
        return jsonify({
            'success': True,
            'prediction_id': prediction_id,
            'status': status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<user_address>/predictions/status', methods=['GET'])
def get_user_predictions_status(user_address):
    """Get status of all predictions for a user"""
    try:
        statuses = prediction_tracking_service.get_user_predictions_status(user_address)
        
        return jsonify({
            'success': True,
            'user_address': user_address,
            'predictions': statuses
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/predictions/<int:prediction_id>/tracking', methods=['POST'])
def update_prediction_tracking(prediction_id):
    """Update tracking data for a specific prediction"""
    try:
        result = prediction_tracking_service.update_prediction_tracking(prediction_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/markets/<int:market_id>/analytics', methods=['GET'])
def get_market_analytics(market_id):
    """Get analytics for a specific market"""
    try:
        analytics = prediction_tracking_service.get_market_analytics(market_id)
        
        if 'error' in analytics:
            return jsonify(analytics), 404
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/predictions/active', methods=['GET'])
def get_active_predictions():
    """Get all active predictions across all users"""
    try:
        # Get query parameters for filtering
        user_address = request.args.get('user_address')
        market_id = request.args.get('market_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = db.session.query(Prediction).join(Market).filter(
            Market.resolved == False
        )
        
        if user_address:
            query = query.filter(Prediction.user_address == user_address)
        if market_id:
            query = query.filter(Prediction.market_id == market_id)
        
        # Apply pagination
        active_predictions = query.offset(offset).limit(limit).all()
        
        results = []
        for prediction in active_predictions:
            status = prediction_tracking_service.get_prediction_status(prediction)
            results.append({
                'prediction_id': prediction.id,
                'user_address': prediction.user_address,
                'market_id': prediction.market_id,
                'market_question': prediction.market.question if prediction.market else 'Unknown Market',
                'outcome': prediction.outcome,
                'amount': prediction.amount / 1_000_000_000,
                'shares': prediction.shares / 1_000_000_000,
                'timestamp': prediction.timestamp,
                'status': status
            })
        
        return jsonify({
            'success': True,
            'predictions': results,
            'total': query.count(),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/predictions/live', methods=['GET'])
def get_live_predictions():
    """Get live predictions with real-time updates"""
    try:
        # Get recent predictions (last 24 hours)
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(hours=24)
        
        recent_predictions = db.session.query(Prediction).join(Market).filter(
            Prediction.timestamp >= since
        ).order_by(Prediction.timestamp.desc()).limit(100).all()
        
        results = []
        for prediction in recent_predictions:
            status = prediction_tracking_service.get_prediction_status(prediction)
            results.append({
                'prediction_id': prediction.id,
                'user_address': prediction.user_address,
                'market_id': prediction.market_id,
                'market_question': prediction.market.question if prediction.market else 'Unknown Market',
                'outcome': prediction.outcome,
                'amount': prediction.amount / 1_000_000_000,
                'shares': prediction.shares / 1_000_000_000,
                'timestamp': prediction.timestamp,
                'status': status,
                'is_live': not prediction.market.resolved if prediction.market else False
            })
        
        return jsonify({
            'success': True,
            'predictions': results,
            'last_updated': datetime.utcnow().isoformat(),
            'total_count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/predictions/recent', methods=['GET'])
def get_recent_predictions():
    """Get most recent predictions for live feed"""
    try:
        limit = int(request.args.get('limit', 20))
        
        recent_predictions = db.session.query(Prediction).join(Market).order_by(
            Prediction.timestamp.desc()
        ).limit(limit).all()
        
        results = []
        for prediction in recent_predictions:
            status = prediction_tracking_service.get_prediction_status(prediction)
            results.append({
                'prediction_id': prediction.id,
                'user_address': prediction.user_address,
                'market_id': prediction.market_id,
                'market_question': prediction.market.question if prediction.market else 'Unknown Market',
                'outcome': prediction.outcome,
                'amount': prediction.amount / 1_000_000_000,
                'shares': prediction.shares / 1_000_000_000,
                'timestamp': prediction.timestamp,
                'status': status,
                'is_resolved': prediction.market.resolved if prediction.market else False
            })
        
        return jsonify({
            'success': True,
            'predictions': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

