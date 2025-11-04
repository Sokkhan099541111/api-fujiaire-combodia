import datetime
from db import get_db_connection
import aiomysql

# ===============================
# Get all warranties (admin)
# ===============================
async def get_all_warranties():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM warranty")
        rows = await cursor.fetchall()
    conn.close()
    return rows

# ===============================
# Get warranty by ID
# ===============================
async def get_warranty_by_id(warranty_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM warranty WHERE id = %s", (warranty_id,))
        row = await cursor.fetchone()
    conn.close()
    return row

# ===============================
# Update warranty
# ===============================
async def update_warranty(warranty_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Check if warranty exists
        await cursor.execute("SELECT created_at FROM warranty WHERE id = %s", (warranty_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Warranty not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.now()

        await cursor.execute("""
            UPDATE warranty SET
                title = %s,
                descriptions = %s,
                image_id = %s,
                path = %s,
                user_id = %s,
                status = %s,
                created_at = %s,
                updated_at = %s
            WHERE id = %s
        """, (
            data.get("title"),
            data.get("descriptions"),
            data.get("image_id"),
            data.get("path"),
            data.get("user_id"),
            data.get("status", 1),
            created_at,
            updated_at,
            warranty_id
        ))
        await conn.commit()
    conn.close()
    return {"id": warranty_id, "updated_at": updated_at, **data}

# ===============================
# Soft delete warranty
# ===============================
async def delete_warranty(warranty_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("UPDATE warranty SET status = 0 WHERE id = %s", (warranty_id,))
        await conn.commit()
    conn.close()
    return {"message": f"Warranty {warranty_id} soft-deleted"}

# ===============================
# Get all warranties (public)
# ===============================
async def get_all_warranties_public():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM warranty WHERE status = 1")
        rows = await cursor.fetchall()
    conn.close()
    return rows
