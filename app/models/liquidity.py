from datetime import datetime
from app import db

class LiquidityProvider(db.Model):
    """Track liquidity providers for each market"""
    __tablename__ = 'liquidity_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False)
    market_id = db.Column(db.String(66), db.ForeignKey('markets.id'), nullable=False)
    provider_address = db.Column(db.String(66), db.ForeignKey('users.address'), nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)
    shares_received = db.Column(db.BigInteger)
    timestamp = db.Column(db.BigInteger, nullable=False)
    withdrawn = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LiquidityProvider {self.provider_address[:10]}... on {self.market_id[:10]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_hash': self.transaction_hash,
            'market_id': self.market_id,
            'provider_address': self.provider_address,
            'amount': self.amount,
            'shares_received': self.shares_received,
            'timestamp': self.timestamp,
            'withdrawn': self.withdrawn,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LiquidityWithdrawal(db.Model):
    """Track liquidity withdrawals"""
    __tablename__ = 'liquidity_withdrawals'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False)
    market_id = db.Column(db.String(66), db.ForeignKey('markets.id'), nullable=False)
    provider_address = db.Column(db.String(66), db.ForeignKey('users.address'), nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_hash': self.transaction_hash,
            'market_id': self.market_id,
            'provider_address': self.provider_address,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

