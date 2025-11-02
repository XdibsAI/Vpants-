from datetime import datetime

def format_currency(amount: float) -> str:
    """Format amount as Indonesian Rupiah"""
    if amount is None:
        return "Rp 0"
    return f"Rp {amount:,.0f}".replace(",", ".")

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    return datetime.strptime(date_str, '%Y-%m-%d')

def validate_positive_number(value: str) -> float:
    """Validate and convert to positive number"""
    try:
        num = float(value)
        if num < 0:
            raise ValueError("Number must be positive")
        return num
    except ValueError:
        raise ValueError("Please enter a valid number")

def safe_float(value, default=0.0):
    """Safely convert to float with default value"""
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default
