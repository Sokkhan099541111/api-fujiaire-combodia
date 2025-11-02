# db.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            auth_plugin='mysql_native_password'
        )
        return conn
    except Error as e:
        print("❌ Error connecting to database:", e)
        return None
