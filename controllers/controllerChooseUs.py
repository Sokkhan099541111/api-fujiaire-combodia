import datetime
from db import get_db_connection
from fastapi import HTTPException
import aiomysql

# ------------------------------
# Get all (Admin)
# ------------------------------
async def get_all_choose_us():
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM choose_us WHERE status = 1 ORDER BY id DESC")
            rows = await cursor.fetchall()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching choose_us: {e}")
    finally:
        conn.close()

# ------------------------------
# Get by ID
# ------------------------------
async def get_choose_us_by_id(choose_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM choose_us WHERE id = %s", (choose_id,))
            row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Choose Us not found")
        return row
    finally:
        conn.close()

# ------------------------------
# Create
# ------------------------------
async def create_choose_us(data: dict):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            now = datetime.datetime.now()

            # Validate user_id
            await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
            if not await cursor.fetchone():
                raise HTTPException(status_code=400, detail="user_id not found")

            await cursor.execute("""
                INSERT INTO choose_us (image_id, title, category, category_sub, descriptions, path, user_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("image_id"),
                data.get("title"),
                data.get("category"),
                data.get("category_sub"),
                data.get("descriptions"),
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                now,
                now
            ))

            await conn.commit()
            choose_id = cursor.lastrowid
            return {"id": choose_id, **data, "created_at": now, "updated_at": now}
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ------------------------------
# Update
# ------------------------------
async def update_choose_us(choose_id: int, data: dict):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT created_at FROM choose_us WHERE id = %s", (choose_id,))
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Choose Us item not found")

            created_at = row["created_at"]
            updated_at = datetime.datetime.now()

            await cursor.execute("""
                UPDATE choose_us SET image_id=%s, title=%s, category=%s, category_sub=%s, descriptions=%s, path=%s,
                    user_id=%s, status=%s, created_at=%s, updated_at=%s WHERE id=%s
            """, (
                data.get("image_id"),
                data.get("title"),
                data.get("category"),
                data.get("category_sub"),
                data.get("descriptions"),
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                created_at,
                updated_at,
                choose_id
            ))

            await conn.commit()
            return {"id": choose_id, **data, "created_at": created_at, "updated_at": updated_at}
    finally:
        conn.close()

# ------------------------------
# Delete (Soft)
# ------------------------------
async def delete_choose_us(choose_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE choose_us SET status = 0 WHERE id = %s", (choose_id,))
            await conn.commit()
        return {"message": f"Choose Us {choose_id} soft-deleted"}
    finally:
        conn.close()

# ------------------------------
# Get all (Public)
# ------------------------------
async def get_all_choose_us_public():
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM choose_us WHERE status = 1 ORDER BY id DESC")
            rows = await cursor.fetchall()
        return rows
    finally:
        conn.close()

# ------------------------------
# Get by ID (Public)
# ------------------------------
async def get_choose_us_by_id_public(choose_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM choose_us WHERE id = %s", (choose_id,))
            row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Choose Us not found")
        return row
    finally:
        conn.close()
