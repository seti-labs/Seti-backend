"""
Admin API endpoints for market management and system operations
"""
from flask import Blueprint, request, jsonify
from app import db, cache
from app.models import Market, Prediction, User
from app.services.contract_service import contract_service
from app.services.event_listener import event_listener
from app.services.sync_scheduler import sync_scheduler
import os
import time

bp = Blueprint('admin', __name__)

def require_admin_auth():
    """Simple admin authentication check"""
    admin_key = request.headers.get('X-Admin-Key')
    expected_key = os.getenv('ADMIN_KEY', 'admin-secret-key')
    
    if admin_key != expected_key:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return None

@bp.route('/sync', methods=['POST'])
def sync_all_data():
    """Force sync all data from blockchain"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        result = sync_scheduler.force_sync()
        
        if result['success']:
            cache.clear()
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/sync/status', methods=['GET'])
def get_sync_status():
    """Get sync scheduler status"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        stats = sync_scheduler.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/system/health', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': int(time.time()),
            'services': {}
        }
        
        # Check database
        try:
            db.session.execute('SELECT 1')
            health_status['services']['database'] = 'healthy'
        except Exception as e:
            health_status['services']['database'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Check blockchain
        try:
            if contract_service.w3 and contract_service.w3.is_connected():
                health_status['services']['blockchain'] = 'healthy'
            else:
                health_status['services']['blockchain'] = 'unhealthy: not connected'
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['services']['blockchain'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': int(time.time())
        }), 500