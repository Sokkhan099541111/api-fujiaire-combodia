<<<<<<< HEAD
import aiomysql
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

pool = None

async def init_db_pool():
    global pool
    try:
        pool = await aiomysql.create_pool(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306)),
            autocommit=True,
            minsize=1,
            maxsize=10,
        )
        print("✅ MySQL connection pool created successfully")
    except Exception as e:
        print("❌ Error creating MySQL pool:", e)
        raise HTTPException(status_code=500, detail=f"Database pool error: {e}")

async def get_db_connection():
    if pool is None:
        await init_db_pool()

    try:
        conn = await pool.acquire()
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
=======
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
>>>>>>> 8d49c6b84cc6d05a2f74ec6138a4145acd273f6a
