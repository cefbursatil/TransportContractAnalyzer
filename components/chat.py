import streamlit as st
import google.generativeai as genai
import os
import logging
from typing import Optional, Dict, Any
import pandas as pd

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

    def analyze_contract(self, contract_data: Dict[str, Any]) -> str:
        """Analyze a single contract using Gemini AI"""
        try:
            # Format monetary values for better readability
            valor = contract_data.get('valor_del_contrato', 0)
            valor_formatted = f"${valor:,.2f}" if isinstance(valor, (int, float)) else str(valor)

            prompt = f"""
            Por favor, analiza el siguiente contrato de transporte y proporciona un análisis detallado:
            
            Detalles del Contrato:
            - Entidad: {contract_data.get('nombre_entidad', 'N/A')}
            - Tipo: {contract_data.get('tipo_de_contrato', 'N/A')}
            - Valor: {valor_formatted}
            - Descripción: {contract_data.get('descripcion_del_proceso', 'N/A')}
            - Departamento: {contract_data.get('departamento', 'N/A')}
            - Estado: {contract_data.get('estado_contrato', 'N/A')}
            
            Por favor proporciona:
            1. Resumen Ejecutivo:
               - Breve descripción del contrato
               - Objetivo principal
               - Alcance del proyecto
            
            2. Análisis Financiero:
               - Evaluación del valor del contrato
               - Recomendaciones sobre el aspecto financiero
            
            3. Análisis de Riesgos:
               - Principales riesgos identificados
               - Medidas de mitigación sugeridas
               - Puntos de atención especial
            
            4. Recomendaciones:
               - Sugerencias para el monitoreo
               - Aspectos clave a supervisar
               - Mejores prácticas aplicables
            """
            
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error analyzing contract: {str(e)}")
            return f"Error al analizar el contrato: {str(e)}"

    @staticmethod
    def render_chat(df: Optional[pd.DataFrame] = None) -> None:
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
            
            # Add clear chat history button
            if st.button("Limpiar Historial de Chat"):
                if hasattr(st.session_state.chat_component, 'chat'):
                    st.session_state.chat_component.chat = st.session_state.chat_component.model.start_chat(history=[])
                    st.success("Historial de chat limpiado")
                    st.rerun()
            
            # Contract selection
            if df is not None and not isinstance(df, pd.DataFrame):
                logger.error("Invalid input: DataFrame expected")
                st.error("Error: Invalid data format")
                return
            
            if df is not None and not df.empty:
                # Filter for contract selection
                col1, col2 = st.columns(2)
                
                filtered_df = df.copy()
                
                with col1:
                    if 'nombre_entidad' in filtered_df.columns:
                        entities = sorted(filtered_df['nombre_entidad'].dropna().unique())
                        selected_entity = st.selectbox(
                            "Filtrar por Entidad",
                            options=['Todos'] + list(entities)
                        )
                        if selected_entity != 'Todos':
                            filtered_df = filtered_df[filtered_df['nombre_entidad'] == selected_entity]
                
                with col2:
                    if 'tipo_de_contrato' in filtered_df.columns:
                        contract_types = sorted(filtered_df['tipo_de_contrato'].dropna().unique())
                        selected_type = st.selectbox(
                            'Tipo de Contrato',
                            options=['Todos'] + list(contract_types)
                        )
                        if selected_type != 'Todos':
                            filtered_df = filtered_df[filtered_df['tipo_de_contrato'] == selected_type]
                
                # Contract selection
                if not filtered_df.empty:
                    st.markdown("### Seleccionar Contrato para Análisis")
                    
                    # Create contract descriptions
                    contract_list = []
                    for idx, row in filtered_df.iterrows():
                        valor = row.get('valor_del_contrato', 'N/A')
                        valor_formatted = f"${valor:,.2f}" if isinstance(valor, (int, float)) else str(valor)
                        desc = (f"{row['nombre_entidad']} - "
                               f"{row['tipo_de_contrato']} - "
                               f"Valor: {valor_formatted}")
                        contract_list.append({"id": idx, "description": desc})
                    
                    if contract_list:
                        selected_contract = st.selectbox(
                            "Seleccionar Contrato",
                            options=[c["description"] for c in contract_list],
                            key="contract_selector"
                        )
                        
                        if selected_contract:
                            # Get selected contract data
                            selected_idx = next(c["id"] for c in contract_list if c["description"] == selected_contract)
                            contract_data = filtered_df.loc[selected_idx].to_dict()
                            
                            # Analyze button
                            if st.button("Analizar Contrato", key="analyze_button"):
                                with st.spinner("Analizando contrato con IA..."):
                                    analysis = st.session_state.chat_component.analyze_contract(contract_data)
                                    st.markdown("### Análisis del Contrato")
                                    st.markdown(analysis)
                
                # Chat history
                if hasattr(st.session_state.chat_component, 'chat'):
                    if st.session_state.chat_component.chat.history:
                        st.markdown("### Historial de Chat")
                        for message in st.session_state.chat_component.chat.history:
                            role = "🤖 IA" if message.role == "model" else "👤 Usuario"
                            with st.container():
                                st.markdown(f"**{role}:**")
                                st.markdown(message.parts[0].text)
                                st.markdown("---")
            else:
                st.warning("No hay contratos disponibles para análisis")
                
        except Exception as e:
            logger.error(f"Error rendering chat interface: {str(e)}")
            st.error("Error al cargar la interfaz de chat")
