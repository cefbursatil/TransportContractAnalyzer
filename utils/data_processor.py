import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
from .notifications import notify_new_contracts
import streamlit as st

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache data for 1 hour
    def load_data():
        """Load contract data from CSV files with enhanced error handling and logging"""
        try:
            logger.info("Starting data loading process")
            files = [f for f in os.listdir() if f.endswith('.csv')]
            logger.info(f"Found {len(files)} CSV files: {files}")
            
            # Get the most recent files
            active_file = None
            historical_file = None
            
            # Update the file identification logic with logging
            for file in files:
                logger.debug(f"Processing file: {file}")
                if 'open' in file.lower():
                    if not active_file or file > active_file:
                        active_file = file
                        logger.debug(f"Updated active file to: {file}")
                elif 'closed' in file.lower():
                    if not historical_file or file > historical_file:
                        historical_file = file
                        logger.debug(f"Updated historical file to: {file}")

            # Load files with proper error handling
            active_df = pd.DataFrame()
            historical_df = pd.DataFrame()
            
            if active_file:
                try:
                    logger.info(f"Loading active contracts from: {active_file}")
                    active_df = pd.read_csv(active_file, encoding='utf-8', low_memory=False)
                    active_df['tipo'] = 'active'
                    logger.info(f"Successfully loaded {len(active_df)} active contracts")
                except Exception as e:
                    logger.error(f"Error loading active contracts from {active_file}: {str(e)}")
                    active_df = pd.DataFrame()

            if historical_file:
                try:
                    logger.info(f"Loading historical contracts from: {historical_file}")
                    historical_df = pd.read_csv(historical_file, encoding='utf-8', low_memory=False)
                    historical_df['tipo'] = 'historical'
                    logger.info(f"Successfully loaded {len(historical_df)} historical contracts")
                except Exception as e:
                    logger.error(f"Error loading historical contracts from {historical_file}: {str(e)}")
                    historical_df = pd.DataFrame()
            
            # Process the dataframes
            active_df = DataProcessor.process_contracts(active_df, 'active') if not active_df.empty else pd.DataFrame()
            historical_df = DataProcessor.process_contracts(historical_df, 'historical') if not historical_df.empty else pd.DataFrame()
            
            return active_df, historical_df
            
        except Exception as e:
            logger.error(f"Error in data loading process: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=3600)  # Cache processed data for 1 hour
    def process_contracts(df, contract_type='active'):
        """Process contracts with enhanced validation and logging"""
        if df is None or df.empty:
            logger.warning(f"Empty dataframe received for {contract_type} contracts")
            return pd.DataFrame()
            
        try:
            logger.info(f"Starting contract processing for {contract_type} contracts")
            
            # Create a copy to avoid modifying original
            df = df.copy()

            # Define column mappings
            column_mapping = {
                'valor_total_adjudicacion': 'valor_del_contrato',
                'fecha_de_publicacion_del': 'fecha_de_firma',
                'departamento_entidad': 'departamento',
                'entidad': 'nombre_entidad',
                'id_del_proceso': 'id_contrato',
                'descripcion_del_procedimiento': 'descripcion_del_proceso',
                'tipo_de_contrato': 'tipo_de_contrato',
                'duracion_del_contrato': 'duracion',
                'proveedor': 'proveedor_adjudicado',
                'documento_proveedor': 'documento_proveedor',
                'dias_adicionados': 'dias_adicionados'
            }
            
            # Log available columns for debugging
            logger.debug(f"Available columns in DataFrame: {df.columns.tolist()}")
            
            # Apply column mapping only for existing columns
            mapping_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=mapping_columns)
            
            # Handle monetary values safely
            if 'valor_del_contrato' in df.columns:
                df['valor_del_contrato'] = pd.to_numeric(
                    df['valor_del_contrato'].astype(str).str.replace(r'[^\d.-]', '', regex=True),
                    errors='coerce'
                ).fillna(0)
            
            # Handle date columns
            date_columns = [col for col in df.columns if 'fecha' in col.lower()]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Handle numerical columns
            for col in ['duracion', 'dias_adicionados']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')
            
            # Sort by fecha_de_firma if available
            if 'fecha_de_firma' in df.columns:
                df = df.sort_values('fecha_de_firma', ascending=False)
            
            # Add calculated columns
            if 'fecha_de_firma' in df.columns and 'duracion' in df.columns:
                df['fecha_fin_estimada'] = df['fecha_de_firma'] + pd.to_timedelta(df['duracion'], unit='D')
            
            if df.empty:
                logger.warning(f"DataFrame is empty after processing {contract_type} contracts")
            else:
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
    def get_contract_statistics(df):
        """Calculate key statistics for contracts"""
        try:
            stats = {
                'total_contracts': len(df),
                'total_value': df['valor_del_contrato'].sum() if 'valor_del_contrato' in df.columns else 0,
                'avg_value': df['valor_del_contrato'].mean() if 'valor_del_contrato' in df.columns else 0,
                'avg_duration': df['duracion'].mean() if 'duracion' in df.columns else 0,
                'contracts_by_type': df['tipo_de_contrato'].value_counts().to_dict() if 'tipo_de_contrato' in df.columns else {},
                'contracts_by_dept': df['departamento'].value_counts().to_dict() if 'departamento' in df.columns else {}
            }
            return stats
        except Exception as e:
            logger.error(f"Error calculating contract statistics: {str(e)}")
            return {}
