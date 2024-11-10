import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class FilterComponent:
    @staticmethod
    def render_filters(df):
        """Render filter controls"""
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
                    max_value=max_date.date()
                )
                if len(date_range) == 2:
                    filters['fecha_de_firma'] = date_range

        # Entity filter
        if 'nombre_entidad' in df.columns:
            entities = df['nombre_entidad'].unique()
            selected_entities = st.sidebar.multiselect(
                "Entidad",
                options=entities,
                default=[]
            )
            if selected_entities:
                filters['nombre_entidad'] = selected_entities

        # Department filter
        if 'departamento' in df.columns:
            departments = df['departamento'].unique()
            selected_departments = st.sidebar.multiselect(
                "Departamento",
                options=departments,
                default=[]
            )
            if selected_departments:
                filters['departamento'] = selected_departments

        # Contract type filter
        if 'tipo_de_contrato' in df.columns:
            contract_types = df['tipo_de_contrato'].unique()
            selected_types = st.sidebar.multiselect(
                "Tipo de Contrato",
                options=contract_types,
                default=[]
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
                value=(min_value, max_value)
            )
            if value_range != (min_value, max_value):
                filters['valor_del_contrato'] = value_range

        return filters
