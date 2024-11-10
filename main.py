import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.scheduler import DataUpdateScheduler
from components.filters import FilterComponent
from components.tables import TableComponent
from components.analytics import AnalyticsComponent
import os

# Page config
st.set_page_config(
    page_title="Sistema de Gestión de Contratos de Transporte",
    page_icon="🚦",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

class ContractManagementSystem:
    def __init__(self):
        self.scheduler = DataUpdateScheduler()
        self.data_processor = DataProcessor()
        
        # Initialize session state
        if 'last_update' not in st.session_state:
            st.session_state.last_update = pd.Timestamp.now()
            
    def run(self):
        st.title("Sistema de Gestión de Contratos de Transporte")
        
        # Manual refresh button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Actualizar Datos"):
                with st.spinner("Actualizando datos..."):
                    if self.scheduler.force_update():
                        st.session_state.last_update = pd.Timestamp.now()
                        st.success("Datos actualizados exitosamente")
                    else:
                        st.error("Error al actualizar los datos")
                        
        with col2:
            st.text(f"Última actualización: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load data
        active_df, presentation_df = self.data_processor.load_data()
        
        # Process data
        active_df = self.data_processor.process_contracts(active_df, 'active')
        presentation_df = self.data_processor.process_contracts(presentation_df, 'presentation')
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs([
            "Contratos Activos",
            "Contratos en Fase de Presentación",
            "Dashboard de Análisis"
        ])
        
        with tab1:
            # Render active contracts
            filters = FilterComponent.render_filters(active_df)
            filtered_df = self.data_processor.apply_filters(active_df, filters)
            TableComponent.render_table(filtered_df, "Contratos Activos")
            
        with tab2:
            # Render presentation phase contracts
            filters = FilterComponent.render_filters(presentation_df)
            filtered_df = self.data_processor.apply_filters(presentation_df, filters)
            TableComponent.render_table(filtered_df, "Contratos en Fase de Presentación")
            
        with tab3:
            # Render analytics
            analytics_data = self.data_processor.generate_analytics(active_df)
            AnalyticsComponent.render_analytics(active_df, analytics_data)
            
    def __del__(self):
        self.scheduler.stop()

if __name__ == "__main__":
    app = ContractManagementSystem()
    app.run()
