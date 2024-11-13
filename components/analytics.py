import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import logging
import json
from utils.format_helpers import format_currency, format_percentage, format_large_number

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
        """Render enhanced analytics dashboards with interactive features"""
        try:
            if not isinstance(active_df, pd.DataFrame) or not isinstance(historical_df, pd.DataFrame):
                logger.error("Invalid input: DataFrames expected")
                st.error("Error: Invalid data format")
                return

            if active_df.empty and historical_df.empty:
                logger.warning("No data available for analysis")
                st.warning("No hay datos disponibles para análisis")
                return

            # Create tabs with enhanced analytics
            tab1, tab2, tab3, tab4 = st.tabs([
                "Vista General",
                "Análisis Geográfico",
                "Análisis Temporal",
                "Análisis Comparativo"
            ])

            with tab1:
                AnalyticsComponent._render_overview_tab(active_df, historical_df)

            with tab2:
                AnalyticsComponent._render_geographic_tab(active_df)

            with tab3:
                AnalyticsComponent._render_temporal_tab(active_df)

            with tab4:
                AnalyticsComponent._render_comparative_tab(active_df, historical_df)

        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error(f"Error al generar análisis: {str(e)}")

    @staticmethod
    def _render_overview_tab(active_df, historical_df):
        """Render overview analytics with key metrics"""
        st.header("Vista General del Sistema")

        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_active = active_df['valor_del_contrato'].sum()
            st.metric(
                "Valor Total Activo",
                format_currency(total_active),
                help="Suma total de contratos activos"
            )

        with col2:
            total_contracts = len(active_df)
            st.metric(
                "Contratos Activos",
                format_large_number(total_contracts),
                help="Número total de contratos activos"
            )

        with col3:
            avg_value = active_df['valor_del_contrato'].mean()
            st.metric(
                "Valor Promedio",
                format_currency(avg_value),
                help="Valor promedio por contrato"
            )

        with col4:
            if 'duracion' in active_df.columns:
                avg_duration = active_df['duracion'].mean()
                st.metric(
                    "Duración Promedio",
                    f"{avg_duration:.0f} días",
                    help="Duración promedio de contratos"
                )

        # Contract Type Distribution
        if 'tipo_de_contrato' in active_df.columns:
            st.subheader("Distribución por Tipo de Contrato")
            contract_types = active_df['tipo_de_contrato'].value_counts()
            fig = px.pie(
                values=contract_types.values,
                names=contract_types.index,
                title="Tipos de Contratos"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Value Distribution
        st.subheader("Distribución de Valores")
        fig = px.box(
            active_df,
            y='valor_del_contrato',
            title="Distribución de Valores de Contratos",
            points="all"
        )
        fig.update_layout(yaxis_title="Valor del Contrato (COP)")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _render_geographic_tab(df):
        """Render geographic analysis with interactive map"""
        st.header("Análisis Geográfico")

        if 'departamento' not in df.columns:
            st.warning("No hay datos geográficos disponibles")
            return

        # Create interactive map
        dept_data = df.groupby('departamento').agg({
            'valor_del_contrato': ['sum', 'count']
        }).reset_index()
        dept_data.columns = ['departamento', 'valor_total', 'cantidad']

        # Normalize department names and add coordinates
        dept_data['departamento'] = dept_data['departamento'].str.upper()
        dept_data['lat'] = dept_data['departamento'].map(lambda x: COLOMBIA_DEPARTMENTS.get(x, {}).get('lat', None))
        dept_data['lon'] = dept_data['departamento'].map(lambda x: COLOMBIA_DEPARTMENTS.get(x, {}).get('lon', None))

        # Create map
        fig = go.Figure()

        fig.add_trace(go.Scattergeo(
            lon=dept_data['lon'],
            lat=dept_data['lat'],
            text=dept_data.apply(lambda x: (
                f"{x['departamento']}<br>"
                f"Valor: {format_currency(x['valor_total'])}<br>"
                f"Cantidad: {x['cantidad']}"
            ), axis=1),
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

        fig.update_layout(
            title="Distribución Geográfica de Contratos",
            geo=dict(
                scope='south america',
                projection_scale=4,
                center=dict(lat=4.5709, lon=-74.2973),
                showland=True,
                showcountries=True,
                showsubunits=True,
                countrycolor='rgb(204, 204, 204)',
                subunitcolor='rgb(255, 255, 255)'
            ),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # Additional geographic insights
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Departamentos por Valor")
            top_value = dept_data.nlargest(10, 'valor_total')
            fig = px.bar(
                top_value,
                x='departamento',
                y='valor_total',
                title="Top 10 por Valor Total"
            )
            fig.update_layout(
                xaxis_title="Departamento",
                yaxis_title="Valor Total (COP)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Top 10 Departamentos por Cantidad")
            top_count = dept_data.nlargest(10, 'cantidad')
            fig = px.bar(
                top_count,
                x='departamento',
                y='cantidad',
                title="Top 10 por Cantidad de Contratos"
            )
            fig.update_layout(
                xaxis_title="Departamento",
                yaxis_title="Cantidad de Contratos"
            )
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _render_temporal_tab(df):
        """Render temporal analysis with interactive time series"""
        st.header("Análisis Temporal")

        if 'fecha_de_firma' not in df.columns:
            st.warning("No hay datos temporales disponibles")
            return

        # Prepare time series data
        df['fecha'] = pd.to_datetime(df['fecha_de_firma'])
        df['mes'] = df['fecha'].dt.to_period('M')
        monthly_data = df.groupby('mes').agg({
            'valor_del_contrato': ['sum', 'count']
        }).reset_index()
        monthly_data['mes'] = monthly_data['mes'].astype(str)

        # Create interactive time series
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=monthly_data['mes'],
            y=monthly_data['valor_del_contrato']['sum'],
            name='Valor Total',
            yaxis='y'
        ))

        fig.add_trace(go.Scatter(
            x=monthly_data['mes'],
            y=monthly_data['valor_del_contrato']['count'],
            name='Cantidad',
            yaxis='y2',
            line=dict(color='red')
        ))

        fig.update_layout(
            title="Evolución Temporal de Contratos",
            xaxis_title="Mes",
            yaxis=dict(
                title="Valor Total (COP)",
                titlefont=dict(color="#1f77b4"),
                tickfont=dict(color="#1f77b4")
            ),
            yaxis2=dict(
                title="Cantidad de Contratos",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
                overlaying="y",
                side="right"
            ),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _render_comparative_tab(active_df, historical_df):
        """Render comparative analysis between active and historical data"""
        st.header("Análisis Comparativo")

        if active_df.empty or historical_df.empty:
            st.warning("No hay suficientes datos para análisis comparativo")
            return

        # Compare key metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            active_avg = active_df['valor_del_contrato'].mean()
            hist_avg = historical_df['valor_del_contrato'].mean()
            percent_diff = ((active_avg - hist_avg) / hist_avg * 100) if hist_avg != 0 else 0
            st.metric(
                "Diferencia en Valor Promedio",
                format_currency(active_avg),
                f"{format_percentage(percent_diff)} vs histórico"
            )

        with col2:
            active_count = len(active_df)
            hist_count = len(historical_df)
            count_diff = ((active_count - hist_count) / hist_count * 100) if hist_count != 0 else 0
            st.metric(
                "Diferencia en Cantidad",
                str(active_count),
                f"{format_percentage(count_diff)} vs histórico"
            )

        with col3:
            if 'duracion' in active_df.columns and 'duracion' in historical_df.columns:
                active_duration = active_df['duracion'].mean()
                hist_duration = historical_df['duracion'].mean()
                duration_diff = ((active_duration - hist_duration) / hist_duration * 100) if hist_duration != 0 else 0
                st.metric(
                    "Diferencia en Duración",
                    f"{active_duration:.0f} días",
                    f"{format_percentage(duration_diff)} vs histórico"
                )

        # Value distribution comparison
        st.subheader("Comparación de Distribución de Valores")
        fig = go.Figure()

        fig.add_trace(go.Box(
            y=active_df['valor_del_contrato'],
            name='Activos',
            boxpoints='outliers'
        ))

        fig.add_trace(go.Box(
            y=historical_df['valor_del_contrato'],
            name='Históricos',
            boxpoints='outliers'
        ))

        fig.update_layout(
            title="Distribución de Valores: Activos vs Históricos",
            yaxis_title="Valor del Contrato (COP)",
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)