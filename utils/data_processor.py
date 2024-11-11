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
        """Load contract data from CSV files with enhanced error handling and logging"""
        try:
            logger.debug("Starting data loading process")
            files = [f for f in os.listdir() if f.endswith('.csv')]
            logger.info(f"Found {len(files)} CSV files: {files}")
            
            # Get the most recent files
            active_file = None
            historical_file = None
            
            # Update the file identification logic with logging
            for file in files:
                logger.debug(f"Processing file: {file}")
                if 'open' in file:
                    if not active_file or file > active_file:
                        active_file = file
                        logger.debug(f"Updated active file to: {file}")
                elif 'closed' in file:
                    if not historical_file or file > historical_file:
                        historical_file = file
                        logger.debug(f"Updated historical file to: {file}")

            # Load files with proper error handling and type checking
            active_df = pd.DataFrame()
            historical_df = pd.DataFrame()
            
            if active_file:
                try:
                    logger.info(f"Loading active contracts from: {active_file}")
                    active_df = pd.read_csv(active_file, encoding='utf-8', low_memory=False)
                    
                    # Verify data types
                    DataProcessor._verify_datatypes(active_df, 'active')
                    logger.info(f"Successfully loaded {len(active_df)} active contracts")
                except Exception as e:
                    logger.error(f"Error loading active contracts from {active_file}: {str(e)}")
                    active_df = pd.DataFrame()

            if historical_file:
                try:
                    logger.info(f"Loading historical contracts from: {historical_file}")
                    historical_df = pd.read_csv(historical_file, encoding='utf-8', low_memory=False)
                    
                    # Verify data types
                    DataProcessor._verify_datatypes(historical_df, 'historical')
                    logger.info(f"Successfully loaded {len(historical_df)} historical contracts")
                except Exception as e:
                    logger.error(f"Error loading historical contracts from {historical_file}: {str(e)}")
                    historical_df = pd.DataFrame()
            
            return active_df, historical_df
            
        except Exception as e:
            logger.error(f"Error in data loading process: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    @staticmethod
    def _verify_datatypes(df, contract_type):
        """Verify and convert data types for DataFrame columns"""
        try:
            # Date columns
            date_columns = [col for col in df.columns if 'fecha' in col.lower()]
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                logger.debug(f"Converted {col} to datetime in {contract_type} contracts")

            # Numeric columns
            numeric_columns = ['valor_del_contrato', 'duracion']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    logger.debug(f"Converted {col} to numeric in {contract_type} contracts")

            # Categorical columns
            categorical_columns = ['departamento', 'tipo_de_contrato', 'estado_del_contrato']
            for col in categorical_columns:
                if col in df.columns:
                    df[col] = df[col].astype('category')
                    logger.debug(f"Converted {col} to category in {contract_type} contracts")

        except Exception as e:
            logger.error(f"Error verifying data types for {contract_type} contracts: {str(e)}")

    @staticmethod
    def process_contracts(df, contract_type='active'):
        """Process contracts with enhanced validation and logging"""
        if df is None or len(df) == 0:
            logger.warning(f"Empty dataframe received for {contract_type} contracts")
            return pd.DataFrame()
            
        try:
            logger.info(f"Starting contract processing for {contract_type} contracts")
            
            # Create a copy to avoid modifying original
            df = df.copy()
            
            # Validate required columns
            required_columns = ['valor_del_contrato', 'fecha_de_firma', 'departamento']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns in {contract_type} contracts: {missing_columns}")
                return pd.DataFrame()
            
            # Define column mappings based on contract type
            if contract_type == 'active':
                column_mapping = {
                    'valor_total_adjudicacion': 'valor_del_contrato',
                    'precio_base': 'valor_del_contrato',
                    'id_del_proceso': 'id_contrato',
                    'descripci_n_del_procedimiento': 'descripcion_del_proceso',
                    'nombre_de_la_entidad': 'nombre_entidad',
                    'departamento_entidad': 'departamento'
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
                logger.debug(f"Renamed columns in {contract_type} contracts: {existing_columns}")
            
            # Handle monetary values safely
            if 'valor_del_contrato' in df.columns:
                logger.debug(f"Processing monetary values for {contract_type} contracts")
                # First convert to string and handle non-numeric characters
                df['valor_del_contrato'] = df['valor_del_contrato'].astype(str)
                df['valor_del_contrato'] = df['valor_del_contrato'].str.replace(r'[^\d.-]', '', regex=True)
                # Then convert to numeric
                df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce').fillna(0)
            
            # Handle date columns
            date_columns = [col for col in df.columns if 'fecha' in col.lower()]
            for col in date_columns:
                if col in df.columns:
                    logger.debug(f"Processing date column {col} for {contract_type} contracts")
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            logger.info(f"Successfully processed {len(df)} {contract_type} contracts")
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