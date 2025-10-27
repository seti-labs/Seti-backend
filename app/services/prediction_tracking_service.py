import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Market, Prediction, User

class PredictionTrackingService:
    """Service for tracking prediction status and outcomes"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = 'https://api-football-v1.p.rapidapi.com/v3'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com',
            'Accept': 'application/json'
        } if self.api_key else {}
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            print("Warning: RAPIDAPI_KEY not set")
            return None
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params, 
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def get_prediction_status(self, prediction: Prediction) -> Dict:
        """Get current status of a prediction"""
        if not prediction.market:
            return {
                'status': 'unknown',
                'message': 'Market not found',
                'progress': 0,
                'current_price': 0,
                'potential_payout': 0,
                'is_resolved': False,
                'winning_outcome': None
            }
        
        market = prediction.market
        
        # Check if market is resolved
        if market.resolved:
            is_winner = market.winning_outcome == prediction.outcome
            return {
                'status': 'resolved',
                'message': 'Market resolved',
                'progress': 100,
                'current_price': 100 if is_winner else 0,
                'potential_payout': prediction.shares / 1_000_000_000 if is_winner else 0,
                'is_resolved': True,
                'winning_outcome': market.winning_outcome,
                'is_winner': is_winner,
                'profit_loss': (prediction.shares / 1_000_000_000) - (prediction.amount / 1_000_000_000) if is_winner else -(prediction.amount / 1_000_000_000)
            }
        
        # For active markets, calculate current status
        from app.models import calculate_prices
        yes_price, no_price = calculate_prices(market.outcome_a_shares, market.outcome_b_shares)
        current_price = yes_price if prediction.outcome == 'YES' else no_price
        
        # Calculate time progress
        now = datetime.utcnow()
        start_time = datetime.fromtimestamp(market.created_timestamp)
        end_time = datetime.fromtimestamp(market.end_time)
        
        total_duration = (end_time - start_time).total_seconds()
        elapsed_time = (now - start_time).total_seconds()
        progress = min(max((elapsed_time / total_duration) * 100, 0), 100)
        
        # Determine status based on time and market activity
        if progress >= 100:
            status = 'pending_resolution'
            message = 'Waiting for resolution'
        elif progress >= 80:
            status = 'ending_soon'
            message = 'Market ending soon'
        elif progress >= 50:
            status = 'active'
            message = 'Market active'
        else:
            status = 'early'
            message = 'Early stage'
        
        # Calculate potential payout
        potential_payout = (prediction.amount / 1_000_000_000) * (100 / current_price) if current_price > 0 else 0
        
        return {
            'status': status,
            'message': message,
            'progress': progress,
            'current_price': current_price,
            'potential_payout': potential_payout,
            'is_resolved': False,
            'winning_outcome': None,
            'is_winner': None,
            'profit_loss': None,
            'time_remaining': max(0, (end_time - now).total_seconds()),
            'volume_24h': market.volume_24h / 1_000_000_000,
            'total_liquidity': market.total_liquidity / 1_000_000_000
        }
    
    def get_user_predictions_status(self, user_address: str) -> List[Dict]:
        """Get status of all user predictions"""
        predictions = Prediction.query.filter_by(user_address=user_address).all()
        results = []
        
        for prediction in predictions:
            status = self.get_prediction_status(prediction)
            results.append({
                'prediction_id': prediction.id,
                'market_id': prediction.market_id,
                'market_question': prediction.market.question if prediction.market else 'Unknown Market',
                'outcome': prediction.outcome,
                'amount': prediction.amount / 1_000_000_000,
                'shares': prediction.shares / 1_000_000_000,
                'timestamp': prediction.timestamp,
                'status': status
            })
        
        return results
    
    def update_prediction_tracking(self, prediction_id: str) -> Dict:
        """Update tracking data for a specific prediction"""
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            return {'error': 'Prediction not found'}
        
        status = self.get_prediction_status(prediction)
        
        # Update prediction with current status if needed
        if status['is_resolved'] and prediction.market:
            prediction.settled_at = datetime.utcnow()
            db.session.commit()
        
        return {
            'prediction_id': prediction_id,
            'status': status
        }
    
    def get_market_analytics(self, market_id: str) -> Dict:
        """Get analytics for a specific market"""
        market = Market.query.get(market_id)
        if not market:
            return {'error': 'Market not found'}
        
        predictions = Prediction.query.filter_by(market_id=market_id).all()
        
        yes_predictions = [p for p in predictions if p.outcome == 'YES']
        no_predictions = [p for p in predictions if p.outcome == 'NO']
        
        total_volume = sum(p.amount for p in predictions) / 1_000_000_000
        yes_volume = sum(p.amount for p in yes_predictions) / 1_000_000_000
        no_volume = sum(p.amount for p in no_predictions) / 1_000_000_000
        
        return {
            'market_id': market_id,
            'total_predictions': len(predictions),
            'yes_predictions': len(yes_predictions),
            'no_predictions': len(no_predictions),
            'total_volume': total_volume,
            'yes_volume': yes_volume,
            'no_volume': no_volume,
            'yes_percentage': (yes_volume / total_volume * 100) if total_volume > 0 else 0,
            'no_percentage': (no_volume / total_volume * 100) if total_volume > 0 else 0,
            'is_resolved': market.resolved,
            'winning_outcome': market.winning_outcome,
            'created_timestamp': market.created_timestamp,
            'end_time': market.end_time
        }

# Global instance
prediction_tracking_service = PredictionTrackingService()

