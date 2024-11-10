import pandas as pd
import secop
from datetime import datetime
import os

def update_data():
    """Fetch new data using the secop.py script"""
    df_secop_i, df_secop_ii = secop.fetch_and_process_all_data()
    
    # Combine and process the data
    combined_df = process_combined_data(df_secop_i, df_secop_ii)
    
    # Save to cache
    save_to_cache(combined_df)
    
    return combined_df

def process_combined_data(df_secop_i, df_secop_ii):
    """Process and combine data from both SECOP I and II"""
    # Standardize column names
    df_secop_i = standardize_secop_i(df_secop_i)
    df_secop_ii = standardize_secop_ii(df_secop_ii)
    
    # Combine datasets
    combined_df = pd.concat([df_secop_i, df_secop_ii], ignore_index=True)
    
    # Convert date columns
    date_columns = [col for col in combined_df.columns if 'fecha' in col.lower()]
    for col in date_columns:
        combined_df[col] = pd.to_datetime(combined_df[col], errors='coerce')
    
    # Convert numeric columns
    numeric_columns = ['valor_del_contrato', 'valor_pagado', 'valor_pendiente_de_pago']
    for col in numeric_columns:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
    
    return combined_df

def standardize_secop_i(df):
    """Standardize SECOP I column names"""
    column_mapping = {
        'valor_del_contrato': 'valor_del_contrato',
        'fecha_de_firma': 'fecha_de_firma',
        'estado_contrato': 'estado_contrato',
        # Add more mappings as needed
    }
    return df.rename(columns=column_mapping)

def standardize_secop_ii(df):
    """Standardize SECOP II column names"""
    column_mapping = {
        'valor_total_adjudicacion': 'valor_del_contrato',
        'fecha_de_publicacion': 'fecha_de_firma',
        'estado_del_procedimiento': 'estado_contrato',
        # Add more mappings as needed
    }
    return df.rename(columns=column_mapping)

def save_to_cache(df):
    """Save processed data to cache"""
    cache_dir = ".cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    df.to_parquet(os.path.join(cache_dir, "contracts_data.parquet"))

def load_from_cache():
    """Load data from cache"""
    cache_file = os.path.join(".cache", "contracts_data.parquet")
    if os.path.exists(cache_file):
        return pd.read_parquet(cache_file)
    return None
