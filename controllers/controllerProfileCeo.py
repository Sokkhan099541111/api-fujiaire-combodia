import os
import datetime
import aiomysql
from db import get_db_connection


# =====================================
# Build safe image URL (remove duplicate domain)
# =====================================
def build_url(path: str):
    if not path:
        return None

    base = os.getenv("CPANEL_BASE_URL", "").rstrip("/")  # e.g. https://fujiairecambodia.com/uploads

    # Remove double domain if exists
    if path.startswith(base):
        path = path.replace(base + "/", "").replace(base, "")

    path = path.lstrip("/")

    return f"{base}/{path}"


# =====================================
# Helper: auto DB execution
# =====================================
async def exec_query(query, params=None, fetchone=False, fetchall=False, commit=False):
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
        await conn.ensure_closed()


# =====================================
# Get all CEOs (admin)
# =====================================
async def get_all_ceos():
    rows = await exec_query("SELECT * FROM profile_ceo WHERE status = 1", fetchall=True)

    for r in rows:
        r["path"] = build_url(r.get("path"))

    return rows


# =====================================
# Get CEO by ID
# =====================================
async def get_ceo_by_id(ceo_id: int):
    row = await exec_query(
        "SELECT * FROM profile_ceo WHERE id = %s",
        (ceo_id,),
        fetchone=True
    )

    if row:
        row["path"] = build_url(row.get("path"))

    return row


# =====================================
# Create CEO
# =====================================
async def create_ceo(data: dict):
    now = datetime.datetime.utcnow()

    # Check foreign keys exist
    for field, table in [("image_id", "gallery"), ("user_id", "users")]:
        fk = await exec_query(f"SELECT id FROM {table} WHERE id=%s", (data.get(field),), fetchone=True)
        if not fk:
            return {"error": f"{field} not found"}

    query = """
        INSERT INTO profile_ceo
        (image_id, path, name, detail, user_id, status,
         testimonial, testimonialTitle, testimonialDescriptions,
         created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
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
    )

    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, values)
            await conn.commit()
            ceo_id = cursor.lastrowid
    except Exception as e:
        await conn.rollback()
        return {"error": str(e)}
    finally:
        await conn.ensure_closed()

    data["path"] = build_url(data.get("path"))

    return {"id": ceo_id, **data, "created_at": now, "updated_at": now}


# =====================================
# Update CEO
# =====================================
async def update_ceo(ceo_id: int, data: dict):
    existing = await exec_query(
        "SELECT created_at FROM profile_ceo WHERE id = %s",
        (ceo_id,),
        fetchone=True
    )

    if not existing:
        return {"error": "CEO profile not found"}

    created_at = existing["created_at"]
    updated_at = datetime.datetime.utcnow()

    query = """
        UPDATE profile_ceo
        SET image_id=%s, path=%s, name=%s, detail=%s, user_id=%s, status=%s,
            testimonial=%s, testimonialTitle=%s, testimonialDescriptions=%s,
            created_at=%s, updated_at=%s
        WHERE id=%s
    """

    values = (
        data.get("image_id"),
        data.get("path"),
        data.get("name"),
        data.get("detail"),
        data.get("user_id"),
        data.get("status", 1),
        data.get("testimonial"),
        data.get("testimonialTitle"),
        data.get("testimonialDescriptions"),
        created_at,
        updated_at,
        ceo_id
    )

    await exec_query(query, values, commit=True)

    data["path"] = build_url(data.get("path"))

    return {"id": ceo_id, **data, "created_at": created_at, "updated_at": updated_at}


# =====================================
# Soft delete CEO
# =====================================
async def delete_ceo(ceo_id: int):
    await exec_query(
        "UPDATE profile_ceo SET status=0, updated_at=%s WHERE id=%s",
        (datetime.datetime.utcnow(), ceo_id),
        commit=True
    )
    return {"message": f"Profile CEO {ceo_id} soft-deleted (status = 0)"}


# =====================================
# Get all CEOs (public)
# =====================================
async def get_all_ceos_public():
    rows = await exec_query(
        "SELECT * FROM profile_ceo WHERE status = 1",
        fetchall=True
    )
    for r in rows:
        r["path"] = build_url(r.get("path"))
    return rows


# =====================================
# Get CEO testimonial list
# =====================================
async def get_testimonial_public(type_id: int):
    rows = await exec_query(
        "SELECT * FROM profile_ceo WHERE publisher = %s AND status = 1",
        (type_id,),
        fetchall=True
    )

    for r in rows:
        r["path"] = build_url(r.get("path"))

    return rows


# =====================================
# Update CEO publisher / testimonial type
# =====================================
async def set_testimonial(ceo_id: int, data: dict):
    updated_at = datetime.datetime.utcnow()

    query = """
        UPDATE profile_ceo
        SET publisher=%s, updated_at=%s
        WHERE id=%s
    """

    values = (data.get("publisher"), updated_at, ceo_id)

    await exec_query(query, values, commit=True)

    return {"message": f"CEO {ceo_id} testimonial publisher updated", "publisher": data.get("publisher")}
