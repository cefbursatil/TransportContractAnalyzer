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
            if not st.session_state.get('authentication_status'):
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
                active_df, historical_df = self.data_processor.load_data()
                
                if active_df.empty and historical_df.empty:
                    st.warning("No se encontraron datos. Por favor, verifique los archivos CSV.")
                    return
                    
                # Process data with error handling
                try:
                    active_df = self.data_processor.process_contracts(active_df, 'active')
                    historical_df = self.data_processor.process_contracts(historical_df, 'historical')
                except Exception as e:
                    logger.error(f"Error processing data: {str(e)}")
                    st.error("Error al procesar los datos")
                    return
                
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
                    if historical_df.empty:
                        logger.info("Historical DataFrame is empty")
                        st.info("No hay datos históricos disponibles")
                    else:
                        logger.info(f"Historical DataFrame has {len(historical_df)} rows")
                        logger.info(f"Historical DataFrame columns: {historical_df.columns.tolist()}")
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
