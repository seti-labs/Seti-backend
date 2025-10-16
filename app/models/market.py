from datetime import datetime
from app import db

class Market(db.Model):
    """Market model for caching blockchain market data"""
    __tablename__ = 'markets'
    
    id = db.Column(db.String(66), primary_key=True)  # Sui object ID
    question = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    end_time = db.Column(db.BigInteger, nullable=False)
    creator = db.Column(db.String(66), nullable=False)
    resolved = db.Column(db.Boolean, default=False)
    winning_outcome = db.Column(db.Integer)
    total_liquidity = db.Column(db.BigInteger, default=0)
    outcome_a_shares = db.Column(db.BigInteger, default=0)
    outcome_b_shares = db.Column(db.BigInteger, default=0)
    volume_24h = db.Column(db.BigInteger, default=0)
    created_timestamp = db.Column(db.BigInteger, nullable=False)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    tags = db.Column(db.JSON)
    
    # Metadata
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='market', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Market {self.id}: {self.question[:50]}>'
    
    def to_dict(self):
        """Convert market to dictionary"""
        return {
            'id': self.id,
            'question': self.question,
            'description': self.description,
            'end_time': self.end_time,
            'creator': self.creator,
            'resolved': self.resolved,
            'winning_outcome': self.winning_outcome,
            'total_liquidity': self.total_liquidity,
            'outcome_a_shares': self.outcome_a_shares,
            'outcome_b_shares': self.outcome_b_shares,
            'volume_24h': self.volume_24h,
            'created_timestamp': self.created_timestamp,
            'category': self.category,
            'image_url': self.image_url,
            'tags': self.tags,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def calculate_prices(self):
        """Calculate YES/NO prices based on shares"""
        total_shares = self.outcome_a_shares + self.outcome_b_shares
        if total_shares == 0:
            return {'yes_price': 50, 'no_price': 50}
        
        yes_price = round((self.outcome_b_shares / total_shares) * 100)
        no_price = round((self.outcome_a_shares / total_shares) * 100)
        
        return {'yes_price': yes_price, 'no_price': no_price}

