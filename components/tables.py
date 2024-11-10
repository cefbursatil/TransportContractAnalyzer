import streamlit as st
import pandas as pd

class TableComponent:
    @staticmethod
    def render_table(df, title):
        """Render an interactive table with the contract data"""
        st.subheader(title)
        
        if df.empty:
            st.warning("No se encontraron contratos que cumplan con los criterios seleccionados.")
            return

        # Select columns to display
        display_columns = [
            'nombre_entidad',
            'departamento',
            'tipo_de_contrato',
            'valor_del_contrato',
            'fecha_de_firma',
            'descripcion_del_proceso',
            'estado_contrato'
        ]
        
        display_columns = [col for col in display_columns if col in df.columns]
        
        # Format the dataframe for display
        display_df = df[display_columns].copy()
        
        # Format currency values
        if 'valor_del_contrato' in display_df.columns:
            display_df['valor_del_contrato'] = display_df['valor_del_contrato'].apply(
                lambda x: f"${x:,.0f}" if pd.notnull(x) else "No especificado"
            )
            
        # Format dates
        date_columns = [col for col in display_columns if 'fecha' in col.lower()]
        for col in date_columns:
            display_df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
            
        # Add URL column if available
        if 'urlproceso' in df.columns:
            display_df['Ver Contrato'] = df['urlproceso'].apply(
                lambda x: f'[Ver]({x})' if isinstance(x, str) else 'No disponible'
            )
            
        # Display the table
        st.dataframe(
            display_df,
            height=400,
            use_container_width=True
        )
        
        # Export button
        if st.button(f"Exportar {title} a CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"{title.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )