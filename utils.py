import pandas as pd
import data_processor as dp

def format_currency(value):
    """Format currency values with comma separator and COP"""
    try:
        return f"${value:,.0f} COP"
    except:
        return value

def load_data():
    """Load data from cache or fetch new data"""
    df = dp.load_from_cache()
    if df is None:
        df = dp.update_data()
    return df

def extract_url(url_dict):
    """Extract URL from dictionary string"""
    try:
        if isinstance(url_dict, str) and 'url' in url_dict:
            return eval(url_dict)['url']
        return url_dict['url'] if isinstance(url_dict, dict) else ''
    except:
        return ''

def clean_text(text):
    """Clean and standardize text fields"""
    if pd.isna(text) or text == 'No Definido':
        return ''
    return str(text).strip()
