import datetime
import aiomysql
from db import get_db_connection

# ---------------------------------------------------------------------
# 🔹 Helper: run query with connection management (auto release)
# ---------------------------------------------------------------------
async def execute_query(query: str, params=None, fetchone=False, fetchall=False, commit=False):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params or ())
            if commit:
                await conn.commit()
            if fetchone:
                return await cursor.fetchone()
            if fetchall:
                return await cursor.fetchall()
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ---------------------------------------------------------------------
# 🔹 Get all active banners
# ---------------------------------------------------------------------
async def get_all_banners():
    query = """
        SELECT b.*, g.image_id AS gallery_image
        FROM banner b
        LEFT JOIN gallery g ON b.image_id = g.id
        WHERE b.status = 1
    """
    return await execute_query(query, fetchall=True)


# ---------------------------------------------------------------------
# 🔹 Get banner by ID
# ---------------------------------------------------------------------
async def get_banner_by_id(banner_id: int):
    query = "SELECT * FROM banner WHERE id = %s"
    return await execute_query(query, (banner_id,), fetchone=True)


# ---------------------------------------------------------------------
# 🔹 Get banner by type (latest updated)
# ---------------------------------------------------------------------
async def get_banner_by_type(banner_type: int):
    query = """
        SELECT b.*, g.image_id AS gallery_image
        FROM banner b
        LEFT JOIN gallery g ON b.image_id = g.id
        WHERE b.status = 1 AND b.type = %s
        ORDER BY b.updated_at DESC
        LIMIT 1
    """
    return await execute_query(query, (banner_type,), fetchone=True)


# ---------------------------------------------------------------------
# 🔹 Create a new banner
# ---------------------------------------------------------------------
async def create_banner(data: dict):
    now = datetime.datetime.utcnow()

    # Validate user_id exists
    user_check = await execute_query("SELECT id FROM users WHERE id = %s", (data.get("user_id"),), fetchone=True)
    if not user_check:
        raise ValueError("user_id not found")

    query = """
        INSERT INTO banner (image_id, path, user_id, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (
                data.get("image_id"),
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                now,
                now,
            ))
            await conn.commit()
            banner_id = cursor.lastrowid
    finally:
        conn.close()

    return {"id": banner_id, **data}


# ---------------------------------------------------------------------
# 🔹 Update an existing banner
# ---------------------------------------------------------------------
async def update_banner(banner_id: int, data: dict):
    existing = await execute_query("SELECT created_at FROM banner WHERE id = %s", (banner_id,), fetchone=True)
    if not existing:
        return {"error": "Banner not found"}

    updated_at = datetime.datetime.utcnow()

    query = """
        UPDATE banner
        SET image_id = %s, title = %s, path = %s, user_id = %s,
            status = %s, created_at = %s, updated_at = %s
        WHERE id = %s
    """

    await execute_query(query, (
        data.get("image_id"),
        data.get("title"),
        data.get("path"),
        data.get("user_id"),
        data.get("status", 1),
        existing["created_at"],
        updated_at,
        banner_id,
    ), commit=True)

    return {
        "id": banner_id,
        **data,
        "created_at": existing["created_at"],
        "updated_at": updated_at,
    }


# ---------------------------------------------------------------------
# 🔹 Soft delete a banner
# ---------------------------------------------------------------------
async def delete_banner(banner_id: int):
    query = "UPDATE banner SET status = 0 WHERE id = %s"
    await execute_query(query, (banner_id,), commit=True)
    return {"message": f"Banner {banner_id} soft-deleted (status = 0)"}


# ---------------------------------------------------------------------
# 🔹 Set banner type
# ---------------------------------------------------------------------
async def set_banner_type(banner_id: int, banner_type: str):
    query = "UPDATE banner SET type = %s WHERE id = %s"
    await execute_query(query, (banner_type, banner_id), commit=True)
    return {"message": f"Banner {banner_id} type set to {banner_type}"}
