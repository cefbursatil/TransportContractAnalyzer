import streamlit as st
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import xlsxwriter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(df, report_type, filters=None):
        """Generate a PDF report from the dataframe"""
        try:
            # Create buffer for PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            # Create story for PDF content
            story = []
            styles = getSampleStyleSheet()
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            title = Paragraph(f"Reporte de Contratos - {report_type}", title_style)
            story.append(title)
            
            # Add timestamp
            timestamp = Paragraph(
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles['Normal']
            )
            story.append(timestamp)
            story.append(Spacer(1, 20))
            
            # Add filters if provided
            if filters:
                filter_text = "Filtros aplicados:\n" + "\n".join([f"{k}: {v}" for k, v in filters.items()])
                story.append(Paragraph(filter_text, styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Prepare data for table
            if not df.empty:
                # Select relevant columns
                columns = [
                    'nombre_entidad',
                    'departamento',
                    'tipo_de_contrato',
                    'valor_del_contrato',
                    'fecha_de_firma',
                    'estado_contrato'
                ]
                columns = [col for col in columns if col in df.columns]
                
                # Format data
                table_data = [columns]  # Header row
                for _, row in df[columns].iterrows():
                    formatted_row = []
                    for col in columns:
                        value = row[col]
                        if col == 'valor_del_contrato':
                            value = f"${value:,.0f}" if pd.notnull(value) else "N/A"
                        elif col == 'fecha_de_firma':
                            value = value.strftime('%Y-%m-%d') if pd.notnull(value) else "N/A"
                        formatted_row.append(str(value))
                    table_data.append(formatted_row)
                
                # Create table
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise

    @staticmethod
    def generate_excel_report(df, report_type, filters=None):
        """Generate an Excel report from the dataframe"""
        try:
            # Create buffer for Excel
            buffer = io.BytesIO()
            
            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write data to Excel
                df.to_excel(writer, sheet_name='Contratos', index=False)
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Contratos']
                
                # Add formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Write headers
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 15)
                
                # Add filters information
                if filters:
                    filter_sheet = workbook.add_worksheet('Filtros')
                    filter_sheet.write(0, 0, 'Filtro', header_format)
                    filter_sheet.write(0, 1, 'Valor', header_format)
                    for i, (key, value) in enumerate(filters.items(), 1):
                        filter_sheet.write(i, 0, key)
                        filter_sheet.write(i, 1, str(value))
                
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}")
            raise

    @staticmethod
    def render_report_generator():
        """Render the report generation interface"""
        st.header("Generador de Reportes")
        
        # Get data from session state
        if 'data' not in st.session_state:
            st.warning("No hay datos disponibles para generar reportes")
            return
            
        df = st.session_state.data
        
        # Report configuration
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Tipo de Reporte",
                ["Contratos Activos", "Contratos Históricos", "Análisis Estadístico"]
            )
            
        with col2:
            file_format = st.selectbox(
                "Formato del Reporte",
                ["PDF", "Excel"]
            )
        
        # Report content selection
        st.subheader("Contenido del Reporte")
        
        include_filters = st.checkbox("Incluir información de filtros", value=True)
        include_stats = st.checkbox("Incluir estadísticas básicas", value=True)
        include_graphs = st.checkbox("Incluir gráficos", value=True)
        
        # Generate report button
        if st.button("Generar Reporte"):
            try:
                # Apply filters if any
                filters = st.session_state.get('filters', {})
                
                # Generate report
                if file_format == "PDF":
                    buffer = ReportGenerator.generate_pdf_report(
                        df,
                        report_type,
                        filters if include_filters else None
                    )
                    
                    # Provide download button
                    st.download_button(
                        label="Descargar PDF",
                        data=buffer,
                        file_name=f"reporte_contratos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    buffer = ReportGenerator.generate_excel_report(
                        df,
                        report_type,
                        filters if include_filters else None
                    )
                    
                    # Provide download button
                    st.download_button(
                        label="Descargar Excel",
                        data=buffer,
                        file_name=f"reporte_contratos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                    
                st.success("Reporte generado exitosamente")
                
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                st.error("Error al generar el reporte")
