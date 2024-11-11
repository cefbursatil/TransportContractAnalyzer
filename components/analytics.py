import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class AnalyticsComponent:
    @staticmethod
    def render_analytics(active_df, historical_df):
        try:
            if active_df.empty and historical_df.empty:
                st.warning("No hay datos disponibles para análisis")
                return
                
            tab1, tab2 = st.tabs(["Contratos Activos", "Contratos Históricos"])
            
            with tab1:
                if not active_df.empty:
                    AnalyticsComponent._render_contract_analysis(active_df)
                else:
                    st.info("No hay datos de contratos activos disponibles")
                    
            with tab2:
                if not historical_df.empty:
                    AnalyticsComponent._render_contract_analysis(historical_df)
                else:
                    st.info("No hay datos de contratos históricos disponibles")
                    
        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error("Error al generar análisis")

    @staticmethod
    def _render_contract_analysis(df):
        """Render analysis section for a specific contract type"""
        try:
            if df.empty:
                st.info("No hay datos disponibles para el análisis")
                return
            
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
                avg_duration = df['duracion'].mean() if 'duracion' in df.columns else 0
                st.metric(
                    "Duración Promedio (días)",
                    f"{avg_duration:.1f}"
                )
                
            # Department distribution
            if 'departamento' in df.columns and not df['departamento'].empty:
                st.subheader("Distribución por Departamento")
                dept_counts = df['departamento'].value_counts()
                if not dept_counts.empty:
                    fig_dept = px.bar(
                        x=dept_counts.index,
                        y=dept_counts.values,
                        labels={'x': 'Departamento', 'y': 'Número de Contratos'}
                    )
                    st.plotly_chart(fig_dept, use_container_width=True)
                else:
                    st.info("No hay datos de departamentos disponibles")
            
            # Contract type distribution
            if 'tipo_de_contrato' in df.columns and not df['tipo_de_contrato'].empty:
                st.subheader("Distribución por Tipo de Contrato")
                type_counts = df['tipo_de_contrato'].value_counts()
                if not type_counts.empty:
                    fig_type = px.pie(
                        values=type_counts.values,
                        names=type_counts.index
                    )
                    st.plotly_chart(fig_type, use_container_width=True)
                else:
                    st.info("No hay datos de tipos de contratos disponibles")
            
            # Monthly trend
            if 'fecha_de_firma' in df.columns and not df['fecha_de_firma'].empty:
                st.subheader("Tendencia Mensual")
                try:
                    monthly_data = df.groupby(pd.to_datetime(df['fecha_de_firma']).dt.to_period('M')).agg({
                        'valor_del_contrato': 'sum',
                        'id_contrato': 'count'
                    }).reset_index()
                    
                    if not monthly_data.empty:
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
                    else:
                        st.info("No hay datos suficientes para mostrar la tendencia mensual")
                except Exception as e:
                    logger.error(f"Error generating monthly trend: {str(e)}")
                    st.error("Error al generar la tendencia mensual")
                
        except Exception as e:
            logger.error(f"Error in contract analysis: {str(e)}")
            st.error("Error al generar el análisis de contratos")
