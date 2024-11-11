import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class FilterComponent:
    @staticmethod
    def render_filters(df, contract_type='active'):
        """Render filter controls with specific filters based on contract type"""
        st.sidebar.header("Filtros")
        
        # Clear other contract type filters
        other_type = 'historical' if contract_type == 'active' else 'active'
        if f'filters_{other_type}' in st.session_state:
            st.session_state[f'filters_{other_type}'] = {}
        
        # Initialize session state for filters if not exists
        if f'filters_{contract_type}' not in st.session_state:
            st.session_state[f'filters_{contract_type}'] = {}
        
        filters = {}
        
        # Date range filter
        if 'fecha_de_firma' in df.columns:
            st.sidebar.subheader("Rango de Fechas")
            min_date = pd.to_datetime(df['fecha_de_firma'].min())
            max_date = pd.to_datetime(df['fecha_de_firma'].max())
            
            if pd.notnull(min_date) and pd.notnull(max_date):
                date_range = st.sidebar.date_input(
                    "Seleccione rango de fechas",
                    value=(min_date.date(), max_date.date()),
                    min_value=min_date.date(),
                    max_value=max_date.date(),
                    key=f"date_range_{contract_type}"
                )
                if isinstance(date_range, tuple) and len(date_range) == 2:
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

        # Contract type specific filters
        if contract_type == 'active':
            # Active contracts specific filters
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
        else:
            # Historical contracts specific filters
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

            if 'proveedores_invitados' in df.columns:
                min_providers = int(df['proveedores_invitados'].min())
                max_providers = int(df['proveedores_invitados'].max())
                providers_range = st.sidebar.slider(
                    "Proveedores Invitados",
                    min_value=min_providers,
                    max_value=max_providers,
                    value=(min_providers, max_providers),
                    key=f"providers_{contract_type}"
                )
                if providers_range != (min_providers, max_providers):
                    filters['proveedores_invitados'] = providers_range

            if 'respuestas_al_procedimiento' in df.columns:
                min_responses = int(df['respuestas_al_procedimiento'].min())
                max_responses = int(df['respuestas_al_procedimiento'].max())
                responses_range = st.sidebar.slider(
                    "Respuestas al Procedimiento",
                    min_value=min_responses,
                    max_value=max_responses,
                    value=(min_responses, max_responses),
                    key=f"responses_{contract_type}"
                )
                if responses_range != (min_responses, max_responses):
                    filters['respuestas_al_procedimiento'] = responses_range

            if 'modalidad_de_contratacion' in df.columns:
                modalities = sorted(df['modalidad_de_contratacion'].unique())
                selected_modalities = st.sidebar.multiselect(
                    "Modalidad de Contratación",
                    options=modalities,
                    default=[],
                    key=f"modalities_{contract_type}"
                )
                if selected_modalities:
                    filters['modalidad_de_contratacion'] = selected_modalities

        # Add clear filters button
        if st.sidebar.button("Limpiar Filtros", key=f"clear_{contract_type}"):
            # Clear the specific contract type filters in session state
            st.session_state[f'filters_{contract_type}'] = {}
            st.rerun()

        # Store filters in session state
        st.session_state[f'filters_{contract_type}'] = filters
        return filters
