from datetime import datetime
from app import db

class Market(db.Model):
    """Market model matching smart contract structure"""
    __tablename__ = 'markets'
    
    # Smart contract fields (exact match)
    id = db.Column(db.String(66), primary_key=True)  # Market ID
    question = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    end_time = db.Column(db.BigInteger, nullable=False)  # endTime
    creator = db.Column(db.String(66), nullable=False)
    resolved = db.Column(db.Boolean, default=False)
    winning_outcome = db.Column(db.Integer)  # winningOutcome (0=NO, 1=YES)
    total_liquidity = db.Column(db.BigInteger, default=0)
    outcome_a_shares = db.Column(db.BigInteger, default=0)  # outcomeAShares
    outcome_b_shares = db.Column(db.BigInteger, default=0)  # outcomeBShares
    yes_pool = db.Column(db.BigInteger, default=0)  # yesPool
    no_pool = db.Column(db.BigInteger, default=0)   # noPool
    volume_24h = db.Column(db.BigInteger, default=0)  # 24h volume
    created_timestamp = db.Column(db.BigInteger, nullable=False)  # created timestamp
    category = db.Column(db.String(50))  # market category
    image_url = db.Column(db.String(500))  # market image
    tags = db.Column(db.JSON)  # market tags
    
    # Web2.5 enhancements (not in smart contract)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = db.Column(db.DateTime, default=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)
    participant_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    slug = db.Column(db.String(200), unique=True)
    featured = db.Column(db.Boolean, default=False)
    trending_score = db.Column(db.Float, default=0.0)
    
    # Sports-specific fields
    home_team = db.Column(db.String(100))
    away_team = db.Column(db.String(100))
    league = db.Column(db.String(100))
    game_status = db.Column(db.String(20), default='NS')  # NS, LIVE, FT
    kickoff_time = db.Column(db.BigInteger)  # Unix timestamp
    current_score = db.Column(db.JSON)  # {'home': 0, 'away': 0}
    team_logos = db.Column(db.JSON)  # {'home': 'url', 'away': 'url'}
    venue = db.Column(db.String(200))
    weather = db.Column(db.String(50))
    odds = db.Column(db.JSON)  # {'home': 1.5, 'away': 2.1, 'draw': 3.2}
    arbitrage_opportunity = db.Column(db.Boolean, default=False)
    market_confidence = db.Column(db.Float, default=0.0)  # 0-1 confidence score
    
    # Relationships
    predictions = db.relationship('Prediction', backref='market', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='market', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='market', lazy='dynamic', cascade='all, delete-orphan')
    liquidity_providers = db.relationship('LiquidityProvider', backref='market', lazy='dynamic', cascade='all, delete-orphan')
    activity_feed = db.relationship('ActivityFeed', backref='market', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Market {self.id}: {self.question[:50]}>'
    
    def to_dict(self):
        """Convert market to dictionary matching smart contract structure"""
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
            'yes_pool': self.yes_pool,
            'no_pool': self.no_pool,
            'volume_24h': self.volume_24h,
            'created_timestamp': self.created_timestamp,
            'category': self.category,
            'image_url': self.image_url,
            'tags': self.tags,
            'view_count': self.view_count,
            'participant_count': self.participant_count,
            'comment_count': self.comment_count,
            'favorite_count': self.favorite_count,
            'slug': self.slug,
            'featured': self.featured,
            'trending_score': self.trending_score,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            # Sports-specific fields
            'home_team': self.home_team,
            'away_team': self.away_team,
            'league': self.league,
            'game_status': self.game_status,
            'kickoff_time': self.kickoff_time,
            'current_score': self.current_score,
            'team_logos': self.team_logos,
            'venue': self.venue,
            'weather': self.weather,
            'odds': self.odds,
            'arbitrage_opportunity': self.arbitrage_opportunity,
            'market_confidence': self.market_confidence
        }
    
    def calculate_prices(self):
        """Calculate YES/NO prices based on smart contract pools"""
        total_liquidity = self.yes_pool + self.no_pool
        if total_liquidity == 0:
            return {'yes_price': 50, 'no_price': 50}
        
        yes_price = round((self.yes_pool / total_liquidity) * 100)
        no_price = round((self.no_pool / total_liquidity) * 100)
        
        return {'yes_price': yes_price, 'no_price': no_price}

