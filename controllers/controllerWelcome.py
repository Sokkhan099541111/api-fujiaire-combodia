import datetime
from db import get_db_connection
import aiomysql

# ===============================
# Get all welcome entries
# ===============================
async def get_all_welcome():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM welcome")
        rows = await cursor.fetchall()
    conn.close()
    return rows

# ===============================
# Get welcome by ID
# ===============================
async def get_welcome_by_id(welcome_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE id = %s", (welcome_id,))
        row = await cursor.fetchone()
    conn.close()
    return row

# ===============================
# Create welcome entry
# ===============================
async def create_welcome(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Validate foreign keys
        await cursor.execute("SELECT id FROM gallery WHERE id = %s", (data.get("image_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "image_id not found"}

        await cursor.execute("SELECT id FROM banner WHERE id = %s", (data.get("banner_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "banner_id not found"}

        await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "user_id not found"}

        now = datetime.datetime.now()
        await cursor.execute("""
            INSERT INTO welcome (title, detail, image_id, path, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("title"),
            data.get("detail"),
            data.get("image_id"),
            data.get("path"),
            data.get("user_id"),
            data.get("status", 1),
            now,
            now
        ))
        await conn.commit()
        welcome_id = cursor.lastrowid
    conn.close()
    return {"id": welcome_id, **data, "created_at": now, "updated_at": now}

# ===============================
# Update welcome entry
# ===============================
async def update_welcome(welcome_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Preserve created_at
        await cursor.execute("SELECT created_at FROM welcome WHERE id = %s", (welcome_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Welcome not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.now()

        await cursor.execute("""
            UPDATE welcome
            SET title = %s, detail = %s, image_id = %s, path = %s, user_id = %s,
                status = %s, created_at = %s, updated_at = %s
            WHERE id = %s
        """, (
            data.get("title"),
            data.get("detail"),
            data.get("image_id"),
            data.get("path"),
            data.get("user_id"),
            data.get("status", 1),
            created_at,
            updated_at,
            welcome_id
        ))
        await conn.commit()
    conn.close()
    return {"id": welcome_id, **data, "created_at": created_at, "updated_at": updated_at}

# ===============================
# Soft delete welcome entry
# ===============================
async def delete_welcome(welcome_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("UPDATE welcome SET status = 0 WHERE id = %s", (welcome_id,))
        await conn.commit()
    conn.close()
    return {"message": f"Welcome {welcome_id} soft-deleted (status = 0)"}

# ===============================
# Get all welcome entries for public
# ===============================
async def get_all_welcome_public():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE status = 1")
        rows = await cursor.fetchall()
    conn.close()
    return rows
