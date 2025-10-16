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
    win_count = db.Column(db.Integer, default=0)
    loss_count = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.BigInteger, default=0)  # Profit and Loss
    
    # Engagement
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    
    # Gamification
    level = db.Column(db.Integer, default=1)
    experience_points = db.Column(db.Integer, default=0)
    badges = db.Column(db.JSON, default=list)  # Array of badge IDs
    
    # Preferences
    notification_settings = db.Column(db.JSON, default=dict)
    theme_preference = db.Column(db.String(20), default='system')  # light, dark, system
    
    # Metadata
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    liquidity_provided = db.relationship('LiquidityProvider', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    activity_feed = db.relationship('ActivityFeed', backref='user', lazy='dynamic')
    
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

