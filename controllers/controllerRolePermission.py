import datetime
from db import get_db_connection  # returns aiomysql connection
import aiomysql


async def assign_permissions_to_user(user_id: int, permission_ids: list):
    if not permission_ids:
        return {"error": "No permission_ids provided"}

    conn = await get_db_connection()  # directly a Connection
    cursor = await conn.cursor(aiomysql.DictCursor)

    try:
        # Get existing role_permission IDs
        format_strings = ",".join(["%s"] * len(permission_ids))
        await cursor.execute(
            f"SELECT id, permission_id FROM role_permission WHERE permission_id IN ({format_strings})",
            tuple(permission_ids)
        )
        role_permission_rows = await cursor.fetchall()
        if not role_permission_rows:
            return {"error": "No matching role_permission found"}

        role_permission_map = {row["permission_id"]: row["id"] for row in role_permission_rows}
        role_permission_ids = list(role_permission_map.values())

        # Get already assigned permissions
        await cursor.execute(
            "SELECT permission_id FROM user_permission WHERE user_id=%s AND status=1",
            (user_id,)
        )
        existing_rows = await cursor.fetchall()
        existing = {row["permission_id"] for row in existing_rows}

        now = datetime.datetime.utcnow()
        assigned = []

        for perm_id in permission_ids:
            rp_id = role_permission_map.get(perm_id)
            if rp_id and perm_id not in existing:
                await cursor.execute(
                    "INSERT INTO user_permission (user_id, permission_id, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, rp_id, 1, now, now)
                )
                assigned.append(rp_id)

        skipped = [role_permission_map[pid] for pid in existing if pid in role_permission_map]
        await conn.commit()

    except Exception as e:
        await conn.rollback()
        return {"error": str(e)}
    finally:
        await cursor.close()
        conn.close()  # or await conn.ensure_closed() if needed

    return {"user_id": user_id, "assigned_permission_ids": assigned, "skipped": skipped}
