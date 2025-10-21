import datetime
import aiomysql
from db import get_db_connection  # should return aiomysql connection


# ===============================
# Get all roles (active)
# ===============================
async def get_all_roles():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM role WHERE status = 1")
        rows = await cursor.fetchall()
    await conn.ensure_closed()
    return rows


# ===============================
# Get role by ID
# ===============================
async def get_role_by_id(role_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM role WHERE id = %s", (role_id,))
        row = await cursor.fetchone()
    await conn.ensure_closed()
    return row


# ===============================
# Create role
# ===============================
async def create_role(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Check if name exists
        await cursor.execute("SELECT * FROM role WHERE name = %s AND status = 1", (data.get("name"),))
        if await cursor.fetchone():
            await conn.ensure_closed()
            return {"error": "Role name already exists"}

        now = datetime.datetime.utcnow()
        await cursor.execute("""
            INSERT INTO role (name, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
        """, (data.get("name"), data.get("status", 1), now, now))
        role_id = cursor.lastrowid
        await conn.commit()
    await conn.ensure_closed()
    return {"id": role_id, **data, "created_at": now, "updated_at": now}


# ===============================
# Update role
# ===============================
async def update_role(role_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Prevent duplicate name
        await cursor.execute("SELECT * FROM role WHERE name = %s AND id != %s AND status = 1", (data.get("name"), role_id))
        if await cursor.fetchone():
            await conn.ensure_closed()
            return {"error": "Role name already exists"}

        # Fetch existing created_at
        await cursor.execute("SELECT created_at FROM role WHERE id = %s", (role_id,))
        row = await cursor.fetchone()
        if not row:
            await conn.ensure_closed()
            return {"error": "Role not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.utcnow()

        # Update role
        await cursor.execute("""
            UPDATE role 
            SET name = %s, status = %s, created_at = %s, updated_at = %s 
            WHERE id = %s
        """, (data.get("name"), data.get("status", 1), created_at, updated_at, role_id))
        await conn.commit()
    await conn.ensure_closed()

    return {"id": role_id, "name": data.get("name"), "status": data.get("status", 1),
            "created_at": created_at, "updated_at": updated_at}


# ===============================
# Soft delete role
# ===============================
async def delete_role(role_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Soft delete (status = 0)
        await cursor.execute("UPDATE role SET status = 0, updated_at = %s WHERE id = %s",
                             (datetime.datetime.utcnow(), role_id))
        await conn.commit()
    await conn.ensure_closed()
    return {"message": f"Role {role_id} deleted successfully!"}
