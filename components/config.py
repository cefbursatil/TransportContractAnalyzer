import streamlit as st
import json
import os
import logging

logger = logging.getLogger(__name__)

class ConfigComponent:
    @staticmethod
    def load_config():
        """Load configuration from file"""
        try:
            config_file = "config.json"
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
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
                    
            return default_config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return default_config

    @staticmethod
    def save_config(config):
        """Save configuration to file"""
        try:
            config_file = "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            return False

    @staticmethod
    def render_config():
        try:
            st.header("Configuración del Sistema")
            
            # Load configuration
            config = ConfigComponent.load_config()
            
            # Create tabs for different configuration sections
            tab1, tab2 = st.tabs(["Configuración SECOP", "Notificaciones"])
            
            with tab1:
                with st.form("secop_config"):
                    st.subheader("Configuración SECOP")
                    
                    code_category = st.text_input(
                        "Código de Categoría",
                        value=config.get("codeCategory", "V1.811022%")
                    )
                    
                    use_keywords = st.checkbox(
                        "Usar filtro de palabras clave",
                        value=config.get("useFilterKeywords", True)
                    )
                    
                    keywords = st.text_area(
                        "Palabras clave (una por línea)",
                        value="\n".join(config.get("keywords", []))
                    )
                    
                    if st.form_submit_button("Guardar Configuración SECOP"):
                        new_config = config.copy()
                        new_config.update({
                            "codeCategory": code_category,
                            "useFilterKeywords": use_keywords,
                            "keywords": [k.strip() for k in keywords.split("\n") if k.strip()]
                        })
                        
                        if ConfigComponent.save_config(new_config):
                            st.success("Configuración SECOP guardada exitosamente")
                            st.rerun()
                        else:
                            st.error("Error al guardar la configuración SECOP")
            
            with tab2:
                st.subheader("Configuración de Notificaciones")
                
                # Add notification recipients outside form
                recipients_str = "\n".join(config.get("notification_recipients", []))
                recipients = st.text_area(
                    "Destinatarios de Notificaciones (uno por línea)",
                    value=recipients_str,
                    help="Ingrese las direcciones de correo electrónico"
                )
                
                # Save button
                if st.button("Guardar Destinatarios"):
                    new_config = config.copy()
                    new_config["notification_recipients"] = [
                        r.strip() for r in recipients.split("\n") if r.strip()
                    ]
                    
                    if ConfigComponent.save_config(new_config):
                        if 'app' in st.session_state:
                            st.session_state.app.scheduler.set_notification_recipients(
                                new_config["notification_recipients"]
                            )
                        st.success("Configuración de notificaciones guardada exitosamente")
                        st.rerun()
                    else:
                        st.error("Error al guardar la configuración de notificaciones")
                
                # Test notification button (outside form)
                if st.button("Probar Notificación"):
                    from utils.notifications import notify_new_contracts
                    test_contract = [{
                        'nombre_entidad': 'Entidad de Prueba',
                        'tipo_de_contrato': 'Contrato de Prueba',
                        'valor_del_contrato': 1000000,
                        'fecha_de_firma': '2024-01-01'
                    }]
                    
                    recipients_list = [r.strip() for r in recipients.split("\n") if r.strip()]
                    if recipients_list:
                        if notify_new_contracts(test_contract, recipients_list):
                            st.success("Notificación de prueba enviada exitosamente")
                        else:
                            st.error("Error al enviar la notificación de prueba")
                    else:
                        st.warning("Por favor, ingrese al menos un destinatario de correo electrónico")
                    
        except Exception as e:
            logger.error(f"Error rendering config: {str(e)}")
            st.error("Error al cargar la configuración. Por favor, contacte al administrador.")
