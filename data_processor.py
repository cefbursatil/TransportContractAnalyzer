import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
from .notifications import notify_new_contracts

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    def process_contracts(df, contract_type='active'):
        if df.empty:
            return df
            
        try:
            # Clean and standardize column names
            column_mapping = {
                'valor_total_adjudicacion': 'valor_del_contrato',
                'precio_base': 'valor_del_contrato'
            }
            df = df.rename(columns=column_mapping)
            
            # Handle monetary values
            if 'valor_del_contrato' in df.columns:
                # Convert to string first
                df['valor_del_contrato'] = df['valor_del_contrato'].astype(str)
                # Remove non-numeric characters
                df['valor_del_contrato'] = df['valor_del_contrato'].str.replace(r'[^\d.-]', '', regex=True)
                df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce').fillna(0)
            
            # Handle date columns
            date_columns = [col for col in df.columns if 'fecha' in col.lower()]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
            return df
        except Exception as e:
            logger.error(f"Error processing contracts: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def apply_filters(df, filters):
        """Apply filters to the dataframe"""
        try:
            filtered_df = df.copy()
            
            for column, value in filters.items():
                if value:
                    if isinstance(value, tuple) and len(value) == 2:  # Date range or numeric range
                        if column in df.columns:
                            if pd.api.types.is_datetime64_any_dtype(df[column]):
                                # Date range filter
                                start_date = pd.to_datetime(value[0])
                                end_date = pd.to_datetime(value[1])
                                filtered_df = filtered_df[
                                    (filtered_df[column].dt.date >= start_date.date()) & 
                                    (filtered_df[column].dt.date <= end_date.date())
                                ]
                            else:
                                # Numeric range filter
                                filtered_df = filtered_df[
                                    (filtered_df[column] >= value[0]) & 
                                    (filtered_df[column] <= value[1])
                                ]
                    elif isinstance(value, list):  # Multiple selection
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                    else:  # Single value
                        filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(
                            str(value), 
                            case=False, 
                            na=False
                        )]
            
            return filtered_df
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            return df
