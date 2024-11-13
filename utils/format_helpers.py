import locale
from typing import Union
import logging

logger = logging.getLogger(__name__)

def format_currency(value: Union[float, int, str]) -> str:
    """Format a numeric value as Colombian Peso currency with enhanced error handling"""
    try:
        # Convert string to float if needed
        if isinstance(value, str):
            value = float(value.replace(',', ''))
        elif not isinstance(value, (int, float)):
            return "$0 COP"
            
        # Handle negative values
        is_negative = value < 0
        abs_value = abs(value)
        
        # Format with thousand separators
        formatted = f"${abs_value:,.0f} COP"
        
        return f"-{formatted}" if is_negative else formatted
    except (TypeError, ValueError) as e:
        logger.warning(f"Error formatting currency value '{value}': {str(e)}")
        return "$0 COP"

def format_percentage(value: Union[float, int, str], decimal_places: int = 1) -> str:
    """Format a numeric value as a percentage with specified decimal places"""
    try:
        if isinstance(value, str):
            value = float(value.replace(',', ''))
        return f"{value:.{decimal_places}f}%"
    except (TypeError, ValueError) as e:
        logger.warning(f"Error formatting percentage value '{value}': {str(e)}")
        return "0%"

def format_large_number(value: Union[float, int, str]) -> str:
    """Format large numbers with K/M/B suffixes"""
    try:
        if isinstance(value, str):
            value = float(value.replace(',', ''))
            
        if not isinstance(value, (int, float)):
            return "0"
            
        if value < 1000:
            return str(int(value))
        elif value < 1000000:
            return f"{value/1000:.1f}K"
        elif value < 1000000000:
            return f"{value/1000000:.1f}M"
        else:
            return f"{value/1000000000:.1f}B"
    except (TypeError, ValueError) as e:
        logger.warning(f"Error formatting large number '{value}': {str(e)}")
        return "0"
