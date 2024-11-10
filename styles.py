import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stButton button {
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        
        .stButton button:hover {
            background-color: #45a049;
        }
        
        .streamlit-expanderHeader {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .stDataFrame {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        
        .css-1d391kg {
            padding-top: 1rem;
        }
        
        h1 {
            color: #1E88E5;
            font-size: 2.5em;
            margin-bottom: 1rem;
        }
        
        h2 {
            color: #424242;
            font-size: 1.8em;
            margin-top: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 1.2em;
        }
        </style>
    """, unsafe_allow_html=True)
