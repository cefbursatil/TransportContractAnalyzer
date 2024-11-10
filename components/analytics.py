import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class AnalyticsComponent:
    @staticmethod
    def render_analytics(df, analytics_data):
        """Render analytics dashboard"""
        st.header("Dashboard de Análisis")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Contratos",
                f"{analytics_data['total_contracts']:,}"
            )
            
        with col2:
            st.metric(
                "Valor Total",
                f"${analytics_data['total_value']:,.0f}"
            )
            
        with col3:
            st.metric(
                "Duración Promedio (días)",
                f"{analytics_data['avg_duration']:.1f}"
            )
            
        # Contracts by department
        st.subheader("Contratos por Departamento")
        fig_dept = px.bar(
            x=list(analytics_data['contracts_by_department'].keys()),
            y=list(analytics_data['contracts_by_department'].values()),
            labels={'x': 'Departamento', 'y': 'Número de Contratos'}
        )
        st.plotly_chart(fig_dept, use_container_width=True)
        
        # Contracts by type
        st.subheader("Distribución por Tipo de Contrato")
        fig_type = px.pie(
            values=list(analytics_data['contracts_by_type'].values()),
            names=list(analytics_data['contracts_by_type'].keys())
        )
        st.plotly_chart(fig_type, use_container_width=True)
        
        # Monthly trend
        st.subheader("Tendencia Mensual de Contratos")
        monthly_data = pd.Series(analytics_data['monthly_contracts'])
        fig_trend = px.line(
            x=monthly_data.index.astype(str),
            y=monthly_data.values,
            labels={'x': 'Mes', 'y': 'Número de Contratos'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
