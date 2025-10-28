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
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['username', 'avatar_url', 'bio']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Update last active timestamp
        user.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500