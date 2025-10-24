"""
Chainlink Oracle Service for Seti Prediction Markets
Fetches real-world data for market resolution
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class ChainlinkService:
    """Service for interacting with Chainlink oracles"""
    
    def __init__(self):
        # Chainlink price feed addresses for different networks
        self.price_feeds = {
            'ethereum': {
                'mainnet': {
                    'ETH_USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
                    'BTC_USD': '0xF4030086522a5bEEa4988F8c5E0051283012D33F',
                    'LINK_USD': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
                },
                'base': {
                    'ETH_USD': '0x71041dddad3595f9ced3dccfbe3d1f4b0a16bb70',
                    'BTC_USD': '0x4e3037C4D9886B8F8B8542c7a78f163F8F2516e9',
                }
            }
        }
        
        # Chainlink API endpoints
        self.api_endpoints = {
            'mainnet': 'https://api.chain.link/v1/feeds',
            'base': 'https://api.chain.link/v1/feeds'
        }
    
    async def get_price_feed(self, symbol: str, network: str = 'base') -> Optional[Dict[str, Any]]:
        """
        Get current price from Chainlink oracle
        
        Args:
            symbol: Trading pair symbol (e.g., 'ETH_USD', 'BTC_USD')
            network: Network to query ('base', 'mainnet')
            
        Returns:
            Dict with price data or None if error
        """
        try:
            if network not in self.price_feeds['ethereum']:
                logger.error(f"Unsupported network: {network}")
                return None
                
            if symbol not in self.price_feeds['ethereum'][network]:
                logger.error(f"Unsupported symbol: {symbol} on {network}")
                return None
            
            # For now, we'll use a mock implementation
            # In production, you'd call the actual Chainlink oracle contracts
            mock_price_data = {
                'ETH_USD': {'price': 2500.50, 'timestamp': int(datetime.now(timezone.utc).timestamp())},
                'BTC_USD': {'price': 45000.75, 'timestamp': int(datetime.now(timezone.utc).timestamp())},
                'LINK_USD': {'price': 15.25, 'timestamp': int(datetime.now(timezone.utc).timestamp())},
            }
            
            if symbol in mock_price_data:
                return {
                    'symbol': symbol,
                    'price': mock_price_data[symbol]['price'],
                    'timestamp': mock_price_data[symbol]['timestamp'],
                    'network': network,
                    'source': 'chainlink'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Chainlink price for {symbol}: {e}")
            return None
    
    async def get_weather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data for location-based markets
        
        Args:
            location: City, country (e.g., 'New York, US')
            
        Returns:
            Dict with weather data or None if error
        """
        try:
            # Mock weather data - in production, use Chainlink weather oracles
            mock_weather = {
                'New York, US': {
                    'temperature': 72,
                    'condition': 'sunny',
                    'humidity': 65,
                    'timestamp': int(datetime.now(timezone.utc).timestamp())
                },
                'London, UK': {
                    'temperature': 55,
                    'condition': 'cloudy',
                    'humidity': 80,
                    'timestamp': int(datetime.now(timezone.utc).timestamp())
                }
            }
            
            if location in mock_weather:
                return {
                    'location': location,
                    'data': mock_weather[location],
                    'source': 'chainlink_weather'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching weather data for {location}: {e}")
            return None
    
    async def get_sports_data(self, sport: str, league: str, team: str) -> Optional[Dict[str, Any]]:
        """
        Get sports data for sports markets
        
        Args:
            sport: Sport type (e.g., 'football', 'basketball')
            league: League name (e.g., 'NFL', 'NBA')
            team: Team name
            
        Returns:
            Dict with sports data or None if error
        """
        try:
            # Mock sports data - in production, use Chainlink sports oracles
            mock_sports = {
                'football': {
                    'NFL': {
                        'Chiefs': {'wins': 8, 'losses': 2, 'last_game': 'W 28-24'},
                        'Bills': {'wins': 7, 'losses': 3, 'last_game': 'L 21-17'}
                    }
                }
            }
            
            if sport in mock_sports and league in mock_sports[sport] and team in mock_sports[sport][league]:
                return {
                    'sport': sport,
                    'league': league,
                    'team': team,
                    'data': mock_sports[sport][league][team],
                    'source': 'chainlink_sports'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching sports data for {team}: {e}")
            return None
    
    async def resolve_market(self, market_id: str, market_type: str, resolution_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolve a market using oracle data
        
        Args:
            market_id: ID of the market to resolve
            market_type: Type of market ('price', 'weather', 'sports', 'election')
            resolution_data: Data needed for resolution
            
        Returns:
            Dict with resolution result or None if error
        """
        try:
            resolution_result = {
                'market_id': market_id,
                'resolved_at': int(datetime.now(timezone.utc).timestamp()),
                'resolution_data': resolution_data,
                'oracle_source': 'chainlink'
            }
            
            # Determine outcome based on market type and data
            if market_type == 'price':
                # Price-based resolution
                target_price = resolution_data.get('target_price')
                current_price = resolution_data.get('current_price')
                
                if current_price and target_price:
                    if current_price >= target_price:
                        resolution_result['outcome'] = 'YES'
                    else:
                        resolution_result['outcome'] = 'NO'
                else:
                    resolution_result['outcome'] = 'INVALID'
            
            elif market_type == 'weather':
                # Weather-based resolution
                target_temp = resolution_data.get('target_temperature')
                current_temp = resolution_data.get('current_temperature')
                
                if current_temp and target_temp:
                    if current_temp >= target_temp:
                        resolution_result['outcome'] = 'YES'
                    else:
                        resolution_result['outcome'] = 'NO'
                else:
                    resolution_result['outcome'] = 'INVALID'
            
            elif market_type == 'sports':
                # Sports-based resolution
                team_wins = resolution_data.get('team_wins', 0)
                target_wins = resolution_data.get('target_wins', 0)
                
                if team_wins >= target_wins:
                    resolution_result['outcome'] = 'YES'
                else:
                    resolution_result['outcome'] = 'NO'
            
            else:
                resolution_result['outcome'] = 'INVALID'
            
            return resolution_result
            
        except Exception as e:
            logger.error(f"Error resolving market {market_id}: {e}")
            return None

# Global instance
chainlink_service = ChainlinkService()
