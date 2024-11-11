import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class AnalyticsComponent:
    @staticmethod
    def render_analytics(active_df, historical_df):
        """Render analytics with improved validation and error handling"""
        try:
            # Validate input data
            if not isinstance(active_df, pd.DataFrame) or not isinstance(historical_df, pd.DataFrame):
                logger.error("Invalid input: DataFrames expected")
                st.error("Error: Invalid data format")
                return

            if active_df.empty and historical_df.empty:
                logger.warning("No data available for analysis")
                st.warning("No hay datos disponibles para análisis")
                return
                
            tab1, tab2 = st.tabs(["Contratos Activos", "Contratos Históricos"])
            
            with tab1:
                with st.spinner("Cargando dashboard de contratos activos..."):
                    AnalyticsComponent._render_active_contracts_dashboard(active_df)
                    
            with tab2:
                with st.spinner("Cargando dashboard de contratos históricos..."):
                    AnalyticsComponent._render_historical_contracts_dashboard(historical_df)
                    
        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error("Error al generar análisis")

    @staticmethod
    def _validate_dataframe(df, required_columns):
        """Validate DataFrame has required columns"""
        if df is None or df.empty:
            return False
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        return True

    @staticmethod
    def _render_active_contracts_dashboard(df):
        """Render active contracts dashboard with validation"""
        try:
            required_columns = ['valor_del_contrato', 'departamento', 'fecha_de_firma']
            if not AnalyticsComponent._validate_dataframe(df, required_columns):
                st.warning("Datos insuficientes para mostrar el dashboard de contratos activos")
                return

            st.header("Dashboard de Contratos Activos")
            
            with st.spinner("Calculando métricas principales..."):
                # Key metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_value = df['valor_del_contrato'].sum()
                    st.metric(
                        "Valor Total de Contratos Activos",
                        f"${total_value:,.0f}"
                    )
                    
                with col2:
                    contract_count = len(df)
                    st.metric(
                        "Número de Contratos Activos",
                        f"{contract_count:,}"
                    )
                    
                with col3:
                    avg_value = df['valor_del_contrato'].mean()
                    st.metric(
                        "Valor Promedio",
                        f"${avg_value:,.0f}"
                    )
                    
                with col4:
                    if 'duracion' in df.columns:
                        avg_duration = df['duracion'].mean()
                        st.metric(
                            "Duración Promedio (días)",
                            f"{avg_duration:.0f}"
                        )
            
            # Active Contracts Analysis Section
            st.subheader("Análisis de Contratos Activos")
            
            with st.spinner("Generando visualizaciones..."):
                # Contract Value Distribution
                if 'valor_del_contrato' in df.columns:
                    fig_box = px.box(
                        df,
                        y='valor_del_contrato',
                        title='Distribución de Valores de Contratos Activos',
                        points='all'
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
                
                # Geographic Distribution
                if 'departamento' in df.columns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        dept_values = df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
                        fig_map = px.bar(
                            dept_values,
                            x='departamento',
                            y='valor_del_contrato',
                            title='Valor Total por Departamento'
                        )
                        st.plotly_chart(fig_map, use_container_width=True)
                    
                    with col2:
                        dept_counts = df['departamento'].value_counts().reset_index()
                        dept_counts.columns = ['departamento', 'count']
                        fig_pie = px.pie(
                            dept_counts,
                            values='count',
                            names='departamento',
                            title='Distribución de Contratos por Departamento'
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

                # Timeline Analysis
                if 'fecha_de_firma' in df.columns:
                    st.subheader("Análisis Temporal de Contratos Activos")
                    df['month'] = pd.to_datetime(df['fecha_de_firma']).dt.to_period('M')
                    monthly_data = df.groupby('month').agg({
                        'valor_del_contrato': ['sum', 'count']
                    }).reset_index()
                    monthly_data['month'] = monthly_data['month'].astype(str)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=monthly_data['month'],
                        y=monthly_data['valor_del_contrato']['sum'],
                        name='Valor Total',
                        marker_color='blue'
                    ))
                    fig.add_trace(go.Scatter(
                        x=monthly_data['month'],
                        y=monthly_data['valor_del_contrato']['count'],
                        name='Número de Contratos',
                        yaxis='y2',
                        line=dict(color='red')
                    ))
                    fig.update_layout(
                        title='Evolución Mensual de Contratos Activos',
                        yaxis=dict(title='Valor Total (COP)'),
                        yaxis2=dict(title='Número de Contratos', overlaying='y', side='right')
                    )
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.error(f"Error in active contracts dashboard: {str(e)}")
            st.error("Error al generar el dashboard de contratos activos")

    @staticmethod
    def _render_historical_contracts_dashboard(df):
        """Render historical contracts dashboard with validation"""
        try:
            required_columns = ['valor_del_contrato', 'fecha_de_firma']
            if not AnalyticsComponent._validate_dataframe(df, required_columns):
                st.warning("Datos insuficientes para mostrar el dashboard de contratos históricos")
                return

            st.header("Dashboard de Contratos Históricos")
            
            with st.spinner("Calculando métricas principales..."):
                # Key metrics for historical contracts
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_historical_value = df['valor_del_contrato'].sum()
                    st.metric(
                        "Valor Total Histórico",
                        f"${total_historical_value:,.0f}"
                    )
                
                with col2:
                    contract_count = len(df)
                    st.metric(
                        "Total Contratos Históricos",
                        f"{contract_count:,}"
                    )
                
                with col3:
                    avg_value = df['valor_del_contrato'].mean()
                    st.metric(
                        "Valor Promedio Histórico",
                        f"${avg_value:,.0f}"
                    )
                
                with col4:
                    if 'estado_del_contrato' in df.columns:
                        completed_count = df[df['estado_del_contrato'] == 'Terminado'].shape[0]
                        completion_rate = (completed_count / len(df)) * 100 if len(df) > 0 else 0
                        st.metric(
                            "Tasa de Finalización",
                            f"{completion_rate:.1f}%"
                        )
            
            with st.spinner("Generando visualizaciones..."):
                # Historical Trends Analysis
                st.subheader("Análisis de Tendencias Históricas")
                
                # Year-over-Year Analysis
                if 'fecha_de_firma' in df.columns:
                    df['year'] = pd.to_datetime(df['fecha_de_firma']).dt.year
                    yearly_data = df.groupby('year').agg({
                        'valor_del_contrato': ['sum', 'mean', 'count']
                    }).reset_index()
                    
                    # Yearly trends
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=yearly_data['year'],
                        y=yearly_data['valor_del_contrato']['sum'],
                        name='Valor Total Anual'
                    ))
                    fig.add_trace(go.Scatter(
                        x=yearly_data['year'],
                        y=yearly_data['valor_del_contrato']['mean'],
                        name='Valor Promedio',
                        yaxis='y2'
                    ))
                    fig.update_layout(
                        title='Tendencias Anuales',
                        yaxis=dict(title='Valor Total (COP)'),
                        yaxis2=dict(title='Valor Promedio', overlaying='y', side='right')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Contract Type Distribution
                if 'tipo_de_contrato' in df.columns:
                    st.subheader("Distribución por Tipo de Contrato")
                    contract_types = df['tipo_de_contrato'].value_counts()
                    fig_pie = px.pie(
                        values=contract_types.values,
                        names=contract_types.index,
                        title='Distribución de Tipos de Contrato'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Duration Analysis
                if 'duracion' in df.columns:
                    st.subheader("Análisis de Duración de Contratos")
                    fig_hist = px.histogram(
                        df,
                        x='duracion',
                        title='Distribución de Duración de Contratos',
                        nbins=30
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

        except Exception as e:
            logger.error(f"Error in historical contracts dashboard: {str(e)}")
            st.error("Error al generar el dashboard de contratos históricos")
