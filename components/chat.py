import streamlit as st
import google.generativeai as genai
import os
import logging
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class ChatComponent:
    def __init__(self):
        """Initialize the chat component with Google's Gemini AI"""
        try:
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("Google API key not found in environment variables")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = self.model.start_chat(history=[])
            logger.info("ChatComponent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChatComponent: {str(e)}")
            raise

    def get_context_data(self, active_df: pd.DataFrame, historical_df: pd.DataFrame) -> str:
        """Get comprehensive context about active and historical contracts"""
        try:
            today = pd.Timestamp.now().date()
            
            # Filter active contracts with future presentation dates
            future_contracts = active_df[
                pd.to_datetime(active_df['fecha_de_recepcion_de']).dt.date >= today
            ] if 'fecha_de_recepcion_de' in active_df.columns else pd.DataFrame()

            # Historical analytics
            hist_analytics = {
                'total_contracts': len(historical_df),
                'avg_value': historical_df['valor_del_contrato'].mean() if 'valor_del_contrato' in historical_df.columns else 0,
                'total_value': historical_df['valor_del_contrato'].sum() if 'valor_del_contrato' in historical_df.columns else 0
            }

            # Contract type distribution
            type_dist = historical_df['tipo_de_contrato'].value_counts().to_dict() if 'tipo_de_contrato' in historical_df.columns else {}

            # Monthly trend analysis
            if 'fecha_de_firma' in historical_df.columns:
                historical_df['month'] = pd.to_datetime(historical_df['fecha_de_firma']).dt.to_period('M')
                monthly_values = historical_df.groupby('month')['valor_del_contrato'].mean().tail(12)
                trend = "creciente" if monthly_values.iloc[-1] > monthly_values.iloc[0] else "decreciente"
            else:
                trend = "no disponible"

            context = f"""
            Contexto del Sistema de Contratos:

            Contratos Activos con Fecha de Presentación Futura:
            - Total de contratos: {len(future_contracts)}
            - Tipos de contratos principales: {', '.join(future_contracts['tipo_de_contrato'].value_counts().nlargest(3).index.tolist()) if not future_contracts.empty else 'N/A'}
            
            Análisis Histórico:
            - Total de contratos históricos: {hist_analytics['total_contracts']:,}
            - Valor promedio de contratos: ${hist_analytics['avg_value']:,.2f}
            - Valor total histórico: ${hist_analytics['total_value']:,.2f}
            
            Distribución por Tipo de Contrato:
            {chr(10).join([f'- {k}: {v} contratos' for k, v in type_dist.items()][:5])}
            
            Tendencia de Valores:
            - La tendencia de valores en los últimos 12 meses es {trend}
            """
            
            return context
        except Exception as e:
            logger.error(f"Error getting context data: {str(e)}")
            return "Error al obtener el contexto de los contratos."

    @staticmethod
    def render_chat(active_df: Optional[pd.DataFrame] = None, 
                   historical_df: Optional[pd.DataFrame] = None) -> None:
        """Render the chat interface"""
        try:
            st.header("Análisis de Contratos con IA")
            
            # Initialize chat component if not in session state
            if 'chat_component' not in st.session_state:
                try:
                    st.session_state.chat_component = ChatComponent()
                    
                    # Initialize chat with context
                    if active_df is not None and historical_df is not None:
                        context = st.session_state.chat_component.get_context_data(active_df, historical_df)
                        initial_prompt = f"""
                        Por favor, analiza el siguiente contexto del sistema de contratos y ayúdame a responder preguntas sobre los contratos:

                        {context}

                        Por favor, ten en cuenta este contexto para responder preguntas sobre:
                        - Análisis de tendencias y patrones
                        - Comparaciones con datos históricos
                        - Recomendaciones basadas en la experiencia histórica
                        - Identificación de oportunidades y riesgos
                        """
                        st.session_state.chat_component.chat.send_message(initial_prompt)
                    
                    st.success("Conexión establecida con Gemini AI")
                except Exception as e:
                    st.error(f"Error al conectar con Gemini AI: {str(e)}")
                    return
            
            # Add clear chat history button
            if st.button("Limpiar Historial de Chat"):
                if hasattr(st.session_state.chat_component, 'chat'):
                    st.session_state.chat_component.chat = st.session_state.chat_component.model.start_chat(history=[])
                    st.success("Historial de chat limpiado")
                    st.rerun()

            # Chat interface
            user_input = st.text_input("Escribe tu pregunta sobre los contratos:", 
                                     placeholder="Ejemplo: ¿Cuál es la tendencia de valores en los últimos contratos?")
            
            if user_input:
                with st.spinner("Procesando tu pregunta..."):
                    response = st.session_state.chat_component.chat.send_message(user_input)
                    st.markdown("### Respuesta:")
                    st.markdown(response.text)
            
            # Display chat history
            if hasattr(st.session_state.chat_component, 'chat') and st.session_state.chat_component.chat.history:
                st.markdown("### Historial de Chat")
                for message in st.session_state.chat_component.chat.history[1:]:  # Skip the initial context message
                    role = "🤖 IA" if message.role == "model" else "👤 Usuario"
                    with st.container():
                        st.markdown(f"**{role}:**")
                        st.markdown(message.parts[0].text)
                        st.markdown("---")
                
        except Exception as e:
            logger.error(f"Error rendering chat interface: {str(e)}")
            st.error("Error al cargar la interfaz de chat")