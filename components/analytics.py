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
        """Render analytics dashboards for active and historical contracts"""
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
                
            tab1, tab2, tab3 = st.tabs(["Contratos Activos", "Contratos Históricos", "Análisis Comparativo"])
            
            with tab1:
                st.header("Dashboard de Contratos Activos")
                AnalyticsComponent._render_active_metrics(active_df)
                AnalyticsComponent._render_active_visualizations(active_df)
                    
            with tab2:
                st.header("Dashboard de Contratos Históricos")
                AnalyticsComponent._render_historical_metrics(historical_df)
                AnalyticsComponent._render_historical_visualizations(historical_df)

            with tab3:
                st.header("Análisis Comparativo")
                AnalyticsComponent._render_comparative_analytics(active_df, historical_df)
                    
        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error("Error al generar análisis")

    @staticmethod
    def _render_active_metrics(df):
        """Render metrics specific to active contracts"""
        if df.empty:
            st.warning("No hay contratos activos disponibles")
            return

        # Active contracts specific metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = df['valor_del_contrato'].sum()
            st.metric("Valor Total Activo", f"${total_value:,.0f}")
        
        with col2:
            avg_value = df['valor_del_contrato'].mean()
            st.metric("Valor Promedio", f"${avg_value:,.0f}")
        
        with col3:
            current_month = pd.Timestamp.now().replace(day=1)
            monthly_contracts = df[pd.to_datetime(df['fecha_de_firma']).dt.to_period('M') == 
                                pd.Period(current_month, freq='M')].shape[0]
            st.metric("Contratos Nuevos (Mes Actual)", monthly_contracts)
        
        with col4:
            if 'duracion' in df.columns:
                avg_duration = df['duracion'].mean()
                st.metric("Duración Promedio (días)", f"{avg_duration:.0f}")

    @staticmethod
    def _render_active_visualizations(df):
        """Render visualizations specific to active contracts"""
        if df.empty:
            return

        # Contract Value Distribution
        st.subheader("Distribución de Valores de Contratos Activos")
        fig_box = px.box(df, y='valor_del_contrato', points='all')
        st.plotly_chart(fig_box, use_container_width=True)

        # Geographical Distribution
        if 'departamento' in df.columns:
            st.subheader("Distribución Geográfica")
            col1, col2 = st.columns(2)
            
            with col1:
                dept_values = df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
                fig_geo = px.bar(dept_values, x='departamento', y='valor_del_contrato',
                               title='Valor Total por Departamento')
                st.plotly_chart(fig_geo, use_container_width=True)
            
            with col2:
                dept_counts = df['departamento'].value_counts()
                fig_pie = px.pie(values=dept_counts.values, names=dept_counts.index,
                               title='Distribución de Contratos por Departamento')
                st.plotly_chart(fig_pie, use_container_width=True)

        # Recent Activity Timeline
        if 'fecha_de_firma' in df.columns:
            st.subheader("Actividad Reciente")
            df['mes'] = pd.to_datetime(df['fecha_de_firma']).dt.to_period('M')
            monthly_activity = df.groupby('mes').agg({
                'valor_del_contrato': ['sum', 'count']
            }).reset_index()
            monthly_activity['mes'] = monthly_activity['mes'].astype(str)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_activity['mes'],
                y=monthly_activity['valor_del_contrato']['sum'],
                name='Valor Total',
                marker_color='blue'
            ))
            fig.add_trace(go.Scatter(
                x=monthly_activity['mes'],
                y=monthly_activity['valor_del_contrato']['count'],
                name='Número de Contratos',
                yaxis='y2',
                line=dict(color='red')
            ))
            fig.update_layout(
                title='Actividad Mensual de Contratos Activos',
                yaxis=dict(title='Valor Total (COP)'),
                yaxis2=dict(title='Número de Contratos', overlaying='y', side='right')
            )
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _render_historical_metrics(df):
        """Render metrics specific to historical contracts"""
        if df.empty:
            st.warning("No hay contratos históricos disponibles")
            return

        # Historical specific metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_historical = df['valor_del_contrato'].sum()
            st.metric("Valor Total Histórico", f"${total_historical:,.0f}")
        
        with col2:
            completed_count = df[df['estado_contrato'] == 'Terminado'].shape[0] if 'estado_contrato' in df.columns else 0
            completion_rate = (completed_count / len(df)) * 100 if len(df) > 0 else 0
            st.metric("Tasa de Finalización", f"{completion_rate:.1f}%")
        
        with col3:
            avg_historical = df['valor_del_contrato'].mean()
            st.metric("Valor Promedio Histórico", f"${avg_historical:,.0f}")
        
        with col4:
            if 'duracion' in df.columns:
                avg_duration = df['duracion'].mean()
                st.metric("Duración Promedio Histórica", f"{avg_duration:.0f} días")

    @staticmethod
    def _render_historical_visualizations(df):
        """Render visualizations specific to historical contracts"""
        if df.empty:
            return

        # Historical Trends
        if 'fecha_de_firma' in df.columns:
            st.subheader("Tendencias Históricas")
            df['año'] = pd.to_datetime(df['fecha_de_firma']).dt.year
            yearly_trends = df.groupby('año').agg({
                'valor_del_contrato': ['sum', 'mean', 'count']
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=yearly_trends['año'],
                y=yearly_trends['valor_del_contrato']['sum'],
                name='Valor Total Anual'
            ))
            fig.add_trace(go.Scatter(
                x=yearly_trends['año'],
                y=yearly_trends['valor_del_contrato']['mean'],
                name='Valor Promedio',
                yaxis='y2'
            ))
            fig.update_layout(
                title='Análisis Anual de Contratos Históricos',
                yaxis=dict(title='Valor Total (COP)'),
                yaxis2=dict(title='Valor Promedio', overlaying='y', side='right')
            )
            st.plotly_chart(fig, use_container_width=True)

        # Contract Status Distribution
        if 'estado_contrato' in df.columns:
            st.subheader("Estado de Contratos Históricos")
            status_dist = df['estado_contrato'].value_counts()
            fig_status = px.pie(
                values=status_dist.values,
                names=status_dist.index,
                title='Distribución por Estado de Contrato'
            )
            st.plotly_chart(fig_status, use_container_width=True)

    @staticmethod
    def _render_comparative_analytics(active_df, historical_df):
        """Render comparative analytics between active and historical contracts"""
        if active_df.empty or historical_df.empty:
            st.warning("No hay suficientes datos para realizar análisis comparativo")
            return

        st.subheader("Métricas Comparativas")
        
        # Calculate comparative metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            active_avg = active_df['valor_del_contrato'].mean()
            hist_avg = historical_df['valor_del_contrato'].mean()
            percent_diff = ((active_avg - hist_avg) / hist_avg) * 100 if hist_avg != 0 else 0
            st.metric(
                "Diferencia en Valor Promedio",
                f"${active_avg:,.0f}",
                f"{percent_diff:+.1f}% vs histórico"
            )

        with col2:
            active_count = len(active_df)
            hist_count = len(historical_df)
            count_diff = ((active_count - hist_count) / hist_count) * 100 if hist_count != 0 else 0
            st.metric(
                "Volumen de Contratos",
                f"{active_count:,}",
                f"{count_diff:+.1f}% vs histórico"
            )

        with col3:
            if 'duracion' in active_df.columns and 'duracion' in historical_df.columns:
                active_duration = active_df['duracion'].mean()
                hist_duration = historical_df['duracion'].mean()
                duration_diff = ((active_duration - hist_duration) / hist_duration) * 100 if hist_duration != 0 else 0
                st.metric(
                    "Diferencia en Duración Promedio",
                    f"{active_duration:.0f} días",
                    f"{duration_diff:+.1f}% vs histórico"
                )

        # Value Distribution Comparison
        st.subheader("Comparación de Distribución de Valores")
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=active_df['valor_del_contrato'],
            name='Contratos Activos',
            boxpoints='outliers'
        ))
        fig.add_trace(go.Box(
            y=historical_df['valor_del_contrato'],
            name='Contratos Históricos',
            boxpoints='outliers'
        ))
        fig.update_layout(
            title='Distribución de Valores: Activos vs Históricos',
            yaxis_title='Valor del Contrato (COP)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Geographical Comparison
        if 'departamento' in active_df.columns and 'departamento' in historical_df.columns:
            st.subheader("Comparación Geográfica")
            
            # Prepare data
            active_dept = active_df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
            hist_dept = historical_df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
            
            # Merge data
            dept_comparison = pd.merge(
                active_dept, 
                hist_dept, 
                on='departamento', 
                suffixes=('_activo', '_historico'),
                how='outer'
            ).fillna(0)
            
            # Create comparative bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dept_comparison['departamento'],
                y=dept_comparison['valor_del_contrato_activo'],
                name='Contratos Activos'
            ))
            fig.add_trace(go.Bar(
                x=dept_comparison['departamento'],
                y=dept_comparison['valor_del_contrato_historico'],
                name='Contratos Históricos'
            ))
            fig.update_layout(
                title='Comparación de Valores por Departamento',
                barmode='group',
                xaxis_title='Departamento',
                yaxis_title='Valor Total (COP)'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Time-based Comparison
        if 'fecha_de_firma' in active_df.columns and 'fecha_de_firma' in historical_df.columns:
            st.subheader("Comparación Temporal")
            
            # Prepare monthly data
            active_df['mes'] = pd.to_datetime(active_df['fecha_de_firma']).dt.to_period('M')
            historical_df['mes'] = pd.to_datetime(historical_df['fecha_de_firma']).dt.to_period('M')
            
            active_monthly = active_df.groupby('mes')['valor_del_contrato'].agg(['sum', 'count']).reset_index()
            hist_monthly = historical_df.groupby('mes')['valor_del_contrato'].agg(['sum', 'count']).reset_index()
            
            # Create time series comparison
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=active_monthly['mes'].astype(str),
                y=active_monthly['sum'],
                name='Valor Total (Activos)',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=hist_monthly['mes'].astype(str),
                y=hist_monthly['sum'],
                name='Valor Total (Históricos)',
                line=dict(color='red')
            ))
            fig.update_layout(
                title='Comparación de Valores Totales por Mes',
                xaxis_title='Mes',
                yaxis_title='Valor Total (COP)'
            )
            st.plotly_chart(fig, use_container_width=True)
