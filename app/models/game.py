from datetime import datetime
from app import db

class Game(db.Model):
    """Model for sports games/fixtures linked to prediction markets"""
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    
    # Team information
    home_team = db.Column(db.String(200), nullable=False)
    away_team = db.Column(db.String(200), nullable=False)
    
    # Match details
    league = db.Column(db.String(100), nullable=False)  # e.g., "Premier League"
    league_id = db.Column(db.Integer)  # API-Sports league ID
    kickoff_time = db.Column(db.DateTime, nullable=False, index=True)
    
    # Match status and scores
    status = db.Column(db.String(50), default='scheduled')  # scheduled, live, finished, postponed, cancelled
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    
    # Linked market
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=True, unique=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # JSON data from API for debugging/backup
    api_data = db.Column(db.JSON, nullable=True)
    
    def __repr__(self):
        return f'<Game {self.fixture_id}: {self.home_team} vs {self.away_team}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fixture_id': self.fixture_id,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'league': self.league,
            'league_id': self.league_id,
            'kickoff_time': self.kickoff_time.isoformat() if self.kickoff_time else None,
            'status': self.status,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'market_id': self.market_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_finished(self) -> bool:
        """Check if game is finished"""
        return self.status == 'finished'
    
    def get_score_string(self) -> str:
        """Get formatted score string"""
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_score} - {self.away_score}"
        return "TBD"
    
    def get_winner(self) -> str:
        """Get winner: 'home', 'away', or 'draw'"""
        if not self.is_finished():
            return None
        
        if self.home_score > self.away_score:
            return 'home'
        elif self.away_score > self.home_score:
            return 'away'
        else:
            return 'draw'
