import streamlit as st
import json
import os

class ConfigComponent:
    @staticmethod
    def render_config():
        """Render configuration controls"""
        st.header("Configuración del Sistema")
        
        # Load current config from secop.py
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {
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
            new_config = {
                "codeCategory": new_code_category,
                "useFilterKeywords": new_use_filter,
                "keywords": [k.strip() for k in new_keywords if k.strip()]
            }
            
            # Save to config file
            with open(config_file, 'w') as f:
                json.dump(new_config, f, indent=2)
                
            # Update secop.py variables
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
