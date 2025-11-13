import aiomysql
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

pool = None

# ✅ Initialize MySQL connection pool
async def init_db_pool():
    global pool
    if pool is not None and not pool._closed:
        return  # already connected

    try:
        pool = await aiomysql.create_pool(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306)),
            autocommit=True,
            maxsize=5000000,         
            # maxsize=50,         
            charset="utf8mb4"
        )
        print("✅ MySQL connection pool created successfully")

    except Exception as e:
        print("❌ Error creating MySQL pool:", e)
        raise HTTPException(status_code=500, detail=f"Database pool error: {e}")


# ✅ Get DB connection safely
async def get_db_connection():
    global pool
    if pool is None or pool._closed:
        await init_db_pool()

    try:
        conn = await pool.acquire()
        return conn
    except Exception as e:
        print("❌ Error acquiring connection:", e)
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


# ✅ Helper: safely release connection (important!)
async def release_db_connection(conn):
    global pool
    if pool and conn:
        pool.release(conn)
