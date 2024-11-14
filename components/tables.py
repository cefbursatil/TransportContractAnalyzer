import streamlit as st
import pandas as pd
import logging
from utils.format_helpers import format_currency

logger = logging.getLogger(__name__)

class TableComponent:
    @staticmethod
    def render_table(df, title):
        """Render an enhanced table with advanced filtering and sorting"""
        try:
            st.subheader(title)
            
            if df.empty:
                st.warning("No se encontraron contratos.")
                return

            # Add sort state to session state if not exists
            sort_key = f"{title.lower()}_sort"
            if sort_key not in st.session_state:
                st.session_state[sort_key] = {
                    'column': 'fecha_de_recepcion_de' if title == "Contratos Activos" else None,
                    'direction': False if title == "Contratos Activos" else True  # False for descending
                }

            # Add filters
            st.subheader("Filtros")
            
            # Create filter columns based on title
            if title == "Contratos Históricos":
                col1, col2, col3 = st.columns(3)
                col4, col5 = st.columns(2)
                
                # Entity filter
                with col1:
                    if 'nombre_entidad' in df.columns:
                        entities = ['Todos'] + sorted(df['nombre_entidad'].unique().tolist())
                        selected_entity = st.selectbox(
                            'Entidad',
                            entities,
                            key=f"{title.lower()}_nombre_entidad_filter"
                        )
                        if selected_entity != 'Todos':
                            df = df[df['nombre_entidad'] == selected_entity]

                # Contract type filter
                with col2:
                    if 'tipo_de_contrato' in df.columns:
                        contract_types = ['Todos'] + sorted(df['tipo_de_contrato'].unique().tolist())
                        selected_type = st.selectbox(
                            'Tipo de Contrato',
                            contract_types,
                            key=f"{title.lower()}_tipo_contrato_filter"
                        )
                        if selected_type != 'Todos':
                            df = df[df['tipo_de_contrato'] == selected_type]

                # Provider filter
                with col3:
                    if 'proveedor_adjudicado' in df.columns:
                        providers = ['Todos'] + sorted(df['proveedor_adjudicado'].unique().tolist())
                        selected_provider = st.selectbox(
                            'Proveedor',
                            providers,
                            key=f"{title.lower()}_proveedor_filter"
                        )
                        if selected_provider != 'Todos':
                            df = df[df['proveedor_adjudicado'] == selected_provider]

                # Value range filter
                with col4:
                    if 'valor_del_contrato' in df.columns:
                        min_val = float(df['valor_del_contrato'].min())
                        max_val = float(df['valor_del_contrato'].max())
                        selected_range = st.slider(
                            'Rango de Valor (COP)',
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            format='%e',
                            key=f"{title.lower()}_valor_filter"
                        )
                        df = df[
                            (df['valor_del_contrato'] >= selected_range[0]) &
                            (df['valor_del_contrato'] <= selected_range[1])
                        ]

                # Date range filter
                with col5:
                    if 'fecha_de_firma' in df.columns:
                        start_date = st.date_input(
                            "Fecha Inicial",
                            value=pd.to_datetime(df['fecha_de_firma']).min(),
                            key=f"{title.lower()}_fecha_inicio_filter"
                        )
                        end_date = st.date_input(
                            "Fecha Final",
                            value=pd.to_datetime(df['fecha_de_firma']).max(),
                            key=f"{title.lower()}_fecha_fin_filter"
                        )
                        df = df[
                            (pd.to_datetime(df['fecha_de_firma']).dt.date >= start_date) &
                            (pd.to_datetime(df['fecha_de_firma']).dt.date <= end_date)
                        ]
            else:
                # Default filters for active contracts tab
                col1, col2, col3, col4 = st.columns(4)
                
                # Department filter
                with col1:
                    if 'departamento' in df.columns:
                        departments = ['Todos'] + sorted(df['departamento'].unique().tolist())
                        selected_dept = st.selectbox(
                            'Departamento',
                            departments,
                            key=f"{title.lower()}_departamento_filter"
                        )
                        if selected_dept != 'Todos':
                            df = df[df['departamento'] == selected_dept]

                # Contract type filter
                with col2:
                    if 'tipo_de_contrato' in df.columns:
                        contract_types = ['Todos'] + sorted(df['tipo_de_contrato'].unique().tolist())
                        selected_type = st.selectbox(
                            'Tipo de Contrato',
                            contract_types,
                            key=f"{title.lower()}_tipo_contrato_filter"
                        )
                        if selected_type != 'Todos':
                            df = df[df['tipo_de_contrato'] == selected_type]

                # Value range filter
                with col3:
                    if 'precio_base' in df.columns:
                        min_val = float(df['precio_base'].min())
                        max_val = float(df['precio_base'].max())
                        selected_range = st.slider(
                            'Rango de Valor (COP)',
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            format='%e',
                            key=f"{title.lower()}_valor_filter"
                        )
                        df = df[
                            (df['precio_base'] >= selected_range[0]) &
                            (df['precio_base'] <= selected_range[1])
                        ]
                # Add the new filter after the existing ones
                with col4:
                    if 'modalidad_de_contratacion' in filtered_active_df.columns:
                        unique_modes = filtered_active_df['modalidad_de_contratacion'].dropna().unique()
                        contract_modes = ['Todos'] + sorted(unique_modes.tolist())
                        selected_mode = st.selectbox(
                            'Modo Contratación',
                            contract_modes,
                            key="active_mode_filter"
                        )
                        if selected_mode != 'Todos':
                            filtered_active_df = filtered_active_df[
                                filtered_active_df['modalidad_de_contratacion'] == selected_mode
                            ]

            # Select relevant columns with better names
            column_mapping = {
                'nombre_entidad': 'Entidad',
                'departamento': 'Departamento',
                'tipo_de_contrato': 'Tipo de Contrato',
                'precio_base': 'Valor (COP)',
                'fecha_de_recepcion_de': 'Fecha Presentación Oferta',
                'descripci_on_del_procedimiento': 'Descripción',
                'valor_del_contrato': 'Valor (COP)',
                'fecha_de_firma': 'Fecha de Firma',
                'descripcion_del_proceso': 'Descripción',
                'estado_contrato': 'Estado',
                'duracion': 'Duración (días)',
                'proveedor_adjudicado': 'Proveedor',
                'documento_proveedor': 'Documento Proveedor',
                'dias_adicionados': 'Días Adicionados',
            }
            
            # Select columns based on tab type
            if title == "Contratos Históricos":
                display_columns = [
                    'nombre_entidad', 'departamento', 'tipo_de_contrato',
                    'valor_del_contrato', 'fecha_de_firma', 'descripcion_del_proceso',
                    'estado_contrato', 'proveedor_adjudicado', 'documento_proveedor',
                    'dias_adicionados'
                ]
            else:
                display_columns = [
                    'nombre_entidad', 'departamento', 'tipo_de_contrato',
                    'precio_base', 'fecha_de_recepcion_de'
                ]
            
            # Filter only existing columns
            display_columns = [col for col in display_columns if col in df.columns]
            display_df = df[display_columns].copy()

            # Apply sorting if selected
            if st.session_state[sort_key]['column']:
                col = st.session_state[sort_key]['column']
                ascending = st.session_state[sort_key]['direction']
                display_df = display_df.sort_values(by=col, ascending=ascending)

            # Create sorting buttons for each column
            st.markdown("### Ordenar por:")
            sort_cols = st.columns(len(display_columns))
            
            for idx, (col, mapped_name) in enumerate(zip(display_columns, [column_mapping[col] for col in display_columns])):
                with sort_cols[idx]:
                    # Add sort button with arrow indicator
                    current_sort = st.session_state[sort_key]
                    is_sorted = current_sort['column'] == col
                    arrow = "↑" if is_sorted and current_sort['direction'] else "↓" if is_sorted else ""
                    if st.button(f"{mapped_name} {arrow}", key=f"sort_{title}_{col}"):
                        if current_sort['column'] == col:
                            # Toggle direction if same column
                            current_sort['direction'] = not current_sort['direction']
                        else:
                            # New column, set to ascending
                            current_sort['column'] = col
                            current_sort['direction'] = True

            # Rename columns for display
            display_df.columns = [column_mapping[col] for col in display_columns]

            # Format the data
            if 'Valor (COP)' in display_df.columns:
                display_df['Valor (COP)'] = display_df['Valor (COP)'].apply(format_currency)

            if 'Fecha de Firma' in display_df.columns:
                display_df['Fecha de Firma'] = pd.to_datetime(display_df['Fecha de Firma']).dt.strftime('%Y-%m-%d')

            if 'Fecha Presentación Oferta' in display_df.columns:
                display_df['Fecha Presentación Oferta'] = pd.to_datetime(display_df['Fecha Presentación Oferta']).dt.strftime('%Y-%m-%d')

            # Format días adicionados as integer
            if 'Días Adicionados' in display_df.columns:
                display_df['Días Adicionados'] = display_df['Días Adicionados'].fillna(0).astype(int)

            # Truncate long descriptions
            if 'Descripción' in display_df.columns:
                display_df['Descripción'] = display_df['Descripción'].apply(
                    lambda x: x[:200] + '...' if isinstance(x, str) and len(x) > 200 else x
                )

            # Display table statistics
            st.markdown(f"**Total de Contratos:** {len(display_df)}")
            if 'Valor (COP)' in display_df.columns:
                total_value = df['precio_base' if title == "Contratos Activos" else 'valor_del_contrato'].sum()
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
                        cursor: pointer;
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
                    .stButton button {
                        width: 100%;
                        padding: 5px;
                        font-size: 0.8em;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Display the table with HTML
            st.dataframe(display_df, use_container_width=True)

            # Export functionality with multiple formats
            st.subheader("Exportar Datos")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exportar a CSV", key=f"{title.lower()}_csv_button"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key=f"{title.lower()}_csv_download"
                    )
            
            with col2:
                if st.button("Exportar a Excel", key=f"{title.lower()}_excel_button"):
                    output = df.to_excel(index=False)
                    st.download_button(
                        label="Descargar Excel",
                        data=output,
                        file_name=f"{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"{title.lower()}_excel_download"
                    )

        except Exception as e:
            logger.error(f"Error rendering table: {str(e)}")
            st.error("Error al mostrar la tabla de contratos")
