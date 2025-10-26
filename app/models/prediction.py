from datetime import datetime
from app import db

class Prediction(db.Model):
    """Prediction model matching smart contract Bet struct"""
    __tablename__ = 'predictions'
    
    # Smart contract Bet struct fields
    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False)
    market_id = db.Column(db.String(66), db.ForeignKey('markets.id'), nullable=False)
    user_address = db.Column(db.String(66), db.ForeignKey('users.address'), nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)  # Bet amount
    outcome = db.Column(db.Integer, nullable=False)    # 0 = NO, 1 = YES
    claimed = db.Column(db.Boolean, default=False)     # Payout claimed
    timestamp = db.Column(db.BigInteger, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.id}: {self.user_address[:10]}... on {self.market_id[:10]}...>'
    
    def to_dict(self):
        """Convert prediction to dictionary matching smart contract Bet struct"""
        return {
            'id': self.id,
            'transaction_hash': self.transaction_hash,
            'market_id': self.market_id,
            'user_address': self.user_address,
            'amount': self.amount,
            'outcome': self.outcome,
            'outcome_label': 'YES' if self.outcome == 1 else 'NO',
            'claimed': self.claimed,
            'timestamp': self.timestamp,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

