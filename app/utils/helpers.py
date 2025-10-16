from datetime import datetime

def format_sui_amount(amount_mist: int) -> float:
    """Convert MIST to SUI (1 SUI = 10^9 MIST)"""
    return amount_mist / 1_000_000_000

def mist_to_sui(mist: int) -> float:
    """Convert MIST to SUI"""
    return mist / 1_000_000_000

def sui_to_mist(sui: float) -> int:
    """Convert SUI to MIST"""
    return int(sui * 1_000_000_000)

def format_timestamp(timestamp: int) -> str:
    """Convert Unix timestamp to ISO format"""
    return datetime.fromtimestamp(timestamp).isoformat()

def calculate_market_prices(outcome_a_shares: int, outcome_b_shares: int) -> dict:
    """Calculate YES/NO prices from shares"""
    total = outcome_a_shares + outcome_b_shares
    
    if total == 0:
        return {'yes_price': 50, 'no_price': 50}
    
    yes_price = round((outcome_b_shares / total) * 100)
    no_price = round((outcome_a_shares / total) * 100)
    
    return {'yes_price': yes_price, 'no_price': no_price}

def format_volume(volume: int) -> str:
    """Format volume for display"""
    sui_amount = format_sui_amount(volume)
    
    if sui_amount >= 1_000_000:
        return f"{sui_amount / 1_000_000:.1f}M"
    elif sui_amount >= 1_000:
        return f"{sui_amount / 1_000:.1f}K"
    else:
        return f"{sui_amount:.2f}"

def time_remaining(end_time: int) -> str:
    """Calculate time remaining until end time"""
    now = datetime.now().timestamp()
    remaining = end_time - now
    
    if remaining <= 0:
        return "Ended"
    
    days = int(remaining // 86400)
    hours = int((remaining % 86400) // 3600)
    
    if days > 0:
        return f"{days}d {hours}h"
    else:
        return f"{hours}h"

def paginate_results(query, page: int, per_page: int, max_per_page: int = 100):
    """Helper for pagination"""
    per_page = min(per_page, max_per_page)
    return query.paginate(page=page, per_page=per_page, error_out=False)

