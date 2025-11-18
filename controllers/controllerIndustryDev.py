import os
import datetime
import aiomysql
from db import get_db_connection


# ============================================================
# URL HELPERS
# ============================================================

CPANEL_BASE = os.getenv("CPANEL_BASE_URL", "https://fujiairecambodia.com/uploads").rstrip("/")


def clean_cpanel_path(path: str):
    """Remove duplicate base URL if included in DB."""
    if not path:
        return None
    return path.replace(CPANEL_BASE + "/", "").replace(CPANEL_BASE, "").lstrip("/")


def build_url(path: str):
    """Convert DB path to full URL."""
    if not path:
        return None
    clean = clean_cpanel_path(path)
    return f"{CPANEL_BASE}/{clean}"


# Detect if connection is a pool
def is_pool(conn):
    return hasattr(conn, "acquire")


# ============================================================
# GET ALL INDUSTRIES (ADMIN)
# ============================================================
async def get_all_industries():
    conn = await get_db_connection()
    try:
        query = "SELECT * FROM industry_development ORDER BY id DESC"

        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
        else:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                rows = await cursor.fetchall()

        # Fix image paths
        for r in rows:
            r["path"] = build_url(r.get("path"))

        return rows

    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# GET INDUSTRY BY ID
# ============================================================
async def get_industry_by_id(industry_id: int):
    conn = await get_db_connection()
    try:
        query = "SELECT * FROM industry_development WHERE id=%s"

        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, (industry_id,))
                    row = await cursor.fetchone()
        else:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (industry_id,))
                row = await cursor.fetchone()

        if row:
            row["path"] = build_url(row.get("path"))

        return row

    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# CREATE INDUSTRY
# ============================================================
async def create_industry(data: dict):
    conn = await get_db_connection()
    now = datetime.datetime.now()

    path_cleaned = clean_cpanel_path(data.get("path"))

    try:
        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor() as cursor:

                    # FK checks
                    await cursor.execute("SELECT id FROM gallery WHERE id=%s", (data.get("image_id"),))
                    if not await cursor.fetchone():
                        return {"error": "image_id not found"}

                    await cursor.execute("SELECT id FROM users WHERE id=%s", (data.get("user_id"),))
                    if not await cursor.fetchone():
                        return {"error": "user_id not found"}

                    await cursor.execute("""
                        INSERT INTO industry_development
                            (year, title, image_id, path, user_id, status, created_at, updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        data.get("year"),
                        data.get("title"),
                        data.get("image_id"),
                        path_cleaned,
                        data.get("user_id"),
                        data.get("status", 1),
                        now,
                        now
                    ))
                    await db.commit()

                    new_id = cursor.lastrowid

        else:
            async with conn.cursor() as cursor:

                await cursor.execute("SELECT id FROM gallery WHERE id=%s", (data.get("image_id"),))
                if not await cursor.fetchone():
                    return {"error": "image_id not found"}

                await cursor.execute("SELECT id FROM users WHERE id=%s", (data.get("user_id"),))
                if not await cursor.fetchone():
                    return {"error": "user_id not found"}

                await cursor.execute("""
                    INSERT INTO industry_development
                        (year, title, image_id, path, user_id, status, created_at, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    data.get("year"),
                    data.get("title"),
                    data.get("image_id"),
                    path_cleaned,
                    data.get("user_id"),
                    data.get("status", 1),
                    now,
                    now
                ))
                await conn.commit()

                new_id = cursor.lastrowid

        return {
            "id": new_id,
            **data,
            "path": build_url(path_cleaned),
            "created_at": now,
            "updated_at": now
        }

    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# UPDATE INDUSTRY
# ============================================================
async def update_industry(industry_id: int, data: dict):
    conn = await get_db_connection()
    now = datetime.datetime.now()

    new_path = clean_cpanel_path(data.get("path"))

    try:
        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor(aiomysql.DictCursor) as cursor:

                    await cursor.execute("SELECT created_at FROM industry_development WHERE id=%s", (industry_id,))
                    row = await cursor.fetchone()
                    if not row:
                        return {"error": "Industry development not found"}

                    created_at = row["created_at"]

                    await cursor.execute("""
                        UPDATE industry_development
                        SET year=%s, title=%s, image_id=%s, path=%s,
                            user_id=%s, status=%s, created_at=%s, updated_at=%s
                        WHERE id=%s
                    """, (
                        data.get("year"),
                        data.get("title"),
                        data.get("image_id"),
                        new_path,
                        data.get("user_id"),
                        data.get("status", 1),
                        created_at,
                        now,
                        industry_id
                    ))
                    await db.commit()

        else:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                await cursor.execute("SELECT created_at FROM industry_development WHERE id=%s", (industry_id,))
                row = await cursor.fetchone()
                if not row:
                    return {"error": "Industry development not found"}

                created_at = row["created_at"]

                await cursor.execute("""
                    UPDATE industry_development
                    SET year=%s, title=%s, image_id=%s, path=%s,
                        user_id=%s, status=%s, created_at=%s, updated_at=%s
                    WHERE id=%s
                """, (
                    data.get("year"),
                    data.get("title"),
                    data.get("image_id"),
                    new_path,
                    data.get("user_id"),
                    data.get("status", 1),
                    created_at,
                    now,
                    industry_id
                ))
                await conn.commit()

        return {
            "id": industry_id,
            **data,
            "path": build_url(new_path),
            "created_at": created_at,
            "updated_at": now
        }

    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# SOFT DELETE
# ============================================================
async def delete_industry(industry_id: int):
    conn = await get_db_connection()
    try:
        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor() as cursor:
                    await cursor.execute("UPDATE industry_development SET status=0 WHERE id=%s", (industry_id,))
                    await db.commit()
        else:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE industry_development SET status=0 WHERE id=%s", (industry_id,))
                await conn.commit()

        return {"message": f"Industry development {industry_id} deleted"}

    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# PUBLIC LIST
# ============================================================
async def get_all_industries_public():
    conn = await get_db_connection()
    try:
        query = "SELECT * FROM industry_development WHERE status=1 ORDER BY year DESC"

        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
        else:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                rows = await cursor.fetchall()

        # Convert path to full URL
        for r in rows:
            r["path"] = build_url(r.get("path"))

        return rows

    finally:
        if conn and not is_pool(conn):
            conn.close()
