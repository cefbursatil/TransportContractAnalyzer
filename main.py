import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.scheduler import DataUpdateScheduler
from components.tables import TableComponent
from components.analytics import AnalyticsComponent
from components.config import ConfigComponent
from components.auth import AuthComponent
from components.reports import ReportGenerator
import logging
from styles import apply_custom_styles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Sistema de Gestión de Contratos de Transporte",
    page_icon="🚦",
    layout="wide"
)

class ContractManagementSystem:
    def __init__(self):
        try:
            self.scheduler = DataUpdateScheduler()
            self.data_processor = DataProcessor()
            self.auth = AuthComponent()
            
            # Initialize session state
            if 'last_update' not in st.session_state:
                st.session_state.last_update = pd.Timestamp.now()
            if 'show_loading' not in st.session_state:
                st.session_state.show_loading = False
        except Exception as e:
            logger.error(f"Error initializing system: {str(e)}")
            st.error(f"Error initializing system: {str(e)}")
            
    def run(self):
        try:
            # Apply custom styles
            apply_custom_styles()
            
            st.title("Sistema de Gestión de Contratos de Transporte")

            # Authentication check
            if not st.session_state.get('authentication_status'):
                self.auth.render_login_signup()
                return

            # Show logout button in sidebar
            with st.sidebar:
                st.text(f"Usuario: {st.session_state['username']}")
                self.auth.logout()
                
                # Add system status indicators
                st.subheader("Estado del Sistema")
                st.info(f"Última actualización: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Manual refresh button
                if st.button("🔄 Actualizar Datos", key="refresh_button"):
                    st.session_state.show_loading = True
                    with st.spinner("Actualizando datos..."):
                        if self.scheduler.force_update():
                            st.session_state.last_update = pd.Timestamp.now()
                            st.success("Datos actualizados exitosamente")
                        else:
                            st.error("Error al actualizar los datos")
                    st.session_state.show_loading = False
            
            try:
                # Show loading indicator
                if st.session_state.show_loading:
                    with st.spinner("Cargando datos..."):
                        active_df, historical_df = self.data_processor.load_data()
                else:
                    active_df, historical_df = self.data_processor.load_data()
                
                if active_df.empty and historical_df.empty:
                    st.warning("No se encontraron datos. Por favor, verifique los archivos CSV.")
                    return
                    
                # Calculate and display key metrics
                col1, col2, col3 = st.columns(3)
                active_stats = DataProcessor.get_contract_statistics(active_df)
                
                with col1:
                    st.metric(
                        "Contratos Activos",
                        f"{active_stats['total_contracts']:,}",
                        help="Número total de contratos activos"
                    )
                
                with col2:
                    st.metric(
                        "Valor Total",
                        f"${active_stats['total_value']:,.0f}",
                        help="Valor total de contratos activos"
                    )
                
                with col3:
                    st.metric(
                        "Duración Promedio",
                        f"{active_stats['avg_duration']:.0f} días",
                        help="Duración promedio de contratos"
                    )
                
                # Create tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Contratos Activos",
                    "Contratos Históricos",
                    "Dashboard de Análisis",
                    "Reportes",
                    "Configuración"
                ])
                
                with tab1:
                    TableComponent.render_table(active_df, "Contratos Activos")
                    
                with tab2:
                    TableComponent.render_table(historical_df, "Contratos Históricos")
                    
                with tab3:
                    AnalyticsComponent.render_analytics(active_df, historical_df)
                    
                with tab4:
                    st.session_state.data = active_df  # Store unfiltered data for reports
                    ReportGenerator.render_report_generator()
                    
                with tab5:
                    ConfigComponent.render_config()
                    
            except Exception as e:
                logger.error(f"Error in main application flow: {str(e)}")
                st.error("Error en la aplicación. Por favor, contacte al administrador.")
                
        except Exception as e:
            logger.error(f"Error in application: {str(e)}")
            st.error(f"Error in application: {str(e)}")
            
    def __del__(self):
        try:
            self.scheduler.stop()
        except:
            pass

if __name__ == "__main__":
    app = ContractManagementSystem()
    app.run()
