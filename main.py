import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.scheduler import DataUpdateScheduler
from components.filters import FilterComponent
from components.tables import TableComponent
from components.analytics import AnalyticsComponent
from components.config import ConfigComponent
from components.auth import AuthComponent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Sistema de Gestión de Contratos de Transporte",
    page_icon="🚦",
    layout="wide"
)

# Load custom CSS
def load_css():
    try:
        st.markdown("""
            <style>
            .main {
                padding: 1rem;
            }
            .table-container {
                margin: 1rem 0;
            }
            .filter-container {
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 5px;
                margin-bottom: 1rem;
            }
            .analytics-card {
                padding: 1rem;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin: 0.5rem;
            }
            .stButton>button {
                width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error loading CSS: {str(e)}")
        st.error(f"Error loading CSS: {str(e)}")

# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

class ContractManagementSystem:
    def __init__(self):
        try:
            self.scheduler = DataUpdateScheduler()
            self.data_processor = DataProcessor()
            self.auth = AuthComponent()
            
            # Initialize session state
            if 'last_update' not in st.session_state:
                st.session_state.last_update = pd.Timestamp.now()
        except Exception as e:
            logger.error(f"Error initializing system: {str(e)}")
            st.error(f"Error initializing system: {str(e)}")
            
    def run(self):
        try:
            st.title("Sistema de Gestión de Contratos de Transporte")
            
            # Load CSS
            load_css()

            # Authentication check
            if not st.session_state['authentication_status']:
                self.auth.render_login_signup()
                return

            # Show logout button in sidebar
            st.sidebar.text(f"Usuario: {st.session_state['username']}")
            self.auth.logout()
            
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
            
            try:
                # Load data
                active_df, presentation_df = self.data_processor.load_data()
                
                # Process data
                active_df = self.data_processor.process_contracts(active_df, 'active')
                historical_df = self.data_processor.process_contracts(presentation_df, 'historical')
                
                # Create tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "Contratos Activos",
                    "Contratos Históricos",
                    "Dashboard de Análisis",
                    "Configuración"
                ])
                
                with tab1:
                    # Render active contracts
                    filters = FilterComponent.render_filters(active_df)
                    filtered_df = self.data_processor.apply_filters(active_df, filters)
                    TableComponent.render_table(filtered_df, "Contratos Activos")
                    
                with tab2:
                    # Render historical contracts
                    filters = FilterComponent.render_filters(historical_df)
                    filtered_df = self.data_processor.apply_filters(historical_df, filters)
                    TableComponent.render_table(filtered_df, "Contratos Históricos")
                    
                with tab3:
                    # Render analytics with separate sections
                    AnalyticsComponent.render_analytics(active_df, historical_df)
                    
                with tab4:
                    try:
                        # Render configuration
                        ConfigComponent.render_config()
                    except Exception as e:
                        logger.error(f"Error in configuration tab: {str(e)}")
                        st.error(f"Error in configuration tab: {str(e)}")
                        st.info("Please contact the administrator if this error persists.")
            except Exception as e:
                logger.error(f"Error loading data: {str(e)}")
                st.error(f"Error loading data: {str(e)}")
                st.info("Por favor, intente recargar la página. Si el problema persiste, contacte al administrador.")
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