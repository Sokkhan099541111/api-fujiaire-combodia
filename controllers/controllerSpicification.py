import datetime
import aiomysql
from db import get_db_connection  # Should return an aiomysql connection pool


# ===============================
# Get all spicifications
# ===============================
async def get_all_spicifications():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM spicification WHERE status = 1")
        rows = await cursor.fetchall()
    await conn.ensure_closed()
    return rows


# ===============================
# Get spicification by ID
# ===============================
async def get_spicification_by_id(spicification_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "SELECT * FROM spicification WHERE id = %s", (spicification_id,)
        )
        row = await cursor.fetchone()
    await conn.ensure_closed()
    return row


# ===============================
# Create spicification
# ===============================
async def create_spicification(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Check if user_id exists
        await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
        if not await cursor.fetchone():
            await conn.ensure_closed()
            return {"error": "user_id not found"}

        now = datetime.datetime.utcnow()
        await cursor.execute("""
            INSERT INTO spicification 
            (category, category_sub, title, descriptions, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("category"),
            data.get("category_sub"),
            data.get("title"),
            data.get("descriptions"),
            data.get("user_id"),
            data.get("status", 1),
            now,
            now
        ))
        spicification_id = cursor.lastrowid
        await conn.commit()
    await conn.ensure_closed()
    return {"id": spicification_id, **data}


# ===============================
# Update spicification
# ===============================
async def update_spicification(spicification_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Get current created_at to preserve
        await cursor.execute("SELECT created_at FROM spicification WHERE id = %s", (spicification_id,))
        row = await cursor.fetchone()
        if not row:
            await conn.ensure_closed()
            return {"error": "Spicification not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.utcnow()

        await cursor.execute("""
            UPDATE spicification 
            SET category=%s, category_sub=%s, title=%s, descriptions=%s, user_id=%s,
                status=%s, created_at=%s, updated_at=%s
            WHERE id=%s
        """, (
            data.get("category"),
            data.get("category_sub"),
            data.get("title"),
            data.get("descriptions"),
            data.get("user_id"),
            data.get("status", 1),
            created_at,
            updated_at,
            spicification_id
        ))
        await conn.commit()
    await conn.ensure_closed()
    return {"id": spicification_id, **data}


# ===============================
# Soft delete spicification
# ===============================
async def delete_spicification(spicification_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "UPDATE spicification SET status = 0 WHERE id = %s", (spicification_id,)
        )
        await conn.commit()
    await conn.ensure_closed()
    return {"message": f"Spicification {spicification_id} soft-deleted"}
