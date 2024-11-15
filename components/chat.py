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

            context_parts = []

            # Active Contracts Section
            active_section = f"""
            Contratos Activos con Fecha de Presentación Futura:
            - Total de contratos: {len(future_contracts)}
            - Tipos de contratos principales: {', '.join(future_contracts['tipo_de_contrato'].value_counts().nlargest(3).index.tolist()) if not future_contracts.empty else 'N/A'}
            """
            context_parts.append(active_section)

            # Historical Analytics Section
            if not historical_df.empty:
                hist_analytics = {
                    'total_contracts': len(historical_df),
                    'avg_value': historical_df['valor_del_contrato'].mean() if 'valor_del_contrato' in historical_df.columns else 0,
                    'total_value': historical_df['valor_del_contrato'].sum() if 'valor_del_contrato' in historical_df.columns else 0
                }

                hist_section = f"""
                Análisis Histórico General:
                - Total de contratos históricos: {hist_analytics['total_contracts']:,}
                - Valor promedio de contratos: ${hist_analytics['avg_value']:,.2f}
                - Valor total histórico: ${hist_analytics['total_value']:,.2f}
                """
                context_parts.append(hist_section)

                # Top 10 Suppliers
                if 'proveedor_adjudicado' in historical_df.columns and 'valor_del_contrato' in historical_df.columns:
                    top_suppliers = historical_df.groupby('proveedor_adjudicado')['valor_del_contrato'].sum().nlargest(10)
                    suppliers_section = """
                    Top 10 Proveedores por Valor Total de Contratos:
                    """ + "\n".join([f"- {name}: ${value:,.2f}" for name, value in top_suppliers.items()])
                    context_parts.append(suppliers_section)

                # Top 10 Entities
                if 'nombre_entidad' in historical_df.columns and 'valor_del_contrato' in historical_df.columns:
                    top_entities = historical_df.groupby('nombre_entidad')['valor_del_contrato'].sum().nlargest(10)
                    entities_section = """
                    Top 10 Entidades por Valor Total de Contratos:
                    """ + "\n".join([f"- {name}: ${value:,.2f}" for name, value in top_entities.items()])
                    context_parts.append(entities_section)

                # Monthly Contract Frequency
                if 'fecha_de_firma' in historical_df.columns and 'id_contrato' in historical_df.columns:
                    monthly_contracts = historical_df.groupby(
                        pd.to_datetime(historical_df['fecha_de_firma']).dt.strftime('%Y-%m')
                    )['id_contrato'].count()
                    peak_months = monthly_contracts.nlargest(5)
                    
                    frequency_section = """
                    Frecuencia de Contratos por Mes (Top 5 meses con más contratos):
                    """ + "\n".join([f"- {month}: {count} contratos" for month, count in peak_months.items()])
                    context_parts.append(frequency_section)

                # Regional Distribution
                if 'departamento' in historical_df.columns and 'valor_del_contrato' in historical_df.columns:
                    region_distribution = historical_df.groupby('departamento')['valor_del_contrato'].sum().nlargest(5)
                    region_section = """
                    Distribución Regional de Contratos (Top 5 departamentos):
                    """ + "\n".join([f"- {dept}: ${value:,.2f}" for dept, value in region_distribution.items()])
                    context_parts.append(region_section)

                # Contract Value Trends
                if 'fecha_de_firma' in historical_df.columns and 'valor_del_contrato' in historical_df.columns:
                    historical_df['year_month'] = pd.to_datetime(historical_df['fecha_de_firma']).dt.to_period('M')
                    monthly_values = historical_df.groupby('year_month')['valor_del_contrato'].mean()
                    
                    recent_trend = "creciente" if monthly_values.iloc[-1] > monthly_values.iloc[-2] else "decreciente"
                    avg_recent = monthly_values.tail(3).mean()
                    avg_previous = monthly_values.tail(6).head(3).mean()
                    trend_strength = "fuerte" if abs(avg_recent - avg_previous)/avg_previous > 0.1 else "moderada"
                    
                    trend_section = f"""
                    Tendencias de Valor de Contratos:
                    - Tendencia reciente: {recent_trend} ({trend_strength})
                    - Valor promedio últimos 3 meses: ${avg_recent:,.2f}
                    - Variación respecto a meses anteriores: {((avg_recent/avg_previous - 1) * 100):,.1f}%
                    """
                    context_parts.append(trend_section)

            # Join all sections with proper spacing
            context = "\n\n".join(context_parts)
            
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
                    st.success("Conexión establecida con Gemini AI")
                except Exception as e:
                    st.error(f"Error al conectar con Gemini AI: {str(e)}")
                    return

            # Initialize context in session state if not present
            if 'chat_context' not in st.session_state and active_df is not None and historical_df is not None:
                st.session_state.chat_context = st.session_state.chat_component.get_context_data(active_df, historical_df)
                st.session_state.context_sent = False

            # Add clear chat history button
            if st.button("Limpiar Historial de Chat"):
                if hasattr(st.session_state.chat_component, 'chat'):
                    st.session_state.chat_component.chat = st.session_state.chat_component.model.start_chat(history=[])
                    st.session_state.context_sent = False
                    st.success("Historial de chat limpiado")
                    st.rerun()

            # Chat interface
            user_input = st.text_input("Escribe tu pregunta sobre los contratos:", 
                                     placeholder="Ejemplo: ¿Cuáles son los principales proveedores y su distribución de contratos?")
            
            if user_input:
                with st.spinner("Procesando tu pregunta..."):
                    # For the first message, prepend the context
                    if not st.session_state.get('context_sent', False):
                        context_prompt = f"""
                        Por favor, analiza el siguiente contexto del sistema de contratos y ayúdame a responder preguntas sobre los contratos:

                        {st.session_state.chat_context}

                        Por favor, ten en cuenta este contexto para responder preguntas sobre:
                        - Análisis de tendencias y patrones en valores y frecuencias de contratos
                        - Comparaciones con datos históricos por región y proveedor
                        - Recomendaciones basadas en el comportamiento histórico de proveedores y entidades
                        - Identificación de oportunidades y riesgos basados en tendencias
                        - Análisis de distribución regional y temporal de contratos

                        Primera pregunta del usuario: {user_input}
                        """
                        response = st.session_state.chat_component.chat.send_message(context_prompt)
                        st.session_state.context_sent = True
                    else:
                        # For subsequent messages, just send the user input
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
