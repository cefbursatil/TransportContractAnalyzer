import streamlit as st
import bcrypt
import jwt
import datetime
import os
from typing import Optional, Tuple
import psycopg2
from psycopg2.extras import DictCursor
import logging

logger = logging.getLogger(__name__)

class AuthComponent:
    def __init__(self):
        self.conn_params = {
            'dbname': os.environ['PGDATABASE'],
            'user': os.environ['PGUSER'],
            'password': os.environ['PGPASSWORD'],
            'host': os.environ['PGHOST'],
            'port': os.environ['PGPORT']
        }
        self.jwt_secret = os.environ.get('JWT_SECRET', 'your-secret-key')

    def get_db_connection(self):
        return psycopg2.connect(**self.conn_params)

    def check_last_login_column(self):
        """Check if last_login column exists in users table"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'last_login';
                    """)
                    return bool(cur.fetchone())
        except Exception as e:
            logger.error(f"Error checking last_login column: {str(e)}")
            return False

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Check if username or email already exists
                    cur.execute(
                        "SELECT username FROM users WHERE username = %s OR email = %s",
                        (username, email)
                    )
                    if cur.fetchone():
                        return False, "Username or email already exists"

                    hashed_password = self.hash_password(password)
                    cur.execute(
                        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (username, email, hashed_password)
                    )
                    conn.commit()
                    logger.info(f"New user created: {username}")
                    return True, "User created successfully"
        except psycopg2.Error as e:
            logger.error(f"Database error creating user: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False, f"Error: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # First check if user exists and password is correct
                    cur.execute(
                        """
                        SELECT id, username, password_hash 
                        FROM users 
                        WHERE username = %s AND is_active = true
                        """,
                        (username,)
                    )
                    user = cur.fetchone()
                    
                    if not user:
                        return False, "Invalid username or password", None
                        
                    if not self.verify_password(password, user['password_hash']):
                        return False, "Invalid username or password", None

                    # Try to update last_login timestamp if column exists
                    try:
                        if self.check_last_login_column():
                            cur.execute(
                                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                                (user['id'],)
                            )
                            conn.commit()
                    except Exception as e:
                        # Log the error but continue with authentication
                        logger.warning(f"Failed to update last_login: {str(e)}")

                    # Generate JWT token
                    token = jwt.encode(
                        {
                            'user_id': user['id'],
                            'username': user['username'],
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                        },
                        self.jwt_secret,
                        algorithm='HS256'
                    )
                    logger.info(f"User logged in: {username}")
                    return True, "Login successful", {'token': token, 'username': user['username']}
                    
        except psycopg2.Error as e:
            logger.error(f"Database error during authentication: {str(e)}")
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False, f"Error: {str(e)}", None

    def render_login_signup(self):
        st.header("Autenticación")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Iniciar Sesión")
            username = st.text_input("Usuario", key="login_username")
            password = st.text_input("Contraseña", type="password", key="login_password")
            
            if st.button("Iniciar Sesión", key="login_button"):
                if not username or not password:
                    st.error("Por favor ingrese usuario y contraseña")
                    return

                success, message, user_data = self.authenticate_user(username, password)
                if success:
                    st.session_state['authentication_status'] = True
                    st.session_state['username'] = user_data['username']
                    st.session_state['token'] = user_data['token']
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            st.subheader("Registrarse")
            new_username = st.text_input("Usuario", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Contraseña", type="password", key="signup_password")
            confirm_password = st.text_input("Confirmar Contraseña", type="password", key="signup_confirm")
            
            if st.button("Registrarse", key="signup_button"):
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Por favor complete todos los campos")
                    return

                if new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                    return

                if len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                    return

                success, message = self.create_user(new_username, new_email, new_password)
                if success:
                    st.success(message)
                    st.info("Por favor inicie sesión con su nueva cuenta")
                else:
                    st.error(message)

    def logout(self):
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['authentication_status'] = None
            st.session_state['username'] = None
            st.session_state['token'] = None
            st.rerun()
