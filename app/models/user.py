from datetime import datetime
from app import db

class User(db.Model):
    """User model for tracking user activity"""
    __tablename__ = 'users'
    
    address = db.Column(db.String(66), primary_key=True)  # Sui wallet address
    username = db.Column(db.String(100))
    email = db.Column(db.String(255))
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    
    # Stats
    total_predictions = db.Column(db.Integer, default=0)
    total_volume = db.Column(db.BigInteger, default=0)
    markets_created = db.Column(db.Integer, default=0)
    
    # Metadata
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.address}>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'address': self.address,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'total_predictions': self.total_predictions,
            'total_volume': self.total_volume,
            'markets_created': self.markets_created,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
    
    def update_stats(self):
        """Update user statistics"""
        self.total_predictions = self.predictions.count()
        self.total_volume = sum([p.amount for p in self.predictions.all()])
        self.last_active = datetime.utcnow()

