import aiomysql
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from contextlib import asynccontextmanager

load_dotenv()

pool = None

async def init_db_pool():
    global pool
    if pool is not None and not pool._closed:
        return

    try:
        pool = await aiomysql.create_pool(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306)),
            autocommit=True,
            minsize=1,    # fix: minsize <= maxsize
            maxsize=5,
            charset="utf8mb4"
        )
        print("✅ MySQL connection pool created successfully")
    except Exception as e:
        print("❌ Error creating MySQL pool:", e)
        raise HTTPException(status_code=500, detail=f"Database pool error: {e}")

@asynccontextmanager
async def get_db_connection():
    global pool
    if pool is None or pool._closed:
        await init_db_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)
