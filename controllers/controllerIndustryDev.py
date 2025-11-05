import datetime
from db import get_db_connection  # async connection

# -------------------------
# Fetch all industries
# -------------------------
async def get_all_industries():
    conn = await get_db_connection()
    conn_is_pool = hasattr(conn, "acquire")
    try:
        if conn_is_pool:
            async with conn.acquire() as connection:
                async with connection.cursor(dictionary=True) as cursor:
                    await cursor.execute("SELECT * FROM industry_development")
                    rows = await cursor.fetchall()
                    return rows
        else:
            async with conn.cursor(dictionary=True) as cursor:
                await cursor.execute("SELECT * FROM industry_development")
                rows = await cursor.fetchall()
                return rows
    finally:
        if conn and not conn_is_pool:
            conn.close()

# -------------------------
# Fetch industry by ID
# -------------------------
async def get_industry_by_id(industry_id: int):
    conn = await get_db_connection()
    conn_is_pool = hasattr(conn, "acquire")
    try:
        query = "SELECT * FROM industry_development WHERE id=%s"
        if conn_is_pool:
            async with conn.acquire() as connection:
                async with connection.cursor(dictionary=True) as cursor:
                    await cursor.execute(query, (industry_id,))
                    row = await cursor.fetchone()
                    return row
        else:
            async with conn.cursor(dictionary=True) as cursor:
                await cursor.execute(query, (industry_id,))
                row = await cursor.fetchone()
                return row
    finally:
        if conn and not conn_is_pool:
            conn.close()

# -------------------------
# Create industry
# -------------------------
async def create_industry(data: dict):
    conn = await get_db_connection()
    conn_is_pool = hasattr(conn, "acquire")
    now = datetime.datetime.now()
    try:
        if conn_is_pool:
            async with conn.acquire() as connection:
                async with connection.cursor() as cursor:
                    # Check FK image_id
                    await cursor.execute("SELECT id FROM gallery WHERE id=%s", (data.get("image_id"),))
                    if not await cursor.fetchone():
                        return {"error": "image_id not found"}

                    # Check FK user_id
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
                    await connection.commit()
                    industry_id = cursor.lastrowid
                    return {"id": industry_id, **data}
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
                    data.get("path"),
                    data.get("user_id"),
                    data.get("status", 1),
                    now,
                    now
                ))
                await conn.commit()
                industry_id = cursor.lastrowid
                return {"id": industry_id, **data}
    finally:
        if conn and not conn_is_pool:
            conn.close()

# -------------------------
# Update industry
# -------------------------
async def update_industry(industry_id: int, data: dict):
    conn = await get_db_connection()
    conn_is_pool = hasattr(conn, "acquire")
    now = datetime.datetime.now()
    try:
        if conn_is_pool:
            async with conn.acquire() as connection:
                async with connection.cursor(dictionary=True) as cursor:
                    await cursor.execute("SELECT created_at FROM industry_development WHERE id=%s", (industry_id,))
                    row = await cursor.fetchone()
                    if not row:
                        return {"error": "Industry development not found"}
                    created_at = row["created_at"]

                    await cursor.execute("""
                        UPDATE industry_development
                        SET year=%s, title=%s, image_id=%s, path=%s, user_id=%s, status=%s,
                            created_at=%s, updated_at=%s
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
                    await connection.commit()
                    return {"id": industry_id, **data, "created_at": created_at, "updated_at": now}
        else:
            async with conn.cursor(dictionary=True) as cursor:
                await cursor.execute("SELECT created_at FROM industry_development WHERE id=%s", (industry_id,))
                row = await cursor.fetchone()
                if not row:
                    return {"error": "Industry development not found"}
                created_at = row["created_at"]

                await cursor.execute("""
                    UPDATE industry_development
                    SET year=%s, title=%s, image_id=%s, path=%s, user_id=%s, status=%s,
                        created_at=%s, updated_at=%s
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
                return {"id": industry_id, **data, "created_at": created_at, "updated_at": now}
    finally:
        if conn and not conn_is_pool:
            conn.close()

# -------------------------
# Soft delete industry
# -------------------------
async def delete_industry(industry_id: int):
    conn = await get_db_connection()
    conn_is_pool = hasattr(conn, "acquire")
    try:
        if conn_is_pool:
            async with conn.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("UPDATE industry_development SET status=0 WHERE id=%s", (industry_id,))
                    await connection.commit()
                    return {"message": f"Industry development {industry_id} soft-deleted"}
        else:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE industry_development SET status=0 WHERE id=%s", (industry_id,))
                await conn.commit()
                return {"message": f"Industry development {industry_id} soft-deleted"}
    finally:
        if conn and not conn_is_pool:
            conn.close()

# -------------------------
# Public fetch all industries
# -------------------------
async def get_all_industries_public():
    conn = await get_db_connection()
    conn_is_pool = hasattr(conn, "acquire")
    try:
        if conn_is_pool:
            async with conn.acquire() as connection:
                async with connection.cursor(dictionary=True) as cursor:
                    await cursor.execute("SELECT * FROM industry_development WHERE status=1")
                    rows = await cursor.fetchall()
                    return rows
        else:
            async with conn.cursor(dictionary=True) as cursor:
                await cursor.execute("SELECT * FROM industry_development WHERE status=1")
                rows = await cursor.fetchall()
                return rows
    finally:
        if conn and not conn_is_pool:
            conn.close()
