import re

def is_valid_sui_address(address: str) -> bool:
    """Validate Sui address format"""
    if not address:
        return False
    
    # Sui addresses are 66 characters (0x + 64 hex chars)
    pattern = r'^0x[a-fA-F0-9]{64}$'
    return bool(re.match(pattern, address))

def is_valid_market_id(market_id: str) -> bool:
    """Validate market ID format"""
    return is_valid_sui_address(market_id)

def validate_prediction_data(data: dict) -> tuple[bool, str]:
    """Validate prediction data"""
    required_fields = ['transaction_hash', 'market_id', 'user_address', 'outcome', 'amount', 'timestamp']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    if not is_valid_sui_address(data['market_id']):
        return False, "Invalid market_id format"
    
    if not is_valid_sui_address(data['user_address']):
        return False, "Invalid user_address format"
    
    if data['outcome'] not in [0, 1]:
        return False, "Outcome must be 0 (NO) or 1 (YES)"
    
    if not isinstance(data['amount'], int) or data['amount'] <= 0:
        return False, "Amount must be a positive integer"
    
    return True, ""

def validate_market_data(data: dict) -> tuple[bool, str]:
    """Validate market data"""
    required_fields = ['question', 'description', 'end_time', 'category']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    if len(data['question']) < 10:
        return False, "Question must be at least 10 characters"
    
    if data['end_time'] <= 0:
        return False, "Invalid end_time"
    
    return True, ""

