import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from utils import format_currency

def plot_contracts_by_department(df):
    """Create a bar chart of contracts by department"""
    dept_counts = df['departamento'].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Count']
    
    fig = px.bar(
        dept_counts,
        x='Department',
        y='Count',
        title='Contracts by Department',
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(t=50, b=100)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_contract_values_distribution(df):
    """Create a box plot of contract values"""
    fig = px.box(
        df,
        y='valor_del_contrato',
        title='Contract Values Distribution',
        points='outliers'
    )
    
    fig.update_layout(
        yaxis_title='Contract Value (COP)',
        height=400,
        margin=dict(t=50, b=50)
    )
    
    fig.update_yaxes(tickformat=',.0f')
    
    st.plotly_chart(fig, use_container_width=True)

def plot_contract_timeline(df):
    """Create a timeline of contracts"""
    df_timeline = df.groupby('fecha_de_firma').agg({
        'valor_del_contrato': 'sum',
        'id_contrato': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_timeline['fecha_de_firma'],
        y=df_timeline['id_contrato'],
        name='Number of Contracts',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=df_timeline['fecha_de_firma'],
        y=df_timeline['valor_del_contrato'],
        name='Total Value',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        title='Contract Timeline',
        yaxis=dict(title='Number of Contracts'),
        yaxis2=dict(
            title='Total Value (COP)',
            overlaying='y',
            side='right',
            tickformat=',.0f'
        ),
        height=400,
        margin=dict(t=50, b=50),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_contract_types(df):
    """Create a pie chart of contract types"""
    type_counts = df['tipo_de_contrato'].value_counts()
    
    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title='Contract Types Distribution'
    )
    
    fig.update_layout(
        height=400,
        margin=dict(t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
