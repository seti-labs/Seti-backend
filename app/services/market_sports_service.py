from typing import List, Dict, Optional
from datetime import datetime
from app.models import Market
from .polymarket_gamma_service import polymarket_gamma_service

class MarketSportsService:
    """Service for integrating live sports data with prediction markets using Polymarket Gamma API"""
    
    def __init__(self):
        # Use Polymarket Gamma API service
        self.api_available = True  # Polymarket API is public, no auth needed
        self.api_type = 'polymarket_gamma'
    
    
    def get_live_scores_for_markets(self, markets: List[Market]) -> Dict[str, Dict]:
        """Get live data for a list of markets using Polymarket Gamma API"""
        return polymarket_gamma_service.get_live_scores_for_markets(markets)
    
    def update_market_with_live_score(self, market_id: str) -> Optional[Dict]:
        """Update a specific market with live data from Polymarket"""
        return polymarket_gamma_service.update_market_with_live_data(market_id)
    
    def get_rate_limit_status(self) -> Dict:
        """Get current API rate limit status"""
        return {
            'api_available': self.api_available,
            'api_type': self.api_type,
            'api_base_url': 'https://gamma-api.polymarket.com',
            'message': 'Using Polymarket Gamma API (public, no authentication required)'
        }
    
    def clear_api_cache(self) -> None:
        """Clear API cache (no-op for Polymarket API)"""
        pass

# Global instance
market_sports_service = MarketSportsService()


