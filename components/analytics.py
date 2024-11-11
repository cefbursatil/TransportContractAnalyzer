import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import logging
import json

logger = logging.getLogger(__name__)

# Colombia department coordinates (approximate centroids)
COLOMBIA_DEPARTMENTS = {
    'AMAZONAS': {'lat': -1.0, 'lon': -71.9},
    'ANTIOQUIA': {'lat': 7.0, 'lon': -75.5},
    'ARAUCA': {'lat': 6.5, 'lon': -71.0},
    'ATLANTICO': {'lat': 10.7, 'lon': -74.9},
    'BOGOTA': {'lat': 4.6, 'lon': -74.1},
    'BOLIVAR': {'lat': 8.6, 'lon': -74.0},
    'BOYACA': {'lat': 5.6, 'lon': -73.0},
    'CALDAS': {'lat': 5.3, 'lon': -75.3},
    'CAQUETA': {'lat': 0.9, 'lon': -73.8},
    'CASANARE': {'lat': 5.3, 'lon': -71.3},
    'CAUCA': {'lat': 2.5, 'lon': -76.6},
    'CESAR': {'lat': 9.3, 'lon': -73.5},
    'CHOCO': {'lat': 5.7, 'lon': -76.6},
    'CORDOBA': {'lat': 8.7, 'lon': -75.6},
    'CUNDINAMARCA': {'lat': 5.0, 'lon': -74.0},
    'GUAINIA': {'lat': 2.6, 'lon': -68.5},
    'GUAVIARE': {'lat': 2.0, 'lon': -72.3},
    'HUILA': {'lat': 2.5, 'lon': -75.5},
    'LA GUAJIRA': {'lat': 11.5, 'lon': -72.5},
    'MAGDALENA': {'lat': 10.4, 'lon': -74.4},
    'META': {'lat': 3.4, 'lon': -73.0},
    'NARIÑO': {'lat': 1.2, 'lon': -77.3},
    'NORTE DE SANTANDER': {'lat': 7.9, 'lon': -72.5},
    'PUTUMAYO': {'lat': 0.4, 'lon': -76.6},
    'QUINDIO': {'lat': 4.5, 'lon': -75.7},
    'RISARALDA': {'lat': 5.3, 'lon': -75.9},
    'SAN ANDRES Y PROVIDENCIA': {'lat': 12.5, 'lon': -81.7},
    'SANTANDER': {'lat': 6.6, 'lon': -73.1},
    'SUCRE': {'lat': 9.0, 'lon': -75.4},
    'TOLIMA': {'lat': 4.0, 'lon': -75.2},
    'VALLE DEL CAUCA': {'lat': 3.8, 'lon': -76.5},
    'VAUPES': {'lat': 0.5, 'lon': -70.5},
    'VICHADA': {'lat': 4.4, 'lon': -69.3}
}

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
    def _create_department_map(df, title):
        """Create an interactive map visualization for department data"""
        if 'departamento' not in df.columns:
            return None

        # Prepare data
        dept_data = df.groupby('departamento').agg({
            'valor_del_contrato': ['sum', 'count']
        }).reset_index()
        dept_data.columns = ['departamento', 'valor_total', 'cantidad']
        
        # Normalize department names
        dept_data['departamento'] = dept_data['departamento'].str.upper()
        
        # Add coordinates
        dept_data['lat'] = dept_data['departamento'].map(lambda x: COLOMBIA_DEPARTMENTS.get(x, {}).get('lat', None))
        dept_data['lon'] = dept_data['departamento'].map(lambda x: COLOMBIA_DEPARTMENTS.get(x, {}).get('lon', None))
        
        # Create map
        fig = go.Figure()

        # Add scatter markers for departments
        fig.add_trace(go.Scattergeo(
            lon=dept_data['lon'],
            lat=dept_data['lat'],
            text=dept_data.apply(lambda x: f"{x['departamento']}<br>Valor: ${x['valor_total']:,.0f}<br>Cantidad: {x['cantidad']}", axis=1),
            mode='markers',
            marker=dict(
                size=dept_data['cantidad'],
                sizeref=2.*max(dept_data['cantidad'])/(40.**2),
                sizemin=4,
                color=dept_data['valor_total'],
                colorscale='Viridis',
                showscale=True,
                colorbar_title="Valor Total"
            ),
            name='Departamentos'
        ))

        # Update layout
        fig.update_layout(
            title=title,
            geo=dict(
                scope='south america',
                projection_scale=4,
                center=dict(lat=4.5709, lon=-74.2973),
                showland=True,
                showcountries=True,
                showsubunits=True,
                countrycolor='rgb(204, 204, 204)',
                subunitcolor='rgb(255, 255, 255)'
            )
        )

        return fig

    @staticmethod
    def _render_active_visualizations(df):
        """Render visualizations specific to active contracts"""
        if df.empty:
            return

        # Geographic Distribution
        if 'departamento' in df.columns:
            st.subheader("Distribución Geográfica de Contratos Activos")
            
            # Create and display the interactive map
            fig_map = AnalyticsComponent._create_department_map(
                df, 
                'Distribución Geográfica de Contratos Activos'
            )
            if fig_map:
                st.plotly_chart(fig_map, use_container_width=True)

            # Additional geographic analytics
            col1, col2 = st.columns(2)
            
            with col1:
                dept_values = df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
                fig_bar = px.bar(
                    dept_values,
                    x='departamento',
                    y='valor_del_contrato',
                    title='Valor Total por Departamento',
                    labels={'valor_del_contrato': 'Valor Total', 'departamento': 'Departamento'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                dept_counts = df['departamento'].value_counts()
                fig_pie = px.pie(
                    values=dept_counts.values,
                    names=dept_counts.index,
                    title='Distribución de Contratos por Departamento'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # Contract Value Distribution
        st.subheader("Distribución de Valores de Contratos Activos")
        fig_box = px.box(df, y='valor_del_contrato', points='all')
        st.plotly_chart(fig_box, use_container_width=True)

        # Time-based visualizations
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
    def _render_historical_visualizations(df):
        """Render visualizations specific to historical contracts"""
        if df.empty:
            return

        # Geographic Distribution
        if 'departamento' in df.columns:
            st.subheader("Distribución Geográfica de Contratos Históricos")
            
            # Create and display the interactive map
            fig_map = AnalyticsComponent._create_department_map(
                df, 
                'Distribución Geográfica de Contratos Históricos'
            )
            if fig_map:
                st.plotly_chart(fig_map, use_container_width=True)

            # Additional geographic analytics
            col1, col2 = st.columns(2)
            
            with col1:
                dept_values = df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
                fig_bar = px.bar(
                    dept_values,
                    x='departamento',
                    y='valor_del_contrato',
                    title='Valor Total Histórico por Departamento',
                    labels={'valor_del_contrato': 'Valor Total', 'departamento': 'Departamento'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                dept_counts = df['departamento'].value_counts()
                fig_pie = px.pie(
                    values=dept_counts.values,
                    names=dept_counts.index,
                    title='Distribución Histórica de Contratos por Departamento'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

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

        # Geographic Comparison
        if 'departamento' in active_df.columns and 'departamento' in historical_df.columns:
            st.subheader("Comparación Geográfica")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_map_active = AnalyticsComponent._create_department_map(
                    active_df,
                    'Distribución Geográfica - Contratos Activos'
                )
                if fig_map_active:
                    st.plotly_chart(fig_map_active, use_container_width=True)
            
            with col2:
                fig_map_hist = AnalyticsComponent._create_department_map(
                    historical_df,
                    'Distribución Geográfica - Contratos Históricos'
                )
                if fig_map_hist:
                    st.plotly_chart(fig_map_hist, use_container_width=True)

            # Comparative bar chart
            dept_active = active_df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
            dept_hist = historical_df.groupby('departamento')['valor_del_contrato'].sum().reset_index()
            
            # Merge data
            dept_comparison = pd.merge(
                dept_active,
                dept_hist,
                on='departamento',
                suffixes=('_activo', '_historico'),
                how='outer'
            ).fillna(0)
            
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
                yaxis_title='Valor Total (COP)',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)