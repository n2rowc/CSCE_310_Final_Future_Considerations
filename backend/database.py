# backend/database.py
import os
import mysql.connector
from dotenv import load_dotenv

# Load variables from .env file in this folder
load_dotenv()

def get_db_connection():
    """
    Returns a new MySQL connection to the online_bookstore database.
    Credentials are loaded from environment variables (see .env).
    """
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "online_bookstore"),
    )
    return conn
