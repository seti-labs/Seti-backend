from flask import Blueprint, request, jsonify
from app import db
from app.models import Comment, Market, User
from sqlalchemy import desc

bp = Blueprint('comments', __name__)

@bp.route('', methods=['GET'])
def get_comments():
    """Get comments with filtering"""
    try:
        market_id = request.args.get('market_id')
        user_address = request.args.get('user_address')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        query = Comment.query
        
        if market_id:
            query = query.filter(Comment.market_id == market_id)
        
        if user_address:
            query = query.filter(Comment.user_address == user_address)
        
        # Get top-level comments (no parent)
        query = query.filter(Comment.parent_id == None)
        query = query.order_by(desc(Comment.created_at))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        comments = [c.to_dict(include_replies=True) for c in pagination.items]
        
        return jsonify({
            'comments': comments,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
def create_comment():
    """Create a new comment"""
    try:
        data = request.get_json()
        
        required = ['market_id', 'user_address', 'content']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        comment = Comment(
            market_id=data['market_id'],
            user_address=data['user_address'],
            content=data['content'],
            parent_id=data.get('parent_id')
        )
        
        db.session.add(comment)
        
        # Update market comment count
        market = Market.query.get(data['market_id'])
        if market:
            market.comment_count = (market.comment_count or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

