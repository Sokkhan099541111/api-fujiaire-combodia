import datetime
import aiomysql
from db import get_db_connection  # returns connection pool


async def get_all_permissions():
    pool = await get_db_connection()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM permission WHERE status = 1")
            rows = await cursor.fetchall()
    return rows


async def get_permission_by_id(permission_id: int):
    pool = await get_db_connection()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM permission WHERE id = %s AND status = 1",
                (permission_id,)
            )
            row = await cursor.fetchone()
    if not row:
        return {"error": "Permission not found"}
    return row


async def create_permission(data: dict):
    pool = await get_db_connection()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            now = datetime.datetime.now()
            await cursor.execute("""
                INSERT INTO permission (name, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """, (
                data.get("name"),
                data.get("status", 1),
                now,
                now
            ))
            await conn.commit()
            permission_id = cursor.lastrowid

    return {
        "id": permission_id,
        "name": data.get("name"),
        "status": data.get("status", 1),
        "created_at": now,
        "updated_at": now
    }


async def update_permission(permission_id: int, data: dict):
    pool = await get_db_connection()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM permission WHERE id = %s", (permission_id,))
            row = await cursor.fetchone()
            if not row:
                return {"error": "Permission not found"}

            updated_at = datetime.datetime.now()
            await cursor.execute("""
                UPDATE permission
                SET name = %s, status = %s, updated_at = %s
                WHERE id = %s
            """, (
                data.get("name", row["name"]),
                data.get("status", row["status"]),
                updated_at,
                permission_id
            ))
            await conn.commit()

    return {
        "id": permission_id,
        "name": data.get("name", row["name"]),
        "status": data.get("status", row["status"]),
        "created_at": row["created_at"],
        "updated_at": updated_at
    }


async def delete_permission(permission_id: int):
    pool = await get_db_connection()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT id FROM permission WHERE id = %s", (permission_id,))
            if not await cursor.fetchone():
                return {"error": "Permission not found"}

            await cursor.execute(
                "UPDATE permission SET status = 0, updated_at = %s WHERE id = %s",
                (datetime.datetime.now(), permission_id)
            )
            await conn.commit()

    return {"message": f"Permission {permission_id} soft-deleted successfully"}
