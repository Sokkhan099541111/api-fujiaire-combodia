import os
import datetime
import aiomysql
from db import get_db_connection

# -----------------------------------------------------------
# 🔹 Fix duplicate URL — correct URL builder
# -----------------------------------------------------------
def build_url(path: str):
    if not path:
        return None

    # Already full URL → return as-is
    if path.startswith("http://") or path.startswith("https://"):
        return path

    base = os.getenv("CPANEL_BASE_URL", "").rstrip("/")
    return f"{base}/{path.lstrip('/')}"


# -----------------------------------------------------------
# 🔹 Helper: run query with auto connection management
# -----------------------------------------------------------
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
        conn.close()


# -----------------------------------------------------------
# 🔹 Get ALL banners (admin)
# -----------------------------------------------------------
async def get_all_banners():
    rows = await execute_query("""
        SELECT b.*, g.path AS gallery_path
        FROM banner b
        LEFT JOIN gallery g ON b.image_id = g.id
    """, fetchall=True)

    for row in rows:
        row["path"] = build_url(row.get("path"))
        row["gallery_path"] = build_url(row.get("gallery_path"))

    return rows


# -----------------------------------------------------------
# 🔹 Get banner by ID
# -----------------------------------------------------------
async def get_banner_by_id(banner_id: int):
    row = await execute_query(
        "SELECT * FROM banner WHERE id = %s",
        (banner_id,), fetchone=True
    )

    if row:
        row["path"] = build_url(row.get("path"))

    return row


# -----------------------------------------------------------
# 🔹 Get banner by type (public home sliders)
# -----------------------------------------------------------
async def get_banner_by_type(banner_type: int):
    row = await execute_query("""
        SELECT b.*, g.path AS gallery_path
        FROM banner b
        LEFT JOIN gallery g ON b.image_id = g.id
        WHERE b.status = 1 AND b.type = %s
        ORDER BY b.updated_at DESC
        LIMIT 1
    """, (banner_type,), fetchone=True)

    if row:
        row["path"] = build_url(row.get("path"))
        row["gallery_path"] = build_url(row.get("gallery_path"))

    return row


# -----------------------------------------------------------
# 🔹 Create banner
# -----------------------------------------------------------
async def create_banner(data: dict):
    now = datetime.datetime.utcnow()

    # Validate user
    user_check = await execute_query(
        "SELECT id FROM users WHERE id = %s",
        (data.get("user_id"),), fetchone=True
    )
    if not user_check:
        raise ValueError("user_id not found")

    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                INSERT INTO banner (image_id, title, path, user_id, status, type, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("image_id"),
                data.get("title"),
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                data.get("type"),
                now,
                now,
            ))

            await conn.commit()
            banner_id = cursor.lastrowid
    finally:
        conn.close()

    # Return clean JSON
    return {
        "id": banner_id,
        **data,
        "path": build_url(data.get("path")),
        "created_at": now,
        "updated_at": now,
    }


# -----------------------------------------------------------
# 🔹 Update banner
# -----------------------------------------------------------
async def update_banner(banner_id: int, data: dict):
    existing = await execute_query(
        "SELECT created_at FROM banner WHERE id = %s",
        (banner_id,), fetchone=True
    )

    if not existing:
        return {"error": "Banner not found"}

    updated_at = datetime.datetime.utcnow()

    await execute_query("""
        UPDATE banner
        SET image_id=%s, title=%s, path=%s, user_id=%s,
            status=%s, type=%s, created_at=%s, updated_at=%s
        WHERE id=%s
    """, (
        data.get("image_id"),
        data.get("title"),
        data.get("path"),
        data.get("user_id"),
        data.get("status", 1),
        data.get("type"),
        existing["created_at"],
        updated_at,
        banner_id,
    ), commit=True)

    return {
        "id": banner_id,
        **data,
        "path": build_url(data.get("path")),
        "created_at": existing["created_at"],
        "updated_at": updated_at,
    }


# -----------------------------------------------------------
# 🔹 Soft delete
# -----------------------------------------------------------
async def delete_banner(banner_id: int):
    await execute_query(
        "UPDATE banner SET status = 0 WHERE id = %s",
        (banner_id,), commit=True
    )
    return {"message": f"Banner {banner_id} soft-deleted"}


# -----------------------------------------------------------
# 🔹 For PUBLIC API (frontend)
# -----------------------------------------------------------
async def get_all_banners_public():
    rows = await execute_query("""
        SELECT b.*, g.path AS gallery_path
        FROM banner b
        LEFT JOIN gallery g ON b.image_id = g.id
        WHERE b.status = 1
    """, fetchall=True)

    for row in rows:
        row["path"] = build_url(row.get("path"))
        row["gallery_path"] = build_url(row.get("gallery_path"))

    return rows
