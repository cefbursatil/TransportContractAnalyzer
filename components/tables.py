import streamlit as st
import pandas as pd
import logging
from utils.format_helpers import format_currency

logger = logging.getLogger(__name__)

class TableComponent:
    @staticmethod
    def render_table(df, title):
        """Render an enhanced table with advanced filtering and improved display"""
        try:
            st.subheader(title)
            
            if df.empty:
                st.warning("No se encontraron contratos.")
                return

            # Add filters
            st.subheader("Filtros")
            col1, col2, col3 = st.columns(3)
            
            # Department filter
            with col1:
                if 'departamento' in df.columns:
                    departments = ['Todos'] + sorted(df['departamento'].unique().tolist())
                    selected_dept = st.selectbox('Departamento', departments)
                    if selected_dept != 'Todos':
                        df = df[df['departamento'] == selected_dept]

            # Contract type filter
            with col2:
                if 'tipo_de_contrato' in df.columns:
                    contract_types = ['Todos'] + sorted(df['tipo_de_contrato'].unique().tolist())
                    selected_type = st.selectbox('Tipo de Contrato', contract_types)
                    if selected_type != 'Todos':
                        df = df[df['tipo_de_contrato'] == selected_type]

            # Value range filter
            with col3:
                if 'valor_del_contrato' in df.columns:
                    min_val = float(df['valor_del_contrato'].min())
                    max_val = float(df['valor_del_contrato'].max())
                    selected_range = st.slider(
                        'Rango de Valor (COP)',
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        format='%e'
                    )
                    df = df[
                        (df['valor_del_contrato'] >= selected_range[0]) &
                        (df['valor_del_contrato'] <= selected_range[1])
                    ]

            # Date range filter if date column exists
            if 'fecha_de_firma' in df.columns:
                st.subheader("Rango de Fechas")
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Fecha Inicial",
                        value=pd.to_datetime(df['fecha_de_firma']).min()
                    )
                with col2:
                    end_date = st.date_input(
                        "Fecha Final",
                        value=pd.to_datetime(df['fecha_de_firma']).max()
                    )
                df = df[
                    (pd.to_datetime(df['fecha_de_firma']).dt.date >= start_date) &
                    (pd.to_datetime(df['fecha_de_firma']).dt.date <= end_date)
                ]

            # Select relevant columns with better names
            column_mapping = {
                'nombre_entidad': 'Entidad',
                'departamento': 'Departamento',
                'tipo_de_contrato': 'Tipo de Contrato',
                'valor_del_contrato': 'Valor (COP)',
                'fecha_de_firma': 'Fecha de Firma',
                'descripcion_del_proceso': 'Descripción',
                'estado_contrato': 'Estado',
                'duracion': 'Duración (días)'
            }
            
            display_columns = [col for col in column_mapping.keys() if col in df.columns]
            display_df = df[display_columns].copy()
            display_df.columns = [column_mapping[col] for col in display_columns]

            # Format the data
            if 'Valor (COP)' in display_df.columns:
                display_df['Valor (COP)'] = display_df['Valor (COP)'].apply(format_currency)

            if 'Fecha de Firma' in display_df.columns:
                display_df['Fecha de Firma'] = pd.to_datetime(display_df['Fecha de Firma']).dt.strftime('%Y-%m-%d')

            # Truncate long descriptions
            if 'Descripción' in display_df.columns:
                display_df['Descripción'] = display_df['Descripción'].apply(
                    lambda x: x[:100] + '...' if isinstance(x, str) and len(x) > 100 else x
                )

            # Add contract URL if available
            if 'urlproceso' in df.columns:
                display_df['Acciones'] = df['urlproceso'].apply(
                    lambda x: f'<a href="{x}" target="_blank" style="text-decoration:none;">'
                            f'<button style="background-color: #4CAF50; color: white; '
                            f'padding: 5px 10px; border: none; border-radius: 4px; '
                            f'cursor: pointer;">Ver Contrato</button></a>'
                    if isinstance(x, str) else 'No disponible'
                )

            # Display table statistics
            st.markdown(f"**Total de Contratos:** {len(display_df)}")
            if 'Valor (COP)' in display_df.columns:
                total_value = df['valor_del_contrato'].sum()
                st.markdown(f"**Valor Total:** {format_currency(total_value)}")

            # Custom CSS for table styling
            st.markdown("""
                <style>
                    .dataframe {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    .dataframe th {
                        background-color: #4CAF50;
                        color: white;
                        padding: 12px;
                        text-align: left;
                    }
                    .dataframe td {
                        padding: 8px;
                        border-bottom: 1px solid #ddd;
                    }
                    .dataframe tr:nth-child(even) {
                        background-color: #f2f2f2;
                    }
                    .dataframe tr:hover {
                        background-color: #ddd;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Display the table with HTML
            st.markdown(
                display_df.to_html(
                    escape=False,
                    index=False,
                    classes=['dataframe']
                ),
                unsafe_allow_html=True
            )

            # Export functionality with multiple formats
            st.subheader("Exportar Datos")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exportar a CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("Exportar a Excel"):
                    output = df.to_excel(index=False)
                    st.download_button(
                        label="Descargar Excel",
                        data=output,
                        file_name=f"{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        except Exception as e:
            logger.error(f"Error rendering table: {str(e)}")
            st.error("Error al mostrar la tabla de contratos")
