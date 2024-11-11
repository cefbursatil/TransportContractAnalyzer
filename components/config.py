import streamlit as st
import json
import os
import logging

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
                ]
            }
            
            config = default_config.copy()
            config_file = "config.json"

            # Try to load existing config
            if os.path.exists(config_file):
                try:
                    # Check file permissions
                    if not os.access(config_file, os.R_OK | os.W_OK):
                        logger.error(f"Insufficient permissions for config file: {config_file}")
                        st.error("Error: No hay permisos suficientes para acceder al archivo de configuración")
                        os.chmod(config_file, 0o644)  # Set read/write permissions
                    
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        config.update(file_config)
                        logger.info("Configuration loaded successfully")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in config file: {str(e)}")
                    st.warning("Error al cargar el archivo de configuración. Usando valores predeterminados.")
                except PermissionError as e:
                    logger.error(f"Permission error accessing config file: {str(e)}")
                    st.warning("Error de permisos al acceder al archivo de configuración. Usando valores predeterminados.")
                except Exception as e:
                    logger.error(f"Unexpected error loading config: {str(e)}")
                    st.warning(f"Error inesperado al cargar la configuración: {str(e)}")
            else:
                logger.info("No existing config file found, using defaults")
                st.info("No se encontró archivo de configuración. Usando valores predeterminados.")
            
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
            
            # Save button
            if st.button("Guardar Configuración"):
                try:
                    new_config = {
                        "codeCategory": new_code_category,
                        "useFilterKeywords": new_use_filter,
                        "keywords": [k.strip() for k in new_keywords if k.strip()]
                    }
                    
                    # Save to config file
                    with open(config_file, 'w') as f:
                        json.dump(new_config, f, indent=2)
                    logger.info("Configuration saved successfully")
                    
                    # Update secop.py variables
                    try:
                        with open('secop.py', 'r') as f:
                            content = f.read()
                            
                        # Update variables in secop.py
                        new_content = []
                        for line in content.split('\n'):
                            if line.startswith('codeCategory='):
                                new_content.append(f"codeCategory='{new_code_category}'")
                            elif line.startswith('useFilterKeywords='):
                                new_content.append(f"useFilterKeywords={str(new_use_filter)}")
                            elif line.startswith('keywords = ['):
                                new_content.append("keywords = [")
                                for keyword in new_keywords:
                                    if keyword.strip():
                                        new_content.append(f'    "{keyword.strip()}",')
                                new_content.append("]")
                            else:
                                new_content.append(line)
                                
                        with open('secop.py', 'w') as f:
                            f.write('\n'.join(new_content))
                        
                        st.success("Configuración guardada exitosamente")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error updating secop.py: {str(e)}")
                        st.error(f"Error al actualizar secop.py: {str(e)}")
                except Exception as e:
                    logger.error(f"Error saving configuration: {str(e)}")
                    st.error(f"Error al guardar la configuración: {str(e)}")
        except Exception as e:
            logger.error(f"Error in configuration component: {str(e)}")
            st.error(f"Error en el componente de configuración: {str(e)}")
            st.info("Por favor, contacte al administrador si este error persiste.")
