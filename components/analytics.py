import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging

class AnalyticsComponent:
    @staticmethod
    def render_analytics(active_df, historical_df):
        """Render analytics dashboard with separate sections for open and historical contracts"""
        st.header("Dashboard de Análisis")
        
        # Create tabs for different contract types
        tab1, tab2 = st.tabs(["Contratos Activos", "Contratos Históricos"])
        
        with tab1:
            AnalyticsComponent._render_contract_analysis(
                active_df, 
                "Análisis de Contratos Activos"
            )
            
        with tab2:
            AnalyticsComponent._render_contract_analysis(
                historical_df,
                "Análisis de Contratos Históricos"
            )
    
    @staticmethod
    def _render_contract_analysis(df, title):
        """Render analysis section for a specific contract type"""
        st.subheader(title)
        
        if df.empty:
            st.warning("No hay datos disponibles para el análisis")
            return
            
        try:
            # Key metrics in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_value = df['valor_del_contrato'].sum() if 'valor_del_contrato' in df.columns else 0
                st.metric(
                    "Valor Total de Contratos",
                    f"${total_value:,.0f}"
                )
                
            with col2:
                contract_count = len(df)
                st.metric(
                    "Número de Contratos",
                    f"{contract_count:,}"
                )
                
            with col3:
                avg_duration = df['duracion'].mean() if 'duracion' in df.columns else df['dias_adicionados'].mean() if 'dias_adicionados' in df.columns else 0
                st.metric(
                    "Duración Promedio (días)",
                    f"{avg_duration:.1f}"
                )
            
            try:
                # Department distribution
                if 'departamento' in df.columns:
                    st.subheader("Distribución por Departamento")
                    dept_counts = df['departamento'].value_counts()
                    fig_dept = px.bar(
                        x=dept_counts.index,
                        y=dept_counts.values,
                        labels={'x': 'Departamento', 'y': 'Número de Contratos'}
                    )
                    st.plotly_chart(fig_dept, use_container_width=True)
            except Exception as e:
                logging.error(f"Error rendering department distribution: {str(e)}")
                st.error("Error al mostrar la distribución por departamento")
            
            try:
                # Contract type distribution
                if 'tipo_de_contrato' in df.columns:
                    st.subheader("Distribución por Tipo de Contrato")
                    type_counts = df['tipo_de_contrato'].value_counts()
                    fig_type = px.pie(
                        values=type_counts.values,
                        names=type_counts.index
                    )
                    st.plotly_chart(fig_type, use_container_width=True)
            except Exception as e:
                logging.error(f"Error rendering contract type distribution: {str(e)}")
                st.error("Error al mostrar la distribución por tipo de contrato")
            
            try:
                # Monthly trend
                if 'fecha_de_firma' in df.columns:
                    st.subheader("Tendencia Mensual")
                    monthly_data = df.groupby(df['fecha_de_firma'].dt.to_period('M')).agg({
                        'valor_del_contrato': 'sum',
                        'id_contrato': 'count'
                    }).reset_index()
                    
                    fig_trend = go.Figure()
                    
                    # Number of contracts line
                    fig_trend.add_trace(go.Scatter(
                        x=monthly_data['fecha_de_firma'].astype(str),
                        y=monthly_data['id_contrato'],
                        name='Número de Contratos',
                        line=dict(color='blue')
                    ))
                    
                    # Contract value line
                    fig_trend.add_trace(go.Scatter(
                        x=monthly_data['fecha_de_firma'].astype(str),
                        y=monthly_data['valor_del_contrato'],
                        name='Valor Total',
                        yaxis='y2',
                        line=dict(color='red')
                    ))
                    
                    fig_trend.update_layout(
                        title='Tendencia Mensual',
                        yaxis=dict(title='Número de Contratos'),
                        yaxis2=dict(
                            title='Valor Total (COP)',
                            overlaying='y',
                            side='right',
                            tickformat=',.0f'
                        ),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e:
                logging.error(f"Error rendering monthly trend: {str(e)}")
                st.error("Error al mostrar la tendencia mensual")
        except Exception as e:
            logging.error(f"Error in contract analysis: {str(e)}")
            st.error(f"Error en el análisis de contratos: {str(e)}")
