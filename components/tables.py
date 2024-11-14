import streamlit as st
import pandas as pd
import logging
from utils.format_helpers import format_currency
import io

logger = logging.getLogger(__name__)

class TableComponent:
    @staticmethod
    def render_table(df, title):
        """Render an enhanced table with advanced filtering and sorting"""
        try:
            if df is None or df.empty:
                st.warning("No se encontraron contratos.")
                return

            st.subheader(title)
            
            # Create filter columns
            col1, col2, col3 = st.columns(3)
            
            filtered_df = df.copy()
            
            # Entity filter
            with col1:
                if 'nombre_entidad' in filtered_df.columns:
                    entities = ['Todos'] + sorted(filtered_df['nombre_entidad'].dropna().unique().tolist())
                    selected_entity = st.selectbox(
                        'Entidad',
                        entities,
                        key=f"{title.lower()}_entity_filter"
                    )
                    if selected_entity != 'Todos':
                        filtered_df = filtered_df[filtered_df['nombre_entidad'] == selected_entity]

            # Contract type filter
            with col2:
                if 'tipo_de_contrato' in filtered_df.columns:
                    contract_types = ['Todos'] + sorted(filtered_df['tipo_de_contrato'].dropna().unique().tolist())
                    selected_type = st.selectbox(
                        'Tipo de Contrato',
                        contract_types,
                        key=f"{title.lower()}_type_filter"
                    )
                    if selected_type != 'Todos':
                        filtered_df = filtered_df[filtered_df['tipo_de_contrato'] == selected_type]

            # Value range filter
            with col3:
                if 'valor_del_contrato' in filtered_df.columns:
                    min_val = float(filtered_df['valor_del_contrato'].min())
                    max_val = float(filtered_df['valor_del_contrato'].max())
                    value_range = st.slider(
                        'Rango de Valor (COP)',
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        format='%e',
                        key=f"{title.lower()}_value_filter"
                    )
                    filtered_df = filtered_df[
                        (filtered_df['valor_del_contrato'] >= value_range[0]) &
                        (filtered_df['valor_del_contrato'] <= value_range[1])
                    ]

            # Select and prepare display columns
            display_columns = [
                'nombre_entidad',
                'tipo_de_contrato',
                'valor_del_contrato',
                'fecha_de_firma',
                'descripcion_del_proceso',
                'estado_contrato'
            ]

            # Filter only existing columns
            display_columns = [col for col in display_columns if col in filtered_df.columns]
            display_df = filtered_df[display_columns].copy()

            # Format data for display while keeping original values for sorting
            sort_df = display_df.copy()
            
            if 'valor_del_contrato' in display_df.columns:
                display_df['valor_del_contrato'] = display_df['valor_del_contrato'].apply(format_currency)

            if 'fecha_de_firma' in display_df.columns:
                display_df['fecha_de_firma'] = pd.to_datetime(display_df['fecha_de_firma']).dt.strftime('%Y-%m-%d')

            if 'descripcion_del_proceso' in display_df.columns:
                display_df['descripcion_del_proceso'] = display_df['descripcion_del_proceso'].apply(
                    lambda x: x[:100] + '...' if isinstance(x, str) and len(x) > 100 else x
                )

            # Column names mapping for display
            column_mapping = {
                'nombre_entidad': 'Entidad',
                'tipo_de_contrato': 'Tipo de Contrato',
                'valor_del_contrato': 'Valor (COP)',
                'fecha_de_firma': 'Fecha de Firma',
                'descripcion_del_proceso': 'Descripción',
                'estado_contrato': 'Estado'
            }

            # Display the table with sorting functionality
            st.dataframe(
                data=display_df.rename(columns=column_mapping),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Entidad": st.column_config.TextColumn(
                        "Entidad",
                        width="medium",
                        help="Nombre de la entidad contratante",
                        sortable=True
                    ),
                    "Tipo de Contrato": st.column_config.TextColumn(
                        "Tipo de Contrato",
                        width="medium",
                        sortable=True
                    ),
                    "Valor (COP)": st.column_config.NumberColumn(
                        "Valor (COP)",
                        width="medium",
                        help="Valor del contrato en pesos colombianos",
                        format="$%d",
                        sortable=True
                    ),
                    "Fecha de Firma": st.column_config.DateColumn(
                        "Fecha de Firma",
                        format="YYYY-MM-DD",
                        width="small",
                        sortable=True
                    ),
                    "Descripción": st.column_config.TextColumn(
                        "Descripción",
                        width="large",
                        sortable=True
                    ),
                    "Estado": st.column_config.TextColumn(
                        "Estado",
                        width="small",
                        sortable=True
                    )
                }
            )

            # Display statistics
            st.markdown(f"**Total de Contratos:** {len(display_df)}")
            if 'valor_del_contrato' in filtered_df.columns:
                total_value = filtered_df['valor_del_contrato'].sum()
                st.markdown(f"**Valor Total:** {format_currency(total_value)}")

            # Export functionality
            st.subheader("Exportar Datos")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exportar a CSV", key=f"{title.lower()}_csv_button"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"contratos_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("Exportar a Excel", key=f"{title.lower()}_excel_button"):
                    buffer = io.BytesIO()
                    filtered_df.to_excel(buffer, index=False, engine='openpyxl')
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Descargar Excel",
                        data=buffer,
                        file_name=f"contratos_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        except Exception as e:
            logger.error(f"Error rendering table: {str(e)}")
            st.error("Error al mostrar la tabla de contratos")
