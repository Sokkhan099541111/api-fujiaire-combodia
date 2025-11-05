# controllers/controllerPermission.py
import datetime
import aiomysql
from db import get_db_connection


# -------------------------
# Get all permissions
# -------------------------
async def get_all_permissions():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM permission WHERE status = 1")
        permissions = await cursor.fetchall()
    conn.close()
    return {"permissions": permissions}


# -------------------------
# Get permission by ID
# -------------------------
async def get_permission_by_id(permission_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "SELECT * FROM permission WHERE id = %s AND status = 1",
            (permission_id,),
        )
        permission = await cursor.fetchone()
    conn.close()

    if not permission:
        return {"error": "Permission not found"}
    return {"permission": permission}


# -------------------------
# Create permission
# -------------------------
async def create_permission(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        await cursor.execute(
            """
            INSERT INTO permission (name, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data.get("name"),
                data.get("status", 1),
                now,
                now,
            ),
        )
        await conn.commit()
        permission_id = cursor.lastrowid

    conn.close()
    return {
        "message": "Permission created successfully",
        "data": {
            "id": permission_id,
            "name": data.get("name"),
            "status": data.get("status", 1),
            "created_at": now,
            "updated_at": now,
        },
    }


# -------------------------
# Update permission
# -------------------------
async def update_permission(permission_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM permission WHERE id = %s", (permission_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Permission not found"}

        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        await cursor.execute(
            """
            UPDATE permission
            SET name = %s, status = %s, updated_at = %s
            WHERE id = %s
            """,
            (
                data.get("name", row["name"]),
                data.get("status", row["status"]),
                updated_at,
                permission_id,
            ),
        )
        await conn.commit()
    conn.close()

    return {
        "message": "Permission updated successfully",
        "data": {
            "id": permission_id,
            "name": data.get("name", row["name"]),
            "status": data.get("status", row["status"]),
            "created_at": row["created_at"],
            "updated_at": updated_at,
        },
    }


# -------------------------
# Soft delete permission
# -------------------------
async def delete_permission(permission_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT id FROM permission WHERE id = %s", (permission_id,))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "Permission not found"}

        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        await cursor.execute(
            "UPDATE permission SET status = 0, updated_at = %s WHERE id = %s",
            (updated_at, permission_id),
        )
        await conn.commit()
    conn.close()

    return {
        "message": f"Permission {permission_id} soft-deleted successfully",
        "deleted_at": updated_at,
    }
