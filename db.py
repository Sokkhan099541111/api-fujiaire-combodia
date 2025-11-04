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
