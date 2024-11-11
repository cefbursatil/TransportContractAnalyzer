import streamlit as st
import json
import os
import logging

logger = logging.getLogger(__name__)

class ConfigComponent:
    @staticmethod
    def render_config():
        """Render configuration controls"""
        st.header("Configuración del Sistema")
        
        try:
            # Set up logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            # Default configuration
            default_config = {
                "codeCategory": "V1.811022%",
                "useFilterKeywords": True,
                "keywords": [
                    "Estudio de demanda", "Plan Maestro de Movilidad",
                    "Estudio de movilidad", "Plan infraestructura",
                    "plan local de seguridad vial", "Plan intermodal",
                    "Modelo de transporte", "Encuesta origen destino",
                    "Toma informacion de campo", "Caracterizacion de vías",
                    "Estudio de tránsito", "Diseño Señalización"
                ],
                "notification_recipients": []
            }
            
            config = default_config.copy()
            config_file = "config.json"

            # Try to load existing config
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        config.update(file_config)
                        logger.info("Configuration loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading config: {str(e)}")
                    st.warning("Error al cargar el archivo de configuración. Usando valores predeterminados.")

            # Create tabs for different configuration sections
            tab1, tab2 = st.tabs(["Configuración General", "Notificaciones"])
            
            with tab1:
                # Code Category input
                new_code_category = st.text_input(
                    "Código de Categoría",
                    value=config["codeCategory"],
                    help="Código de categoría para filtrar contratos (ej: V1.811022%)"
                )
                
                # Use Filter Keywords toggle
                new_use_filter = st.toggle(
                    "Usar Filtro de Palabras Clave",
                    value=config["useFilterKeywords"],
                    help="Activar/Desactivar el filtro por palabras clave"
                )
                
                # Keywords text area
                new_keywords = st.text_area(
                    "Palabras Clave",
                    value="\n".join(config["keywords"]),
                    height=200,
                    help="Una palabra clave por línea"
                ).split("\n")

            with tab2:
                st.subheader("Configuración de Notificaciones por Email")
                
                # Email recipients
                recipients_str = "\n".join(config.get("notification_recipients", []))
                new_recipients = st.text_area(
                    "Destinatarios de Notificaciones",
                    value=recipients_str,
                    height=100,
                    help="Ingrese las direcciones de correo electrónico (una por línea)"
                ).split("\n")
                
                # Test notification button
                if st.button("Probar Notificación"):
                    from utils.notifications import notify_new_contracts
                    test_contract = [{
                        'nombre_entidad': 'Entidad de Prueba',
                        'tipo_de_contrato': 'Contrato de Prueba',
                        'valor_del_contrato': 1000000,
                        'fecha_de_firma': '2024-01-01'
                    }]
                    recipients = [r.strip() for r in new_recipients if r.strip()]
                    if notify_new_contracts(test_contract, recipients):
                        st.success("Notificación de prueba enviada exitosamente")
                    else:
                        st.error("Error al enviar la notificación de prueba")
            
            # Save button
            if st.button("Guardar Configuración"):
                try:
                    new_config = {
                        "codeCategory": new_code_category,
                        "useFilterKeywords": new_use_filter,
                        "keywords": [k.strip() for k in new_keywords if k.strip()],
                        "notification_recipients": [r.strip() for r in new_recipients if r.strip()]
                    }
                    
                    # Save to config file
                    with open(config_file, 'w') as f:
                        json.dump(new_config, f, indent=2)
                    
                    # Update scheduler recipients
                    if 'app' in st.session_state:
                        st.session_state.app.scheduler.set_notification_recipients(
                            new_config["notification_recipients"]
                        )
                    
                    st.success("Configuración guardada exitosamente")
                    st.rerun()
                except Exception as e:
                    logger.error(f"Error saving configuration: {str(e)}")
                    st.error(f"Error al guardar la configuración: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in configuration component: {str(e)}")
            st.error(f"Error en el componente de configuración: {str(e)}")
