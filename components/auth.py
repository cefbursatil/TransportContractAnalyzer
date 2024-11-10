import streamlit as st
import bcrypt
import jwt
import datetime
import os
from typing import Optional, Tuple
import psycopg2
from psycopg2.extras import DictCursor

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

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    hashed_password = self.hash_password(password)
                    cur.execute(
                        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (username, email, hashed_password)
                    )
                    conn.commit()
                    return True, "User created successfully"
        except psycopg2.Error as e:
            if e.pgcode == '23505':  # Unique violation
                return False, "Username or email already exists"
            return False, f"Database error: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        "SELECT id, username, password_hash FROM users WHERE username = %s AND is_active = true",
                        (username,)
                    )
                    user = cur.fetchone()
                    
                    if user and self.verify_password(password, user['password_hash']):
                        token = jwt.encode(
                            {
                                'user_id': user['id'],
                                'username': user['username'],
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                            },
                            self.jwt_secret,
                            algorithm='HS256'
                        )
                        return True, "Login successful", {'token': token, 'username': user['username']}
                    return False, "Invalid username or password", None
        except psycopg2.Error as e:
            return False, f"Database error: {str(e)}", None

    def render_login_signup(self):
        if 'authentication_status' not in st.session_state:
            st.session_state.authentication_status = None

        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", key="login_button"):
                success, message, user_data = self.authenticate_user(username, password)
                if success:
                    st.session_state.authentication_status = True
                    st.session_state.username = user_data['username']
                    st.session_state.token = user_data['token']
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            st.subheader("Sign Up")
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Sign Up", key="signup_button"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    success, message = self.create_user(new_username, new_email, new_password)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)

    def check_authentication(self) -> bool:
        return st.session_state.get('authentication_status', False)

    def logout(self):
        if st.sidebar.button("Logout"):
            st.session_state.authentication_status = None
            st.session_state.username = None
            st.session_state.token = None
            st.rerun()
