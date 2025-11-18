import os
import datetime
import aiomysql
from db import get_db_connection

# Base URL to your cPanel uploads folder (adjust if needed)
CPANEL_BASE = os.getenv("CPANEL_BASE_URL", "https://fujiairecambodia.com/uploads").rstrip("/")

def clean_cpanel_path(path: str):
    if not path:
        return None
    # Remove duplicate base URL if accidentally stored
    return path.replace(CPANEL_BASE + "/", "").replace(CPANEL_BASE, "").lstrip("/")

def build_url(path: str):
    if not path:
        return None
    clean_path = clean_cpanel_path(path)
    return f"{CPANEL_BASE}/{clean_path}"


# ==========================================
# Get all welcome entries (admin)
# ==========================================
async def get_all_welcome():
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM welcome ORDER BY id DESC")
            rows = await cursor.fetchall()
            # Fix image URLs
            for r in rows:
                r["path"] = build_url(r.get("path"))
            return rows
    finally:
        conn.close()


# ==========================================
# Get welcome entry by ID
# ==========================================
async def get_welcome_by_id(welcome_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE id = %s", (welcome_id,))
            row = await cursor.fetchone()
            if row:
                row["path"] = build_url(row.get("path"))
            return row
    finally:
        conn.close()


# ==========================================
# Create welcome entry
# ==========================================
async def create_welcome(data: dict):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            # Validate FK: image_id
            await cursor.execute("SELECT id FROM gallery WHERE id = %s", (data.get("image_id"),))
            if not await cursor.fetchone():
                return {"error": "image_id not found"}

            # Validate FK: banner_id
            await cursor.execute("SELECT id FROM banner WHERE id = %s", (data.get("banner_id"),))
            if not await cursor.fetchone():
                return {"error": "banner_id not found"}

            # Validate FK: user_id
            await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
            if not await cursor.fetchone():
                return {"error": "user_id not found"}

            now = datetime.datetime.now()

            # Clean path before insert
            path_cleaned = clean_cpanel_path(data.get("path"))

            await cursor.execute("""
                INSERT INTO welcome
                    (title, detail, image_id, path, banner_id, user_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("title"),
                data.get("detail"),
                data.get("image_id"),
                path_cleaned,
                data.get("banner_id"),
                data.get("user_id"),
                data.get("status", 1),
                now,
                now
            ))

            await conn.commit()
            welcome_id = cursor.lastrowid

            return {
                "id": welcome_id,
                **data,
                "path": build_url(path_cleaned),
                "created_at": now,
                "updated_at": now
            }

    finally:
        conn.close()


# ==========================================
# Update welcome entry
# ==========================================
async def update_welcome(welcome_id: int, data: dict):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            # Get created_at
            await cursor.execute("SELECT created_at FROM welcome WHERE id = %s", (welcome_id,))
            row = await cursor.fetchone()
            if not row:
                return {"error": "Welcome entry not found"}

            created_at = row["created_at"]
            updated_at = datetime.datetime.now()

            # Validate FK: image_id
            await cursor.execute("SELECT id FROM gallery WHERE id = %s", (data.get("image_id"),))
            if not await cursor.fetchone():
                return {"error": "image_id not found"}

            # Validate FK: banner_id
            await cursor.execute("SELECT id FROM banner WHERE id = %s", (data.get("banner_id"),))
            if not await cursor.fetchone():
                return {"error": "banner_id not found"}

            # Validate FK: user_id
            await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
            if not await cursor.fetchone():
                return {"error": "user_id not found"}

            path_cleaned = clean_cpanel_path(data.get("path"))

            await cursor.execute("""
                UPDATE welcome SET
                    title = %s,
                    detail = %s,
                    image_id = %s,
                    path = %s,
                    banner_id = %s,
                    user_id = %s,
                    status = %s,
                    created_at = %s,
                    updated_at = %s
                WHERE id = %s
            """, (
                data.get("title"),
                data.get("detail"),
                data.get("image_id"),
                path_cleaned,
                data.get("banner_id"),
                data.get("user_id"),
                data.get("status", 1),
                created_at,
                updated_at,
                welcome_id
            ))

            await conn.commit()

            return {
                "id": welcome_id,
                **data,
                "path": build_url(path_cleaned),
                "created_at": created_at,
                "updated_at": updated_at
            }

    finally:
        conn.close()


# ==========================================
# Soft delete welcome
# ==========================================
async def delete_welcome(welcome_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE welcome SET status = 0 WHERE id = %s", (welcome_id,))
            await conn.commit()
            return {"message": f"Welcome {welcome_id} soft-deleted"}
    finally:
        conn.close()


# ==========================================
# Public list (status = 1)
# ==========================================
async def get_all_welcome_public():
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE status = 1 ORDER BY id DESC")
            rows = await cursor.fetchall()
            for r in rows:
                r["path"] = build_url(r.get("path"))
            return rows
    finally:
        conn.close()
