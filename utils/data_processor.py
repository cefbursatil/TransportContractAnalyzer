import pandas as pd
import numpy as np
from datetime import datetime
import os

class DataProcessor:
    @staticmethod
    def load_data():
        """Load the most recent CSV files"""
        files = [f for f in os.listdir() if f.endswith('.csv')]
        
        # Get the most recent files for each type
        active_contracts = None
        presentation_phase = None
        
        for file in files:
            if 'active_transport_contracts' in file:
                if active_contracts is None or file > active_contracts:
                    active_contracts = file
            elif 'secop_ii_transport_presentation_phase' in file:
                if presentation_phase is None or file > presentation_phase:
                    presentation_phase = file
        
        active_df = pd.read_csv(active_contracts) if active_contracts else pd.DataFrame()
        presentation_df = pd.read_csv(presentation_phase) if presentation_phase else pd.DataFrame()
        
        return active_df, presentation_df

    @staticmethod
    def process_contracts(df, contract_type='active'):
        """Process and clean contract data"""
        if df.empty:
            return df
            
        # Convert date columns
        date_columns = [col for col in df.columns if 'fecha' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        # Convert monetary columns
        monetary_cols = [col for col in df.columns if 'valor' in col.lower()]
        for col in monetary_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Clean text columns
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].fillna('No especificado')
            
        return df

    @staticmethod
    def apply_filters(df, filters):
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if value:
                if isinstance(value, tuple) and len(value) == 2:  # Date range
                    if column in df.columns:
                        start_date = pd.to_datetime(value[0])
                        end_date = pd.to_datetime(value[1])
                        filtered_df = filtered_df[
                            (filtered_df[column].dt.date >= start_date.date()) & 
                            (filtered_df[column].dt.date <= end_date.date())
                        ]
                elif isinstance(value, list):  # Multiple selection
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:  # Single value
                    filtered_df = filtered_df[filtered_df[column].str.contains(str(value), 
                                                                         case=False, 
                                                                         na=False)]
        
        return filtered_df

    @staticmethod
    def generate_analytics(df):
        """Generate analytics for the dashboard"""
        analytics = {
            'total_contracts': len(df),
            'total_value': df['valor_del_contrato'].sum() if 'valor_del_contrato' in df.columns else 0,
            'avg_duration': df['duracion'].mean() if 'duracion' in df.columns else 0,
            'contracts_by_department': df['departamento'].value_counts().head(10).to_dict() 
                                     if 'departamento' in df.columns else {},
            'contracts_by_type': df['tipo_de_contrato'].value_counts().to_dict() 
                               if 'tipo_de_contrato' in df.columns else {},
            'monthly_contracts': df.groupby(df['fecha_de_firma'].dt.to_period('M')).size().to_dict() 
                               if 'fecha_de_firma' in df.columns else {}
        }
        return analytics
