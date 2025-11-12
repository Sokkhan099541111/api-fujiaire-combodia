import datetime
import aiomysql
from db import get_db_connection  # should return aiomysql connection


# ===============================
# Get all CEOs (admin)
# ===============================
async def get_all_ceos():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM profile_ceo WHERE status = 1")
        rows = await cursor.fetchall()
    await conn.ensure_closed()
    return rows


# ===============================
# Get CEO by ID
# ===============================
async def get_ceo_by_id(ceo_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM profile_ceo WHERE id = %s", (ceo_id,))
        row = await cursor.fetchone()
    await conn.ensure_closed()
    return row


# ===============================
# Create CEO
# ===============================
async def create_ceo(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            # Check foreign keys
            for field, table in [("image_id", "gallery"), ("user_id", "users")]:
                await cursor.execute(f"SELECT id FROM {table} WHERE id = %s", (data.get(field),))
                if not await cursor.fetchone():
                    return {"error": f"{field} not found"}

            now = datetime.datetime.utcnow()
            await cursor.execute("""
                INSERT INTO profile_ceo (image_id, path, name, detail, user_id,  status, testimonial, testimonialTitle, testimonialDescriptions, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("image_id"),
                data.get("path"),
                data.get("name"),
                data.get("detail"),
                data.get("user_id"),
                data.get("status", 1),
                data.get("testimonial"),
                data.get("testimonialTitle"),
                data.get("testimonialDescriptions"),
                now,
                now
            ))
            ceo_id = cursor.lastrowid
            await conn.commit()
            return {"id": ceo_id, **data, "created_at": now, "updated_at": now}

        except Exception as e:
            await conn.rollback()
            return {"error": str(e)}

        finally:
            await conn.ensure_closed()


# ===============================
# Update CEO
# ===============================
async def update_ceo(ceo_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT created_at FROM profile_ceo WHERE id = %s", (ceo_id,))
            row = await cursor.fetchone()
            if not row:
                return {"error": "CEO profile not found"}

            created_at = row["created_at"]
            updated_at = datetime.datetime.utcnow()

            await cursor.execute("""
                UPDATE profile_ceo SET image_id=%s, path=%s, name=%s, detail=%s, user_id=%s, status=%s, testimonial = %s, testimonialTitle = %s, testimonialDescriptions = %s, created_at=%s, updated_at=%s
                WHERE id=%s
            """, (
                data.get("image_id"),
                data.get("path"),
                data.get("name"),
                data.get("detail"),
                data.get("user_id"),
                data.get("status", 1),
                created_at,
                updated_at,
                ceo_id
            ))
            await conn.commit()
            return {"id": ceo_id, **data, "created_at": created_at, "updated_at": updated_at}

        except Exception as e:
            await conn.rollback()
            return {"error": str(e)}

        finally:
            await conn.ensure_closed()


# ===============================
# Soft delete CEO
# ===============================
async def delete_ceo(ceo_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("UPDATE profile_ceo SET status=0, updated_at=%s WHERE id=%s", (datetime.datetime.utcnow(), ceo_id))
        await conn.commit()
    await conn.ensure_closed()
    return {"message": f"Profile CEO {ceo_id} soft-deleted (status = 0)"}


# ===============================
# Get all CEOs (public)
# ===============================
async def get_all_ceos_public():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM profile_ceo WHERE status = 1")
        rows = await cursor.fetchall()
    await conn.ensure_closed()
    return rows


# ===============================
# Get CEOs by type (public)
# ===============================
async def get_testimonial_public(type_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM profile_ceo WHERE publisher = %s AND status = 1", (type_id,))
        rows = await cursor.fetchall()
    await conn.ensure_closed()
    return rows

# ===============================
# Set testimonial for CEO
# ===============================   

async def set_testimonial(publisher: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("""
                UPDATE profile_ceo SET publisher=%s,
                WHERE id=%s
            """, (
                data.get("publisher"),
                datetime.datetime.utcnow(),
                publisher
            ))
            await conn.commit()
            return {"message": f"{publisher}"}

        except Exception as e:
            await conn.rollback()
            return {"error": str(e)}

        finally:
            await conn.ensure_closed()