from datetime import datetime
from app import db

class Comment(db.Model):
    """User comments on markets"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.String(66), db.ForeignKey('markets.id'), nullable=False)
    user_address = db.Column(db.String(66), db.ForeignKey('users.address'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # For replies
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.user_address[:10]}...>'
    
    def to_dict(self, include_replies=False):
        data = {
            'id': self.id,
            'market_id': self.market_id,
            'user_address': self.user_address,
            'content': self.content,
            'parent_id': self.parent_id,
            'likes': self.likes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_replies and self.replies:
            data['replies'] = [r.to_dict() for r in self.replies]
        
        return data

class Favorite(db.Model):
    """User favorites/watchlist"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_address = db.Column(db.String(66), db.ForeignKey('users.address'), nullable=False)
    market_id = db.Column(db.String(66), db.ForeignKey('markets.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_address', 'market_id', name='unique_favorite'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_address': self.user_address,
            'market_id': self.market_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

