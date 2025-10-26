"""
Admin API endpoints for market management and system operations
"""
from flask import Blueprint, request, jsonify
from app import db, cache
from app.models import Market, Prediction, User
from app.services.contract_service import contract_service
from app.services.event_listener import event_listener
from app.services.sync_scheduler import sync_scheduler
from web3 import Web3
import os

bp = Blueprint('admin', __name__)

def require_admin_auth():
    """Simple admin authentication check"""
    # In production, implement proper admin authentication
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
            # Clear cache after successful sync
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

@bp.route('/sync/start', methods=['POST'])
def start_sync_scheduler():
    """Start the sync scheduler"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        sync_scheduler.start()
        event_listener.start_listening()
        return jsonify({'message': 'Sync scheduler and event listener started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/sync/stop', methods=['POST'])
def stop_sync_scheduler():
    """Stop the sync scheduler"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        sync_scheduler.stop()
        event_listener.stop_listening()
        return jsonify({'message': 'Sync scheduler and event listener stopped'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/markets/create', methods=['POST'])
def create_market():
    """Create a new market (admin only)"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['question', 'description', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate end_time
        import time
        if data['end_time'] <= int(time.time()):
            return jsonify({'error': 'End time must be in the future'}), 400
        
        # Create market on blockchain
        # Note: This would require admin wallet access
        # For now, we'll just create it in the database
        # In production, you'd call the smart contract here
        
        market_data = {
            'id': str(int(time.time())),  # Simple ID generation
            'question': data['question'],
            'description': data['description'],
            'end_time': data['end_time'],
            'resolved': False,
            'winning_outcome': None,
            'total_liquidity': 0,
            'outcome_a_shares': 0,
            'outcome_b_shares': 0,
            'yes_pool': 0,
            'no_pool': 0,
            'creator': 'admin',
            'category': data.get('category', 'General'),
            'image_url': data.get('image_url', ''),
            'tags': data.get('tags', [])
        }
        
        market = Market(**market_data)
        db.session.add(market)
        db.session.commit()
        
        # Clear cache
        cache.clear()
        
        return jsonify({
            'message': 'Market created successfully',
            'market': market.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/markets/<market_id>/resolve', methods=['POST'])
def resolve_market():
    """Resolve a market (admin only)"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        
        if not data or 'winning_outcome' not in data:
            return jsonify({'error': 'Missing winning_outcome'}), 400
        
        winning_outcome = data['winning_outcome']
        if winning_outcome not in [0, 1]:
            return jsonify({'error': 'winning_outcome must be 0 (NO) or 1 (YES)'}), 400
        
        market = Market.query.get(market_id)
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        if market.resolved:
            return jsonify({'error': 'Market already resolved'}), 400
        
        # Update market
        market.resolved = True
        market.winning_outcome = winning_outcome
        
        # Update all predictions for this market
        predictions = Prediction.query.filter_by(market_id=market_id).all()
        for prediction in predictions:
            if prediction.outcome == winning_outcome:
                # Winner - calculate payout
                # This is a simplified calculation
                # In production, you'd use the actual smart contract logic
                prediction.status = 'won'
            else:
                # Loser
                prediction.status = 'lost'
        
        db.session.commit()
        
        # Clear cache
        cache.clear()
        
        return jsonify({
            'message': 'Market resolved successfully',
            'market': market.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    auth_error = require_admin_auth()
    if auth_error:
        return auth_error
    
    try:
        # Check blockchain connection
        blockchain_status = {
            'connected': contract_service.w3.is_connected() if contract_service.w3 else False,
            'contract_address': contract_service.contract_address,
            'rpc_url': contract_service.rpc_url
        }
        
        # Get database stats
        db_stats = {
            'total_markets': Market.query.count(),
            'active_markets': Market.query.filter_by(resolved=False).count(),
            'resolved_markets': Market.query.filter_by(resolved=True).count(),
            'total_predictions': Prediction.query.count(),
            'total_users': User.query.count()
        }
        
        # Get sync stats
        sync_stats = sync_scheduler.get_stats()
        
        return jsonify({
            'blockchain': blockchain_status,
            'database': db_stats,
            'sync': sync_stats,
            'timestamp': int(time.time())
        }), 200
        
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
        
        # Check sync scheduler
        try:
            if sync_scheduler.is_running:
                health_status['services']['sync_scheduler'] = 'healthy'
            else:
                health_status['services']['sync_scheduler'] = 'stopped'
        except Exception as e:
            health_status['services']['sync_scheduler'] = f'unhealthy: {str(e)}'
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': int(time.time())
        }), 500
