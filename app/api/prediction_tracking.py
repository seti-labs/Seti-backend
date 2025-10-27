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
        # Get all predictions for active markets
        active_predictions = db.session.query(Prediction).join(Market).filter(
            Market.resolved == False
        ).all()
        
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
            'predictions': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

