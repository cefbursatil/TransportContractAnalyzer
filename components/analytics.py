import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.format_helpers import format_currency, format_percentage, format_large_number
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class AnalyticsComponent:
    @staticmethod
    def render_analytics(active_df: pd.DataFrame, historical_df: pd.DataFrame):
        """Render analytics dashboard with active and historical contract analysis"""
        try:
            if not isinstance(active_df, pd.DataFrame) or not isinstance(historical_df, pd.DataFrame):
                logger.error("Invalid input: DataFrames expected")
                st.error("Error: Invalid data format")
                return

            if active_df.empty and historical_df.empty:
                logger.warning("No data available for analysis")
                st.warning("No hay datos disponibles para análisis")
                return

            # Create two main tabs
            tab1, tab2 = st.tabs([
                "Contratos Activos",
                "Contratos Históricos"
            ])

            # Active Contracts Tab
            with tab1:
                st.header("Análisis de Contratos Activos")
                
                # Filters
                col1, col2, col3, col4 = st.columns(4)
                
                filtered_active_df = active_df.copy()
                
                with col1:
                    if 'fecha_de_publicacion' in filtered_active_df.columns:
                        min_date = pd.to_datetime(filtered_active_df['fecha_de_publicacion']).min()
                        max_date = pd.to_datetime(filtered_active_df['fecha_de_publicacion']).max()
                        date_range = st.date_input(
                            "Fecha de Publicación",
                            value=(min_date.date(), max_date.date()),
                            key="active_date_filter"
                        )
                        if isinstance(date_range, tuple) and len(date_range) == 2:
                            start_date, end_date = date_range
                            mask = (
                                pd.to_datetime(filtered_active_df['fecha_de_publicacion']).dt.date.between(
                                    start_date, end_date
                                )
                            )
                            filtered_active_df = filtered_active_df[mask]

                with col2:
                    if 'tipo_de_contrato' in filtered_active_df.columns:
                        unique_types = filtered_active_df['tipo_de_contrato'].dropna().unique()
                        contract_types = ['Todos'] + sorted(unique_types.tolist())
                        selected_type = st.selectbox(
                            'Tipo de Contrato',
                            contract_types,
                            key="active_type_filter"
                        )
                        if selected_type != 'Todos':
                            filtered_active_df = filtered_active_df[
                                filtered_active_df['tipo_de_contrato'] == selected_type
                            ]

                with col3:
                    if 'valor_del_contrato' in filtered_active_df.columns:
                        min_val = float(filtered_active_df['valor_del_contrato'].min())
                        max_val = float(filtered_active_df['valor_del_contrato'].max())
                        value_range = st.slider(
                            'Valor del Contrato',
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            format='$%f',
                            key="active_value_filter"
                        )
                        filtered_active_df = filtered_active_df[
                            (filtered_active_df['valor_del_contrato'] >= value_range[0]) &
                            (filtered_active_df['valor_del_contrato'] <= value_range[1])
                        ]

                with col4:
                    if 'nombre_entidad' in filtered_active_df.columns:
                        unique_entities = filtered_active_df['nombre_entidad'].dropna().unique()
                        entities = ['Todos'] + sorted(unique_entities.tolist())
                        selected_entity = st.selectbox(
                            'Entidad',
                            entities,
                            key="active_entity_filter"
                        )
                        if selected_entity != 'Todos':
                            filtered_active_df = filtered_active_df[
                                filtered_active_df['nombre_entidad'] == selected_entity
                            ]

                # Charts for Active Contracts
                col1, col2 = st.columns(2)

                with col1:
                    # Top 10 entities by contract value
                    if not filtered_active_df.empty:
                        entity_values = filtered_active_df.groupby('nombre_entidad')['valor_del_contrato'].sum()
                        top_entities = entity_values.nlargest(10)
                        
                        fig = px.bar(
                            x=top_entities.index.tolist(),
                            y=top_entities.values,
                            title='Top 10 Entidades por Valor de Contrato',
                            labels={'x': 'Entidad', 'y': 'Valor Total (COP)'}
                        )
                        fig.update_layout(
                            xaxis_tickangle=-45,
                            height=400,
                            yaxis_tickformat=',.0f'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Regions with highest contract value
                    if 'departamento' in filtered_active_df.columns and not filtered_active_df.empty:
                        dept_values = filtered_active_df.groupby('departamento')['valor_del_contrato'].sum()
                        region_values = dept_values.sort_values(ascending=True)
                        
                        fig = px.bar(
                            x=region_values.values,
                            y=region_values.index.tolist(),
                            orientation='h',
                            title='Valor Total de Contratos por Región',
                            labels={'x': 'Valor Total (COP)', 'y': 'Región'}
                        )
                        fig.update_layout(
                            height=400,
                            xaxis_tickformat=',.0f'
                        )
                        st.plotly_chart(fig, use_container_width=True)

            # Historical Contracts Tab
            with tab2:
                st.header("Análisis de Contratos Históricos")
                
                # Filters
                col1, col2, col3, col4, col5 = st.columns(5)
                
                filtered_hist_df = historical_df.copy()
                
                with col1:
                    if 'fecha_de_firma' in filtered_hist_df.columns:
                        min_date = pd.to_datetime(filtered_hist_df['fecha_de_firma']).min()
                        max_date = pd.to_datetime(filtered_hist_df['fecha_de_firma']).max()
                        date_range = st.date_input(
                            "Fecha de Firma",
                            value=(min_date.date(), max_date.date()),
                            key="hist_date_filter"
                        )
                        if isinstance(date_range, tuple) and len(date_range) == 2:
                            start_date, end_date = date_range
                            mask = (
                                pd.to_datetime(filtered_hist_df['fecha_de_firma']).dt.date.between(
                                    start_date, end_date
                                )
                            )
                            filtered_hist_df = filtered_hist_df[mask]

                with col2:
                    if 'tipo_de_contrato' in filtered_hist_df.columns:
                        unique_types = filtered_hist_df['tipo_de_contrato'].dropna().unique()
                        contract_types = ['Todos'] + sorted(unique_types.tolist())
                        selected_type = st.selectbox(
                            'Tipo de Contrato',
                            contract_types,
                            key="hist_type_filter"
                        )
                        if selected_type != 'Todos':
                            filtered_hist_df = filtered_hist_df[
                                filtered_hist_df['tipo_de_contrato'] == selected_type
                            ]

                with col3:
                    if 'valor_del_contrato' in filtered_hist_df.columns:
                        min_val = float(filtered_hist_df['valor_del_contrato'].min())
                        max_val = float(filtered_hist_df['valor_del_contrato'].max())
                        value_range = st.slider(
                            'Valor del Contrato',
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            format='$%f',
                            key="hist_value_filter"
                        )
                        filtered_hist_df = filtered_hist_df[
                            (filtered_hist_df['valor_del_contrato'] >= value_range[0]) &
                            (filtered_hist_df['valor_del_contrato'] <= value_range[1])
                        ]

                with col4:
                    if 'nombre_entidad' in filtered_hist_df.columns:
                        unique_entities = filtered_hist_df['nombre_entidad'].dropna().unique()
                        entities = ['Todos'] + sorted(unique_entities.tolist())
                        selected_entity = st.selectbox(
                            'Entidad',
                            entities,
                            key="hist_entity_filter"
                        )
                        if selected_entity != 'Todos':
                            filtered_hist_df = filtered_hist_df[
                                filtered_hist_df['nombre_entidad'] == selected_entity
                            ]

                with col5:
                    if 'proveedor_adjudicado' in filtered_hist_df.columns:
                        unique_providers = filtered_hist_df['proveedor_adjudicado'].dropna().unique()
                        providers = ['Todos'] + sorted(unique_providers.tolist())
                        selected_provider = st.selectbox(
                            'Proveedor',
                            providers,
                            key="hist_provider_filter"
                        )
                        if selected_provider != 'Todos':
                            filtered_hist_df = filtered_hist_df[
                                filtered_hist_df['proveedor_adjudicado'] == selected_provider
                            ]

                # Charts for Historical Contracts
                col1, col2 = st.columns(2)

                with col1:
                    # Top 10 entities by contract value
                    if not filtered_hist_df.empty:
                        entity_values = filtered_hist_df.groupby('nombre_entidad')['valor_del_contrato'].sum()
                        top_entities = entity_values.nlargest(10)
                        
                        fig = px.bar(
                            x=top_entities.index.tolist(),
                            y=top_entities.values,
                            title='Top 10 Entidades por Valor de Contrato',
                            labels={'x': 'Entidad', 'y': 'Valor Total (COP)'}
                        )
                        fig.update_layout(
                            xaxis_tickangle=-45,
                            height=400,
                            yaxis_tickformat=',.0f'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Regions with highest contract value
                    if 'departamento' in filtered_hist_df.columns and not filtered_hist_df.empty:
                        dept_values = filtered_hist_df.groupby('departamento')['valor_del_contrato'].sum()
                        region_values = dept_values.sort_values(ascending=True)
                        
                        fig = px.bar(
                            x=region_values.values,
                            y=region_values.index.tolist(),
                            orientation='h',
                            title='Valor Total de Contratos por Región',
                            labels={'x': 'Valor Total (COP)', 'y': 'Región'}
                        )
                        fig.update_layout(
                            height=400,
                            xaxis_tickformat=',.0f'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                col3, col4 = st.columns(2)

                with col3:
                    # Top providers by contract value
                    if 'proveedor_adjudicado' in filtered_hist_df.columns and not filtered_hist_df.empty:
                        provider_values = filtered_hist_df.groupby('proveedor_adjudicado')['valor_del_contrato'].sum()
                        top_providers = provider_values.nlargest(10)
                        
                        fig = px.bar(
                            x=top_providers.index.tolist(),
                            y=top_providers.values,
                            title='Top 10 Proveedores por Valor de Contrato',
                            labels={'x': 'Proveedor', 'y': 'Valor Total (COP)'}
                        )
                        fig.update_layout(
                            xaxis_tickangle=-45,
                            height=400,
                            yaxis_tickformat=',.0f'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col4:
                    # Regional distribution analysis
                    if 'departamento' in filtered_hist_df.columns and not filtered_hist_df.empty:
                        region_dist = filtered_hist_df.groupby('departamento').agg({
                            'valor_del_contrato': ['sum', 'count']
                        }).reset_index()
                        region_dist.columns = ['departamento', 'valor_total', 'cantidad']
                        
                        fig = px.scatter(
                            region_dist,
                            x='valor_total',
                            y='cantidad',
                            text='departamento',
                            title='Distribución Regional: Valor vs Cantidad',
                            labels={
                                'valor_total': 'Valor Total (COP)',
                                'cantidad': 'Cantidad de Contratos'
                            }
                        )
                        fig.update_traces(textposition='top center')
                        fig.update_layout(
                            height=400,
                            xaxis_tickformat=',.0f'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                # Comparative Analysis Section
                st.header("Análisis Comparativo")
                
                # Compare contract values between active and historical
                if not active_df.empty and not historical_df.empty:
                    active_values = active_df.groupby('nombre_entidad')['valor_del_contrato'].sum()
                    hist_values = historical_df.groupby('nombre_entidad')['valor_del_contrato'].sum()
                    
                    # Get common entities
                    common_entities = sorted(list(set(active_values.index) & set(hist_values.index)))
                    
                    if common_entities:
                        comparison_data = []
                        for entity in common_entities:
                            comparison_data.append({
                                'Entidad': entity,
                                'Tipo': 'Activos',
                                'Valor': active_values[entity]
                            })
                            comparison_data.append({
                                'Entidad': entity,
                                'Tipo': 'Históricos',
                                'Valor': hist_values[entity]
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        
                        fig = px.bar(
                            comparison_df,
                            x='Entidad',
                            y='Valor',
                            color='Tipo',
                            title='Comparación de Valores por Entidad',
                            barmode='group',
                            labels={'Valor': 'Valor Total (COP)'}
                        )
                        
                        fig.update_layout(
                            xaxis_tickangle=-45,
                            height=500,
                            yaxis_tickformat=',.0f'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No hay entidades comunes para comparar entre contratos activos e históricos")

        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error(f"Error al generar análisis: {str(e)}")
