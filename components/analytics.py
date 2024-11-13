import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import logging

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
                AnalyticsComponent._render_active_contracts(active_df)

            with tab2:
                st.header("Dashboard de Contratos Históricos")
                AnalyticsComponent._render_historical_contracts(historical_df)

            with tab3:
                st.header("Análisis Comparativo")
                AnalyticsComponent._render_comparative_analysis(active_df, historical_df)

        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error("Error al generar análisis")

    @staticmethod
    def _create_geographic_visualization(df, title):
        """Create geographic distribution visualization"""
        try:
            if 'departamento' not in df.columns:
                logger.warning("Column 'departamento' not found in DataFrame")
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

            # Create map visualization
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

        except Exception as e:
            logger.error(f"Error creating geographic visualization: {str(e)}")
            return None

    @staticmethod
    def _render_active_contracts(df):
        """Render active contracts analysis"""
        try:
            # Add filters
            st.subheader("Filtros")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'fecha_de_publicacion_del' in df.columns:
                    min_date = pd.to_datetime(df['fecha_de_publicacion_del']).min()
                    max_date = pd.to_datetime(df['fecha_de_publicacion_del']).max()
                    date_range = st.date_input(
                        "Rango de Fecha de Publicación",
                        value=(min_date, max_date),
                        key="active_date_range"
                    )

                if 'tipo_de_contrato' in df.columns:
                    contract_types = df['tipo_de_contrato'].unique()
                    selected_types = st.multiselect(
                        "Tipo de Contrato",
                        options=contract_types,
                        key="active_contract_types"
                    )

            with col2:
                if 'valor_del_contrato' in df.columns:
                    min_val = float(df['valor_del_contrato'].min())
                    max_val = float(df['valor_del_contrato'].max())
                    value_range = st.slider(
                        "Rango de Valor del Contrato",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        key="active_value_range"
                    )

                if 'nombre_entidad' in df.columns:
                    entities = df['nombre_entidad'].unique()
                    selected_entities = st.multiselect(
                        "Nombre de Entidad",
                        options=entities,
                        key="active_entities"
                    )

            # Apply filters
            filtered_df = df.copy()
            if 'fecha_de_publicacion_del' in df.columns and len(date_range) == 2:
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['fecha_de_publicacion_del']).dt.date >= date_range[0]) &
                    (pd.to_datetime(filtered_df['fecha_de_publicacion_del']).dt.date <= date_range[1])
                ]

            if selected_types:
                filtered_df = filtered_df[filtered_df['tipo_de_contrato'].isin(selected_types)]

            if 'valor_del_contrato' in df.columns:
                filtered_df = filtered_df[
                    (filtered_df['valor_del_contrato'] >= value_range[0]) &
                    (filtered_df['valor_del_contrato'] <= value_range[1])
                ]

            if selected_entities:
                filtered_df = filtered_df[filtered_df['nombre_entidad'].isin(selected_entities)]

            # Display visualizations
            st.subheader("Distribución Geográfica")
            fig_map = AnalyticsComponent._create_geographic_visualization(
                filtered_df,
                'Distribución Regional de Contratos Activos'
            )
            if fig_map:
                st.plotly_chart(fig_map, use_container_width=True)

            # Top 10 entities by contract value
            st.subheader("Top 10 Entidades por Valor de Contrato")
            top_entities = filtered_df.groupby('nombre_entidad')['valor_del_contrato'].sum().sort_values(ascending=False).head(10)
            fig_top = px.bar(
                x=top_entities.index,
                y=top_entities.values,
                title="Top 10 Entidades por Valor Total de Contratos",
                labels={'x': 'Entidad', 'y': 'Valor Total'}
            )
            fig_top.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_top, use_container_width=True)

        except Exception as e:
            logger.error(f"Error rendering active contracts: {str(e)}")
            st.error("Error al mostrar análisis de contratos activos")

    @staticmethod
    def _render_historical_contracts(df):
        """Render historical contracts analysis"""
        try:
            # Add filters
            st.subheader("Filtros")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'fecha_de_firma' in df.columns:
                    min_date = pd.to_datetime(df['fecha_de_firma']).min()
                    max_date = pd.to_datetime(df['fecha_de_firma']).max()
                    date_range = st.date_input(
                        "Rango de Fecha de Firma",
                        value=(min_date, max_date),
                        key="hist_date_range"
                    )

                if 'tipo_de_contrato' in df.columns:
                    contract_types = df['tipo_de_contrato'].unique()
                    selected_types = st.multiselect(
                        "Tipo de Contrato",
                        options=contract_types,
                        key="hist_contract_types"
                    )

            with col2:
                if 'valor_del_contrato' in df.columns:
                    min_val = float(df['valor_del_contrato'].min())
                    max_val = float(df['valor_del_contrato'].max())
                    value_range = st.slider(
                        "Rango de Valor del Contrato",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        key="hist_value_range"
                    )

                if 'nombre_entidad' in df.columns:
                    entities = df['nombre_entidad'].unique()
                    selected_entities = st.multiselect(
                        "Nombre de Entidad",
                        options=entities,
                        key="hist_entities"
                    )

            with col3:
                if 'proveedor_adjudicado' in df.columns:
                    providers = df['proveedor_adjudicado'].unique()
                    selected_providers = st.multiselect(
                        "Proveedor Adjudicado",
                        options=providers,
                        key="hist_providers"
                    )

            # Apply filters
            filtered_df = df.copy()
            if 'fecha_de_firma' in df.columns and len(date_range) == 2:
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['fecha_de_firma']).dt.date >= date_range[0]) &
                    (pd.to_datetime(filtered_df['fecha_de_firma']).dt.date <= date_range[1])
                ]

            if selected_types:
                filtered_df = filtered_df[filtered_df['tipo_de_contrato'].isin(selected_types)]

            if 'valor_del_contrato' in df.columns:
                filtered_df = filtered_df[
                    (filtered_df['valor_del_contrato'] >= value_range[0]) &
                    (filtered_df['valor_del_contrato'] <= value_range[1])
                ]

            if selected_entities:
                filtered_df = filtered_df[filtered_df['nombre_entidad'].isin(selected_entities)]

            if selected_providers:
                filtered_df = filtered_df[filtered_df['proveedor_adjudicado'].isin(selected_providers)]

            # Display visualizations
            st.subheader("Distribución Geográfica")
            fig_map = AnalyticsComponent._create_geographic_visualization(
                filtered_df,
                'Distribución Regional de Contratos Históricos'
            )
            if fig_map:
                st.plotly_chart(fig_map, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                # Top 10 entities by contract value
                st.subheader("Top 10 Entidades")
                top_entities = filtered_df.groupby('nombre_entidad')['valor_del_contrato'].sum().sort_values(ascending=False).head(10)
                fig_top = px.bar(
                    x=top_entities.index,
                    y=top_entities.values,
                    title="Top 10 Entidades por Valor Total",
                    labels={'x': 'Entidad', 'y': 'Valor Total'}
                )
                fig_top.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_top, use_container_width=True)

            with col2:
                # Top providers by contract value
                if 'proveedor_adjudicado' in filtered_df.columns:
                    st.subheader("Top Proveedores")
                    top_providers = filtered_df.groupby('proveedor_adjudicado')['valor_del_contrato'].sum().sort_values(ascending=False).head(10)
                    fig_prov = px.bar(
                        x=top_providers.index,
                        y=top_providers.values,
                        title="Top 10 Proveedores por Valor Total",
                        labels={'x': 'Proveedor', 'y': 'Valor Total'}
                    )
                    fig_prov.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_prov, use_container_width=True)

        except Exception as e:
            logger.error(f"Error rendering historical contracts: {str(e)}")
            st.error("Error al mostrar análisis de contratos históricos")

    @staticmethod
    def _render_comparative_analysis(active_df, historical_df):
        """Render comparative analysis between active and historical contracts"""
        try:
            st.subheader("Comparación de Valor por Entidad")

            # Get top entities by contract value for both datasets
            active_top = active_df.groupby('nombre_entidad')['valor_del_contrato'].sum()
            hist_top = historical_df.groupby('nombre_entidad')['valor_del_contrato'].sum()

            # Combine and get top 10 entities overall
            combined_top = pd.concat([active_top, hist_top]).groupby('nombre_entidad').sum()
            top_entities = combined_top.sort_values(ascending=False).head(10).index

            # Prepare data for comparison
            compare_data = []
            for entity in top_entities:
                active_value = active_top.get(entity, 0)
                hist_value = hist_top.get(entity, 0)
                compare_data.append({
                    'Entidad': entity,
                    'Valor Contratos Activos': active_value,
                    'Valor Contratos Históricos': hist_value
                })

            df_compare = pd.DataFrame(compare_data)

            # Create comparison chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Contratos Activos',
                x=df_compare['Entidad'],
                y=df_compare['Valor Contratos Activos'],
                marker_color='blue'
            ))
            fig.add_trace(go.Bar(
                name='Contratos Históricos',
                x=df_compare['Entidad'],
                y=df_compare['Valor Contratos Históricos'],
                marker_color='red'
            ))

            fig.update_layout(
                title='Comparación de Valores por Entidad (Top 10)',
                xaxis_tickangle=-45,
                barmode='group',
                xaxis_title='Entidad',
                yaxis_title='Valor Total'
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.error(f"Error rendering comparative analysis: {str(e)}")
            st.error("Error al mostrar análisis comparativo")
