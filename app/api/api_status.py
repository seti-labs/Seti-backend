from flask import Blueprint, jsonify, request
from app.services.market_sports_service import market_sports_service
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('api_status', __name__, url_prefix='/api/v1/status')

@bp.route('/rate-limits', methods=['GET'])
def get_rate_limits():
    """Get current API rate limit status"""
    try:
        status = market_sports_service.get_rate_limit_status()
        return jsonify({
            'success': True,
            'rate_limits': status
        }), 200
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear API cache"""
    try:
        market_sports_service.clear_api_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if API key is configured
        api_key_configured = bool(market_sports_service.api_key)
        
        # Get rate limit status
        rate_limit_status = market_sports_service.get_rate_limit_status()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'api_key_configured': api_key_configured,
            'rate_limits': rate_limit_status,
            'timestamp': market_sports_service.api_client.last_reset_date.isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500
