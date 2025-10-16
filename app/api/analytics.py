from flask import Blueprint, request, jsonify
from app import db, cache
from app.models import Market, Prediction, User
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('analytics', __name__)

@bp.route('/overview', methods=['GET'])
@cache.cached(timeout=300)
def get_overview():
    """Get platform overview statistics"""
    try:
        # Total markets
        total_markets = Market.query.count()
        active_markets = Market.query.filter_by(resolved=False).count()
        resolved_markets = Market.query.filter_by(resolved=True).count()
        
        # Total volume
        total_volume = db.session.query(
            func.sum(Market.volume_24h)
        ).scalar() or 0
        
        # Total liquidity
        total_liquidity = db.session.query(
            func.sum(Market.total_liquidity)
        ).scalar() or 0
        
        # Total predictions
        total_predictions = Prediction.query.count()
        
        # Total users
        total_users = User.query.count()
        
        # Active users (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_users = User.query.filter(
            User.last_active >= seven_days_ago
        ).count()
        
        return jsonify({
            'overview': {
                'total_markets': total_markets,
                'active_markets': active_markets,
                'resolved_markets': resolved_markets,
                'total_volume': total_volume,
                'total_liquidity': total_liquidity,
                'total_predictions': total_predictions,
                'total_users': total_users,
                'active_users_7d': active_users
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/markets/top', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_top_markets():
    """Get top markets by various metrics"""
    try:
        metric = request.args.get('metric', 'volume')  # volume, liquidity, predictions
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        if metric == 'liquidity':
            markets = Market.query.order_by(desc(Market.total_liquidity)).limit(limit).all()
        elif metric == 'predictions':
            # Count predictions per market
            market_ids = db.session.query(
                Prediction.market_id,
                func.count(Prediction.id).label('count')
            ).group_by(Prediction.market_id).order_by(desc('count')).limit(limit).all()
            
            markets = []
            for market_id, count in market_ids:
                market = Market.query.get(market_id)
                if market:
                    market_dict = market.to_dict()
                    market_dict['prediction_count'] = count
                    markets.append(market_dict)
            
            return jsonify({'markets': markets}), 200
        else:
            markets = Market.query.order_by(desc(Market.volume_24h)).limit(limit).all()
        
        market_list = [m.to_dict() for m in markets]
        
        return jsonify({'markets': market_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/categories/stats', methods=['GET'])
@cache.cached(timeout=300)
def get_category_stats():
    """Get statistics by category"""
    try:
        stats = db.session.query(
            Market.category,
            func.count(Market.id).label('market_count'),
            func.sum(Market.volume_24h).label('total_volume'),
            func.sum(Market.total_liquidity).label('total_liquidity')
        ).group_by(Market.category).all()
        
        category_stats = []
        for cat, count, volume, liquidity in stats:
            category_stats.append({
                'category': cat,
                'market_count': count,
                'total_volume': volume or 0,
                'total_liquidity': liquidity or 0
            })
        
        # Sort by volume
        category_stats.sort(key=lambda x: x['total_volume'], reverse=True)
        
        return jsonify({'categories': category_stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/activity/recent', methods=['GET'])
@cache.cached(timeout=60)
def get_recent_activity():
    """Get recent platform activity"""
    try:
        limit = min(request.args.get('limit', 20, type=int), 100)
        
        # Get recent predictions with market info
        predictions = Prediction.query.order_by(
            desc(Prediction.timestamp)
        ).limit(limit).all()
        
        activity = []
        for pred in predictions:
            market = Market.query.get(pred.market_id)
            if market:
                activity.append({
                    'type': 'prediction',
                    'prediction': pred.to_dict(),
                    'market': {
                        'id': market.id,
                        'question': market.question,
                        'category': market.category
                    },
                    'timestamp': pred.timestamp
                })
        
        return jsonify({'activity': activity}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/volume/history', methods=['GET'])
@cache.cached(timeout=300)
def get_volume_history():
    """Get volume history (placeholder for time-series data)"""
    try:
        # This would require a time-series table or more complex aggregation
        # For now, return current 24h volume by category
        
        volume_data = db.session.query(
            Market.category,
            func.sum(Market.volume_24h).label('volume')
        ).group_by(Market.category).all()
        
        history = [
            {'category': cat, 'volume': vol or 0}
            for cat, vol in volume_data
        ]
        
        return jsonify({'volume_history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

