import datetime
import aiomysql
from db import get_db_connection   # returns aiomysql.Connection or a pool


# Detect if connection is a pool
def is_pool(conn):
    return hasattr(conn, "acquire")


# ============================================================
# GET ALL INDUSTRIES (admin)
# ============================================================
async def get_all_industries():
    conn = await get_db_connection()
    try:
        if is_pool(conn):
            async with conn.acquire() as db:
                async with db.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute("SELECT * FROM industry_development ORDER BY id DESC")
                    return await cursor.fetchall()
        else:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM industry_development ORDER BY id DESC")
                return await cursor.fetchall()
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
                    return await cursor.fetchone()
        else:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (industry_id,))
                return await cursor.fetchone()
    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# CREATE INDUSTRY
# ============================================================
async def create_industry(data: dict):
    conn = await get_db_connection()
    now = datetime.datetime.now()
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
                        data.get("path"),
                        data.get("user_id"),
                        data.get("status", 1),
                        now,
                        now
                    ))
                    await db.commit()
                    return {"id": cursor.lastrowid, **data}

        # Normal MySQL connection
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
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                now,
                now
            ))
            await conn.commit()
            return {"id": cursor.lastrowid, **data}

    finally:
        if conn and not is_pool(conn):
            conn.close()


# ============================================================
# UPDATE INDUSTRY
# ============================================================
async def update_industry(industry_id: int, data: dict):
    conn = await get_db_connection()
    now = datetime.datetime.now()

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
                        SET year=%s, title=%s, image_id=%s, path=%s, user_id=%s,
                            status=%s, created_at=%s, updated_at=%s
                        WHERE id=%s
                    """, (
                        data.get("year"),
                        data.get("title"),
                        data.get("image_id"),
                        data.get("path"),
                        data.get("user_id"),
                        data.get("status", 1),
                        created_at,
                        now,
                        industry_id
                    ))
                    await db.commit()

                    return {
                        "id": industry_id,
                        **data,
                        "created_at": created_at,
                        "updated_at": now
                    }

        # Normal MySQL connection
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT created_at FROM industry_development WHERE id=%s", (industry_id,))
            row = await cursor.fetchone()
            if not row:
                return {"error": "Industry development not found"}

            created_at = row["created_at"]

            await cursor.execute("""
                UPDATE industry_development
                SET year=%s, title=%s, image_id=%s, path=%s, user_id=%s,
                    status=%s, created_at=%s, updated_at=%s
                WHERE id=%s
            """, (
                data.get("year"),
                data.get("title"),
                data.get("image_id"),
                data.get("path"),
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
                    return {"message": f"Industry development {industry_id} deleted"}

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
                    return await cursor.fetchall()

        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            return await cursor.fetchall()

    finally:
        if conn and not is_pool(conn):
            conn.close()
