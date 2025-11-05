from fastapi import APIRouter, Depends, HTTPException, Request
from utils.jwt_handler import get_current_user
from db import get_db_connection

router = APIRouter(prefix="/api/role-permissions", tags=["Role Permissions"])


# ----------------------------
# Helper: Permission Checker
# ----------------------------
def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker


# ----------------------------
# ASSIGN PERMISSIONS TO USER
# ----------------------------
@router.put("/assign/{user_id}")
async def assign_permissions_to_user(
    user_id: int,
    request: Request,
    user=Depends(require_permission("Update Role Permissions"))
):
    data = await request.json()
    permission_ids = data.get("permission_id", [])

    if not permission_ids:
        raise HTTPException(status_code=400, detail="permission_id is required")

    db = await get_db_connection()
    conn_is_pool = hasattr(db, "acquire")

    try:
        if conn_is_pool:
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Remove old permissions
                    await cursor.execute("DELETE FROM user_permission WHERE user_id=%s", (user_id,))
                    # Add new permissions
                    for pid in permission_ids:
                        await cursor.execute(
                            "INSERT INTO user_permission (user_id, permission_id) VALUES (%s, %s)",
                            (user_id, pid),
                        )
                    await conn.commit()
        else:
            async with db.cursor() as cursor:
                await cursor.execute("DELETE FROM user_permission WHERE user_id=%s", (user_id,))
                for pid in permission_ids:
                    await cursor.execute(
                        "INSERT INTO user_permission (user_id, permission_id) VALUES (%s, %s)",
                        (user_id, pid),
                    )
                await db.commit()

        return {"user_id": user_id, "assigned_permissions": permission_ids}

    except Exception as e:
        if db:
            await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if db and not conn_is_pool:
            db.close()


# ----------------------------
# GET USER PERMISSIONS
# ----------------------------
@router.get("/user/{user_id}")
async def get_user_permissions(user_id: int, user=Depends(get_current_user)):
    try:
        db = await get_db_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection error: {e}")

    conn_is_pool = hasattr(db, "acquire")
    result = []

    try:
        if conn_is_pool:
            # ---------- For pooled connection ----------
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    # 1. Fetch all permissions
                    await cursor.execute("SELECT id, name FROM permission WHERE status=1")
                    all_permissions = await cursor.fetchall()

                    # 2. Fetch assigned permissions
                    await cursor.execute(
                        "SELECT permission_id FROM user_permission WHERE user_id=%s",
                        (user_id,),
                    )
                    assigned_rows = await cursor.fetchall()
        else:
            # ---------- For single async connection ----------
            async with db.cursor() as cursor:
                await cursor.execute("SELECT id, name FROM permission WHERE status=1")
                all_permissions = await cursor.fetchall()

                await cursor.execute(
                    "SELECT permission_id FROM user_permission WHERE user_id=%s",
                    (user_id,),
                )
                assigned_rows = await cursor.fetchall()

        # ✅ Convert results to dicts if not already
        def to_dict_list(rows, columns):
            return [dict(zip(columns, row)) for row in rows]

        if all_permissions and not isinstance(all_permissions[0], dict):
            cols = ["id", "name"]
            all_permissions = to_dict_list(all_permissions, cols)

        if assigned_rows and not isinstance(assigned_rows[0], dict):
            assigned_rows = to_dict_list(assigned_rows, ["permission_id"])

        # ✅ Mark assigned permissions
        assigned_ids = {row["permission_id"] for row in assigned_rows}
        for perm in all_permissions:
            perm["assigned"] = perm["id"] in assigned_ids

        result = all_permissions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {e}")

    finally:
        # ✅ Ensure cleanup if not pooled
        if db and not conn_is_pool:
            await db.ensure_closed() if hasattr(db, "ensure_closed") else db.close()

    return {"permissions": result}
