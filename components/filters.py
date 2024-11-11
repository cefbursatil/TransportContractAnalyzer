import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class FilterComponent:
    @staticmethod
    def render_filters(df, contract_type='active'):
        """Render filter controls with specific filters based on contract type"""
        st.sidebar.header("Filtros")
        
        filters = {}
        
        # Date range filter
        if 'fecha_de_firma' in df.columns:
            st.sidebar.subheader("Rango de Fechas")
            min_date = df['fecha_de_firma'].min()
            max_date = df['fecha_de_firma'].max()
            
            if pd.notnull(min_date) and pd.notnull(max_date):
                date_range = st.sidebar.date_input(
                    "Seleccione rango de fechas",
                    value=(min_date.date(), max_date.date()),
                    min_value=min_date.date(),
                    max_value=max_date.date(),
                    key=f"date_range_{contract_type}"
                )
                if len(date_range) == 2:
                    filters['fecha_de_firma'] = date_range

        # Entity filter
        if 'nombre_entidad' in df.columns:
            entities = sorted(df['nombre_entidad'].unique())
            selected_entities = st.sidebar.multiselect(
                "Entidad",
                options=entities,
                default=[],
                key=f"entities_{contract_type}"
            )
            if selected_entities:
                filters['nombre_entidad'] = selected_entities

        # Department filter
        if 'departamento' in df.columns:
            departments = sorted(df['departamento'].unique())
            selected_departments = st.sidebar.multiselect(
                "Departamento",
                options=departments,
                default=[],
                key=f"departments_{contract_type}"
            )
            if selected_departments:
                filters['departamento'] = selected_departments

        # Contract type filter
        if 'tipo_de_contrato' in df.columns:
            contract_types = sorted(df['tipo_de_contrato'].unique())
            selected_types = st.sidebar.multiselect(
                "Tipo de Contrato",
                options=contract_types,
                default=[],
                key=f"contract_types_{contract_type}"
            )
            if selected_types:
                filters['tipo_de_contrato'] = selected_types

        # Value range filter
        if 'valor_del_contrato' in df.columns:
            st.sidebar.subheader("Rango de Valor")
            min_value = float(df['valor_del_contrato'].min())
            max_value = float(df['valor_del_contrato'].max())
            value_range = st.sidebar.slider(
                "Valor del Contrato",
                min_value=min_value,
                max_value=max_value,
                value=(min_value, max_value),
                key=f"value_range_{contract_type}"
            )
            if value_range != (min_value, max_value):
                filters['valor_del_contrato'] = value_range

        # Status filter (specific to contract type)
        if contract_type == 'active':
            if 'estado_contrato' in df.columns:
                status_options = sorted(df['estado_contrato'].unique())
                selected_status = st.sidebar.multiselect(
                    "Estado del Contrato",
                    options=status_options,
                    default=[],
                    key=f"status_{contract_type}"
                )
                if selected_status:
                    filters['estado_contrato'] = selected_status
        else:  # Historical contracts
            if 'fase' in df.columns:
                phase_options = sorted(df['fase'].unique())
                selected_phase = st.sidebar.multiselect(
                    "Fase del Proceso",
                    options=phase_options,
                    default=[],
                    key=f"phase_{contract_type}"
                )
                if selected_phase:
                    filters['fase'] = selected_phase

        # Add clear filters button
        if st.sidebar.button("Limpiar Filtros", key=f"clear_{contract_type}"):
            st.session_state[f"filters_{contract_type}"] = {}
            st.rerun()

        return filters
