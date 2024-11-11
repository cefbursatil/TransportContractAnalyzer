import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)

class AnalyticsComponent:
    @staticmethod
    def render_analytics(active_df, historical_df):
        try:
            if active_df.empty and historical_df.empty:
                st.warning("No hay datos disponibles para análisis")
                return
                
            tab1, tab2, tab3 = st.tabs(["Vista General", "Análisis Detallado", "Predicciones"])
            
            with tab1:
                AnalyticsComponent._render_overview_analysis(active_df, historical_df)
                    
            with tab2:
                AnalyticsComponent._render_detailed_analysis(active_df, historical_df)
                
            with tab3:
                AnalyticsComponent._render_predictions(active_df, historical_df)
                    
        except Exception as e:
            logger.error(f"Error in analytics: {str(e)}")
            st.error("Error al generar análisis")

    @staticmethod
    def _render_overview_analysis(active_df, historical_df):
        """Render overview analysis section"""
        try:
            st.subheader("Resumen General")
            
            # Combine dataframes for total metrics
            combined_df = pd.concat([active_df, historical_df], ignore_index=True)
            
            # Key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_value = combined_df['valor_del_contrato'].sum() if 'valor_del_contrato' in combined_df.columns else 0
                st.metric(
                    "Valor Total de Contratos",
                    f"${total_value:,.0f}"
                )
                
            with col2:
                contract_count = len(combined_df)
                st.metric(
                    "Número Total de Contratos",
                    f"{contract_count:,}"
                )
                
            with col3:
                avg_value = combined_df['valor_del_contrato'].mean() if 'valor_del_contrato' in combined_df.columns else 0
                st.metric(
                    "Valor Promedio",
                    f"${avg_value:,.0f}"
                )
                
            with col4:
                active_count = len(active_df)
                st.metric(
                    "Contratos Activos",
                    f"{active_count:,}"
                )
            
            # Geographical Distribution
            if 'departamento' in combined_df.columns:
                st.subheader("Distribución Geográfica")
                dept_data = combined_df.groupby('departamento').agg({
                    'valor_del_contrato': 'sum',
                    'id_contrato': 'count'
                }).reset_index()
                
                # Create two columns for the charts
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_count = px.bar(
                        dept_data,
                        x='departamento',
                        y='id_contrato',
                        title='Contratos por Departamento',
                        labels={'id_contrato': 'Número de Contratos', 'departamento': 'Departamento'}
                    )
                    st.plotly_chart(fig_count, use_container_width=True)
                
                with col2:
                    fig_value = px.pie(
                        dept_data,
                        values='valor_del_contrato',
                        names='departamento',
                        title='Distribución del Valor por Departamento'
                    )
                    st.plotly_chart(fig_value, use_container_width=True)

        except Exception as e:
            logger.error(f"Error in overview analysis: {str(e)}")
            st.error("Error al generar el análisis general")

    @staticmethod
    def _render_detailed_analysis(active_df, historical_df):
        """Render detailed analysis section"""
        try:
            st.subheader("Análisis Detallado")
            
            # Contract Value Distribution
            if 'valor_del_contrato' in active_df.columns:
                st.write("### Distribución de Valores de Contratos")
                
                fig_box = px.box(
                    active_df,
                    y='valor_del_contrato',
                    title='Distribución de Valores',
                    points='all'
                )
                st.plotly_chart(fig_box, use_container_width=True)
                
                # Statistical summary
                q1 = active_df['valor_del_contrato'].quantile(0.25)
                q3 = active_df['valor_del_contrato'].quantile(0.75)
                iqr = q3 - q1
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mediana", f"${active_df['valor_del_contrato'].median():,.0f}")
                with col2:
                    st.metric("IQR", f"${iqr:,.0f}")
                with col3:
                    st.metric("Mínimo", f"${active_df['valor_del_contrato'].min():,.0f}")
                with col4:
                    st.metric("Máximo", f"${active_df['valor_del_contrato'].max():,.0f}")
            
            # Time Series Analysis
            if 'fecha_de_firma' in active_df.columns:
                st.write("### Análisis Temporal")
                
                # Monthly aggregation
                monthly_data = active_df.groupby(
                    pd.to_datetime(active_df['fecha_de_firma']).dt.to_period('M')
                ).agg({
                    'valor_del_contrato': ['sum', 'mean', 'count']
                }).reset_index()
                
                # Convert period to datetime for plotting
                monthly_data['fecha_de_firma'] = monthly_data['fecha_de_firma'].astype(str)
                
                # Create multiple plots
                fig = go.Figure()
                
                # Total value line
                fig.add_trace(go.Scatter(
                    x=monthly_data['fecha_de_firma'],
                    y=monthly_data['valor_del_contrato']['sum'],
                    name='Valor Total',
                    line=dict(color='blue')
                ))
                
                # Contract count line
                fig.add_trace(go.Scatter(
                    x=monthly_data['fecha_de_firma'],
                    y=monthly_data['valor_del_contrato']['count'],
                    name='Número de Contratos',
                    yaxis='y2',
                    line=dict(color='red')
                ))
                
                fig.update_layout(
                    title='Evolución Temporal',
                    yaxis=dict(title='Valor Total (COP)'),
                    yaxis2=dict(
                        title='Número de Contratos',
                        overlaying='y',
                        side='right'
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.error(f"Error in detailed analysis: {str(e)}")
            st.error("Error al generar el análisis detallado")

    @staticmethod
    def _render_predictions(active_df, historical_df):
        """Render predictions section"""
        try:
            st.subheader("Análisis Predictivo")
            
            if 'fecha_de_firma' in active_df.columns and 'valor_del_contrato' in active_df.columns:
                # Prepare data for prediction
                df = active_df.copy()
                df['fecha_de_firma'] = pd.to_datetime(df['fecha_de_firma'])
                df['dias'] = (df['fecha_de_firma'] - df['fecha_de_firma'].min()).dt.days
                
                # Simple linear regression
                X = df['dias'].values.reshape(-1, 1)
                y = df['valor_del_contrato'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate future dates
                future_days = np.array(range(X.max(), X.max() + 90)).reshape(-1, 1)  # 90 days prediction
                future_predictions = model.predict(future_days)
                
                # Create prediction plot
                fig = go.Figure()
                
                # Actual values
                fig.add_trace(go.Scatter(
                    x=df['fecha_de_firma'],
                    y=df['valor_del_contrato'],
                    name='Valores Reales',
                    mode='markers'
                ))
                
                # Predicted values
                future_dates = pd.date_range(
                    start=df['fecha_de_firma'].max(),
                    periods=90,
                    freq='D'
                )
                
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=future_predictions,
                    name='Predicción',
                    line=dict(dash='dash')
                ))
                
                fig.update_layout(
                    title='Predicción de Valores de Contratos (90 días)',
                    xaxis_title='Fecha',
                    yaxis_title='Valor del Contrato (COP)',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Confidence metrics
                r2_score = model.score(X, y)
                st.metric(
                    "Coeficiente de Determinación (R²)",
                    f"{r2_score:.2%}"
                )
                
                st.info("""
                Este es un modelo predictivo simple basado en regresión lineal.
                Las predicciones son estimaciones basadas en tendencias históricas
                y deben interpretarse con precaución.
                """)
                
        except Exception as e:
            logger.error(f"Error in predictions: {str(e)}")
            st.error("Error al generar predicciones")
