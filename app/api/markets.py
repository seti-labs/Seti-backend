from flask import Blueprint, request, jsonify
from app import db, cache
from app.models import Market
from app.services.sui_service import SuiService
from sqlalchemy import desc, func

bp = Blueprint('markets', __name__)
sui_service = SuiService()

@bp.route('', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_markets():
    """Get all markets with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        status = request.args.get('status')  # active, resolved
        sort_by = request.args.get('sort_by', 'created_timestamp')  # volume_24h, total_liquidity, created_timestamp
        search = request.args.get('search')
        
        # Build query
        query = Market.query
        
        # Apply filters
        if category and category != 'All':
            query = query.filter(Market.category == category)
        
        if status == 'active':
            query = query.filter(Market.resolved == False)
        elif status == 'resolved':
            query = query.filter(Market.resolved == True)
        
        if search:
            query = query.filter(
                db.or_(
                    Market.question.ilike(f'%{search}%'),
                    Market.description.ilike(f'%{search}%')
                )
            )
        
        # Apply sorting
        if sort_by == 'volume_24h':
            query = query.order_by(desc(Market.volume_24h))
        elif sort_by == 'total_liquidity':
            query = query.order_by(desc(Market.total_liquidity))
        else:
            query = query.order_by(desc(Market.created_timestamp))
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        markets = []
        for market in pagination.items:
            market_dict = market.to_dict()
            market_dict['prices'] = market.calculate_prices()
            markets.append(market_dict)
        
        return jsonify({
            'markets': markets,
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

@bp.route('/<market_id>', methods=['GET'])
@cache.cached(timeout=30)
def get_market(market_id):
    """Get a specific market by ID"""
    try:
        market = Market.query.get(market_id)
        
        if not market:
            # Try fetching from blockchain
            market_data = sui_service.get_market(market_id)
            if market_data:
                market = Market(**market_data)
                db.session.add(market)
                db.session.commit()
            else:
                return jsonify({'error': 'Market not found'}), 404
        
        market_dict = market.to_dict()
        market_dict['prices'] = market.calculate_prices()
        
        return jsonify({'market': market_dict}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/sync', methods=['POST'])
def sync_markets():
    """Sync markets from blockchain (admin endpoint)"""
    try:
        markets_data = sui_service.fetch_all_markets()
        
        synced_count = 0
        for market_data in markets_data:
            market = Market.query.get(market_data['id'])
            if market:
                # Update existing market
                for key, value in market_data.items():
                    if hasattr(market, key):
                        setattr(market, key, value)
            else:
                # Create new market
                market = Market(**market_data)
                db.session.add(market)
            
            synced_count += 1
        
        db.session.commit()
        cache.clear()
        
        return jsonify({
            'message': 'Markets synced successfully',
            'synced_count': synced_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
@cache.cached(timeout=300)
def get_categories():
    """Get all market categories with counts"""
    try:
        categories = db.session.query(
            Market.category,
            func.count(Market.id).label('count')
        ).group_by(Market.category).all()
        
        category_list = [
            {'name': cat, 'count': count}
            for cat, count in categories
        ]
        
        return jsonify({'categories': category_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/featured', methods=['GET'])
@cache.cached(timeout=120)
def get_featured_markets():
    """Get featured markets (high volume/liquidity)"""
    try:
        markets = Market.query.filter(
            Market.resolved == False
        ).order_by(
            desc(Market.total_liquidity)
        ).limit(10).all()
        
        market_list = []
        for market in markets:
            market_dict = market.to_dict()
            market_dict['prices'] = market.calculate_prices()
            market_list.append(market_dict)
        
        return jsonify({'markets': market_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

