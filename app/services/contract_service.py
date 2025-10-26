"""
Single Smart Contract Service - Used by both Frontend and Backend
No duplication, no over-engineering
"""
import os
import requests
from typing import List, Dict, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware

class ContractService:
    """Single service for all smart contract interactions"""
    
    def __init__(self):
        # Use BASE_RPC_URL from config (fallback to old env var for compatibility)
        self.rpc_url = os.getenv('BASE_RPC_URL') or os.getenv('ETH_RPC_URL', 'https://base-sepolia.api.onfinality.io/public')
        # Use PREDICTION_MARKET_CONTRACT_ADDRESS from config (fallback to old env var for compatibility)
        self.contract_address = os.getenv('PREDICTION_MARKET_CONTRACT_ADDRESS') or os.getenv('CONTRACT_ADDRESS', '0x63c0c19a282a1B52b07dD5a65b58948A07DAE32B')
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add POA middleware for Base (required for Base testnet)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check if Web3 connection is working
        if not self.w3.is_connected():
            print(f"Warning: Could not connect to {self.rpc_url}")
            self.contract = None
            return
        
        # Contract ABI - Single source of truth
        self.contract_abi = [
            {
                "inputs": [],
                "name": "nextMarketId",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "name": "markets",
                "outputs": [
                    {"internalType": "string", "name": "question", "type": "string"},
                    {"internalType": "string", "name": "description", "type": "string"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "bool", "name": "resolved", "type": "bool"},
                    {"internalType": "uint8", "name": "winningOutcome", "type": "uint8"},
                    {"internalType": "uint256", "name": "totalLiquidity", "type": "uint256"},
                    {"internalType": "uint256", "name": "outcomeAShares", "type": "uint256"},
                    {"internalType": "uint256", "name": "outcomeBShares", "type": "uint256"},
                    {"internalType": "uint256", "name": "yesPool", "type": "uint256"},
                    {"internalType": "uint256", "name": "noPool", "type": "uint256"},
                    {"internalType": "address", "name": "creator", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "", "type": "uint256"},
                    {"internalType": "address", "name": "", "type": "address"}
                ],
                "name": "bets",
                "outputs": [
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "uint8", "name": "outcome", "type": "uint8"},
                    {"internalType": "bool", "name": "claimed", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "uint256", "name": "marketId", "type": "uint256"},
                    {"indexed": False, "internalType": "string", "name": "question", "type": "string"},
                    {"indexed": False, "internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"indexed": True, "internalType": "address", "name": "creator", "type": "address"}
                ],
                "name": "MarketCreated",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "uint256", "name": "marketId", "type": "uint256"},
                    {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
                    {"indexed": False, "internalType": "uint8", "name": "outcome", "type": "uint8"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "BetPlaced",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "uint256", "name": "marketId", "type": "uint256"},
                    {"indexed": False, "internalType": "uint8", "name": "winningOutcome", "type": "uint8"}
                ],
                "name": "MarketResolved",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "uint256", "name": "marketId", "type": "uint256"},
                    {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "payout", "type": "uint256"}
                ],
                "name": "PayoutClaimed",
                "type": "event"
            }
        ]
        
        if self.contract_address:
            try:
                # Convert to checksum address
                checksum_address = self.w3.to_checksum_address(self.contract_address)
                self.contract = self.w3.eth.contract(
                    address=checksum_address,
                    abi=self.contract_abi
                )
                print(f"Contract service initialized with address: {checksum_address}")
            except Exception as e:
                print(f"Error initializing contract: {e}")
                self.contract = None
        else:
            print("No contract address provided")
            self.contract = None
    
    def get_market(self, market_id: int) -> Optional[Dict]:
        """Get single market from blockchain"""
        if not self.contract:
            return None
            
        try:
            market_data = self.contract.functions.markets(market_id).call()
            
            return {
                'id': str(market_id),
                'question': market_data[0],
                'description': market_data[1],
                'end_time': market_data[2],
                'resolved': market_data[3],
                'winning_outcome': market_data[4],
                'total_liquidity': market_data[5],
                'outcome_a_shares': market_data[6],
                'outcome_b_shares': market_data[7],
                'yes_pool': market_data[8],
                'no_pool': market_data[9],
                'creator': market_data[10]
            }
        except Exception as e:
            print(f"Error fetching market {market_id}: {e}")
            return None
    
    def fetch_all_markets(self) -> List[Dict]:
        """Get all markets from blockchain"""
        if not self.contract:
            return []
            
        try:
            next_market_id = self.contract.functions.nextMarketId().call()
            markets = []
            
            for market_id in range(next_market_id):
                market_data = self.get_market(market_id)
                if market_data:
                    markets.append(market_data)
            
            return markets
        except Exception as e:
            print(f"Error fetching all markets: {e}")
            return []
    
    def get_user_bet(self, market_id: int, user_address: str) -> Optional[Dict]:
        """Get user's bet for a market"""
        if not self.contract:
            return None
            
        try:
            bet_data = self.contract.functions.bets(market_id, user_address).call()
            
            return {
                'amount': bet_data[0],
                'outcome': bet_data[1],
                'claimed': bet_data[2]
            }
        except Exception as e:
            print(f"Error fetching user bet: {e}")
            return None
    
    def calculate_prices(self, yes_pool: int, no_pool: int) -> Dict[str, int]:
        """Calculate YES/NO prices from pools"""
        total_liquidity = yes_pool + no_pool
        if total_liquidity == 0:
            return {'yes_price': 50, 'no_price': 50}
        
        yes_price = round((yes_pool / total_liquidity) * 100)
        no_price = round((no_pool / total_liquidity) * 100)
        
        return {'yes_price': yes_price, 'no_price': no_price}
    
    def is_market_active(self, end_time: int) -> bool:
        """Check if market is still active"""
        import time
        return time.time() < end_time
    
    def get_market_status(self, market: Dict) -> str:
        """Get market status: active, ended, resolved"""
        if market['resolved']:
            return 'resolved'
        if not self.is_market_active(market['end_time']):
            return 'ended'
        return 'active'

# Single instance - no duplication
contract_service = ContractService()
