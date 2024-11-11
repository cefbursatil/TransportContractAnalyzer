import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
from .notifications import notify_new_contracts

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    def load_data():
        try:
            files = [f for f in os.listdir() if f.endswith('.csv')]
            
            # Get the most recent files
            active_file = None
            historical_file = None
            
            # Update the file identification logic
            for file in files:
                if 'secop_ii_transport_presentation_phase_' in file:
                    if not active_file or file > active_file:
                        active_file = file
                elif 'active_transport_contracts_' in file:
                    if not historical_file or file > historical_file:
                        historical_file = file

            # Load files with proper error handling
            active_df = pd.DataFrame()
            historical_df = pd.DataFrame()
            
            if active_file:
                try:
                    active_df = pd.read_csv(active_file, encoding='utf-8', low_memory=False)
                    logger.info(f"Loaded {len(active_df)} active contracts")
                except Exception as e:
                    logger.error(f"Error loading active contracts: {str(e)}")
                    active_df = pd.DataFrame()

            if historical_file:
                try:
                    historical_df = pd.read_csv(historical_file, encoding='utf-8', low_memory=False)
                    logger.info(f"Loaded {len(historical_df)} historical contracts")
                except Exception as e:
                    logger.error(f"Error loading historical contracts: {str(e)}")
                    historical_df = pd.DataFrame()
            
            return active_df, historical_df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    @staticmethod
    def process_contracts(df, contract_type='active'):
        if df is None or len(df) == 0:  # Use len() instead of df.empty
            logger.warning(f"Empty dataframe received for {contract_type} contracts")
            return pd.DataFrame()
            
        try:
            # Create a copy to avoid modifying original
            df = df.copy()
            
            # Define column mappings based on contract type
            if contract_type == 'active':
                column_mapping = {
                    'valor_total_adjudicacion': 'valor_del_contrato',
                    'precio_base': 'valor_del_contrato',
                    'id_del_proceso': 'id_contrato',
                    'descripci_n_del_procedimiento': 'descripcion_del_proceso'
                }
            else:
                column_mapping = {
                    'valor_del_contrato': 'valor_del_contrato',
                    'proceso_de_compra': 'id_contrato',
                    'descripcion_del_proceso': 'descripcion_del_proceso',
                    'nombre_de_la_entidad': 'nombre_entidad',
                    'departamento_entidad': 'departamento'
                }
            
            # Only rename columns that exist
            existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
            if existing_columns:
                df = df.rename(columns=existing_columns)
            
            # Handle monetary values safely
            if 'valor_del_contrato' in df.columns:
                # Convert to numeric, removing non-numeric characters
                df['valor_del_contrato'] = pd.to_numeric(
                    df['valor_del_contrato'].astype(str).str.replace(r'[^\d.-]', '', regex=True),
                    errors='coerce'
                ).fillna(0)
            
            # Handle date columns
            date_columns = [col for col in df.columns if 'fecha' in col.lower()]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing {contract_type} contracts: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def detect_new_contracts(current_df, previous_df):
        """Detect new contracts by comparing current and previous data"""
        if previous_df.empty:
            return current_df
        
        try:
            # Use contract ID for comparison
            current_ids = set(current_df['id_contrato'])
            previous_ids = set(previous_df['id_contrato'])
            
            # Find new contract IDs
            new_contract_ids = current_ids - previous_ids
            
            # Get new contracts data
            new_contracts = current_df[current_df['id_contrato'].isin(new_contract_ids)]
            
            return new_contracts
        except Exception as e:
            logger.error(f"Error detecting new contracts: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def notify_if_new_contracts(current_df, previous_df, recipients):
        """Check for new contracts and send notifications if found"""
        try:
            new_contracts = DataProcessor.detect_new_contracts(current_df, previous_df)
            
            if not new_contracts.empty:
                # Convert DataFrame to list of dictionaries for notification
                contracts_data = new_contracts.to_dict('records')
                
                # Send notification
                if notify_new_contracts(contracts_data, recipients):
                    logger.info(f"Notification sent for {len(contracts_data)} new contracts")
                else:
                    logger.error("Failed to send notification for new contracts")
        except Exception as e:
            logger.error(f"Error in notification process: {str(e)}")
    
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

    @staticmethod
    def generate_analytics(df):
        """Generate analytics for the dashboard"""
        try:
            analytics = {
                'total_contracts': len(df),
                'total_value': df['valor_del_contrato'].sum() if 'valor_del_contrato' in df.columns else 0,
                'avg_duration': df['duracion'].mean() if 'duracion' in df.columns else 0,
                'contracts_by_department': df['departamento'].value_counts().head(10).to_dict() if 'departamento' in df.columns else {},
                'contracts_by_type': df['tipo_de_contrato'].value_counts().to_dict() if 'tipo_de_contrato' in df.columns else {},
                'monthly_contracts': df.groupby(pd.to_datetime(df['fecha_de_firma']).dt.to_period('M')).size().to_dict() if 'fecha_de_firma' in df.columns else {}
            }
            return analytics
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return {
                'total_contracts': 0,
                'total_value': 0,
                'avg_duration': 0,
                'contracts_by_department': {},
                'contracts_by_type': {},
                'monthly_contracts': {}
            }
