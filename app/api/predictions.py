from flask import Blueprint, request, jsonify
from app import db
from app.models import Prediction, Market, User
from sqlalchemy import desc
from datetime import datetime

bp = Blueprint('predictions', __name__)

@bp.route('', methods=['GET'])
def get_predictions():
    """Get predictions with filtering"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        market_id = request.args.get('market_id')
        user_address = request.args.get('user_address')
        outcome = request.args.get('outcome', type=int)
        
        # Build query
        query = Prediction.query
        
        if market_id:
            query = query.filter(Prediction.market_id == market_id)
        
        if user_address:
            query = query.filter(Prediction.user_address == user_address)
        
        if outcome is not None:
            query = query.filter(Prediction.outcome == outcome)
        
        # Order by most recent
        query = query.order_by(desc(Prediction.timestamp))
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        predictions = [p.to_dict() for p in pagination.items]
        
        return jsonify({
            'predictions': predictions,
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

@bp.route('/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Get a specific prediction by ID"""
    try:
        prediction = Prediction.query.get(prediction_id)
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        return jsonify({'prediction': prediction.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
def create_prediction():
    """Create a new prediction record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['market_id', 'user_address', 'outcome', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate market exists
        market = Market.query.get(data['market_id'])
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        # Validate market is not resolved
        if market.resolved:
            return jsonify({'error': 'Cannot predict on resolved market'}), 400
        
        # Validate outcome and convert to integer
        if data['outcome'] not in ['YES', 'NO']:
            return jsonify({'error': 'Outcome must be YES or NO'}), 400
        
        outcome_int = 1 if data['outcome'] == 'YES' else 0
        
        # Generate transaction hash if not provided (for simulation)
        transaction_hash = data.get('transaction_hash', f'sim_{data["user_address"]}_{int(datetime.utcnow().timestamp())}')
        
        # Check if prediction already exists (by user, market, and outcome)
        existing = Prediction.query.filter_by(
            market_id=data['market_id'],
            user_address=data['user_address'],
            outcome=outcome_int
        ).first()
        
        if existing:
            return jsonify({'error': 'User already has a prediction on this outcome for this market'}), 409
        
        # Create prediction matching smart contract Bet struct
        prediction = Prediction(
            transaction_hash=transaction_hash,
            market_id=data['market_id'],
            user_address=data['user_address'],
            outcome=outcome_int,
            amount=data['amount'],
            claimed=False,  # Matching smart contract Bet.claimed
            timestamp=int(datetime.utcnow().timestamp())
        )
        
        db.session.add(prediction)
        
        # Update market liquidity matching smart contract
        if outcome_int == 1:  # YES
            market.yes_pool += data['amount']
            market.outcome_b_shares += data['amount']
        else:  # NO
            market.no_pool += data['amount']
            market.outcome_a_shares += data['amount']
        market.total_liquidity += data['amount']
        
        # Update or create user
        user = User.query.get(data['user_address'])
        if not user:
            user = User(address=data['user_address'])
            db.session.add(user)
        
        # Update user stats and activity
        user.update_stats()
        user.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Prediction created successfully',
            'prediction': prediction.to_dict(),
            'receipt': {
                'transaction_hash': transaction_hash,
                'market_id': data['market_id'],
                'outcome': data['outcome'],
                'amount': data['amount'],
                'claimed': False,
                'timestamp': prediction.timestamp
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/recent', methods=['GET'])
def get_recent_predictions():
    """Get recent predictions across all markets"""
    try:
        limit = min(request.args.get('limit', 50, type=int), 100)
        
        predictions = Prediction.query.order_by(
            desc(Prediction.timestamp)
        ).limit(limit).all()
        
        prediction_list = []
        for prediction in predictions:
            pred_dict = prediction.to_dict()
            # Include market info
            market = Market.query.get(prediction.market_id)
            if market:
                pred_dict['market'] = {
                    'question': market.question,
                    'category': market.category
                }
            prediction_list.append(pred_dict)
        
        return jsonify({'predictions': prediction_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

