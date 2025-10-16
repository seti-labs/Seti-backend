from datetime import datetime
from app import db

class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_address = db.Column(db.String(66), db.ForeignKey('users.address'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # market_resolved, prediction_won, comment_reply, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(500))  # Link to relevant page
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id} for {self.user_address[:10]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_address': self.user_address,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ActivityFeed(db.Model):
    """Platform-wide activity feed"""
    __tablename__ = 'activity_feed'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)  # market_created, prediction_placed, market_resolved
    user_address = db.Column(db.String(66), db.ForeignKey('users.address'))
    market_id = db.Column(db.String(66), db.ForeignKey('markets.id'))
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'))
    data = db.Column(db.JSON)  # Additional contextual data
    timestamp = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Activity {self.activity_type} by {self.user_address[:10] if self.user_address else "system"}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'user_address': self.user_address,
            'market_id': self.market_id,
            'prediction_id': self.prediction_id,
            'data': self.data,
            'timestamp': self.timestamp,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

