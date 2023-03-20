from dotenv import load_dotenv
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import base64
import hashlib
import uuid
import psycopg2
import jwt
import os

# Load env variables from .env
load_dotenv()

# Get database credentials from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Define user table
USERS_TABLE = 'users'
USER_COLUMNS = ['username', 'password', 'email']

# Define password reset table
PASSWORD_RESET_TABLE = 'password_reset'
PASSWORD_RESET_COLUMNS = ['username', 'reset_token', 'expiry_date']

# Define password reset expiry time (in minutes)
PASSWORD_RESET_EXPIRY_MINUTES = 30

# Connect to the database
conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

# create a cursor to execute SQL commands
cur = conn.cursor()

# Define user registration function
def register_user(username, password, email):
    # Check if username already exists
    query = f"SELECT * FROM {USERS_TABLE} WHERE username = '{username}'"
    result = pd.read_sql_query(query, DATABASE_URL)
    if not result.empty:
        return False, 'Username already exists'

    # Generate salt and hash password
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    # Insert user into database
    query = f"INSERT INTO {USERS_TABLE} ({','.join(USER_COLUMNS)}) VALUES ('{username}', '{hashed_password}', '{email}')"
    pd.read_sql_query(query, DATABASE_URL)

    return True, 'User registered successfully'

# Define user authentication function
def authenticate_user(username, password):
    # Get user from database
    query = f"SELECT * FROM {USERS_TABLE} WHERE username = '{username}'"
    result = pd.read_sql_query(query, DATABASE_URL)
    if result.empty:
        return False, 'User does not exist'

    # Verify password
    user = result.iloc[0]
    salt = user['password'][:32]
    hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    if hashed_password != user['password'][32:]:
        return False, 'Invalid password'

    return True, 'User authenticated successfully'

# Define password reset function
def reset_password(username, email):
    # Get user from database
    query = f"SELECT * FROM {USERS_TABLE} WHERE username = '{username}' AND email = '{email}'"
    result = pd.read_sql_query(query, DATABASE_URL)
    if result.empty:
        return False, 'User does not exist'

    # Generate reset token
    reset_token = uuid.uuid4().hex

    # Insert reset token into database
    expiry_date = pd.Timestamp.utcnow() + pd.Timedelta(minutes=PASSWORD_RESET_EXPIRY_MINUTES)
    query = f"INSERT INTO {PASSWORD_RESET_TABLE} ({','.join(PASSWORD_RESET_COLUMNS)}) VALUES ('{username}', '{reset_token}', '{expiry_date}')"
    pd.read_sql_query(query, DATABASE_URL)

    # Send email with reset link
    # ...

    return True, 'Password reset email sent'

# Define password reset validation function
# function to validate the reset token
def validate_reset_token(token, secret_key, expiration_time):
    try:
        # decode the token with the secret key
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        # check if the token has expired
        token_time = datetime.fromtimestamp(payload['exp'])
        if datetime.utcnow() > token_time + timedelta(minutes=expiration_time):
            return None
        return payload['user_id']
    except jwt.exceptions.DecodeError:
        return None
    except jwt.exceptions.ExpiredSignatureError:
        return None
