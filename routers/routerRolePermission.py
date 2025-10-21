from fastapi import APIRouter, Depends, HTTPException, Request
from utils.jwt_handler import get_current_user
from db import get_db_connection

router = APIRouter(prefix="/api/role-permissions", tags=["role_permissions"])

# Permission checker
def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker


@router.put("/assign/{user_id}")
def assign_permissions_to_user(
    user_id: int, request: Request, user=Depends(require_permission("Update Role Permissions"))
):
    data = request.json() if hasattr(request, "json") else {}
    permission_ids = data.get("permission_id", [])

    if not permission_ids:
        raise HTTPException(status_code=400, detail="permission_id is required")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Remove old permissions
        cursor.execute("DELETE FROM user_permission WHERE user_id=%s", (user_id,))

        # Add new permissions
        for pid in permission_ids:
            cursor.execute(
                "INSERT INTO user_permission (user_id, permission_id) VALUES (%s, %s)",
                (user_id, pid)
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {"user_id": user_id, "assigned_permissions": permission_ids}


@router.get("/user/{user_id}")
def get_user_permissions(user_id: int, user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get all active permissions
        cursor.execute("SELECT id, name FROM permission WHERE status=1")
        all_permissions = cursor.fetchall()

        # Get permissions assigned to this user
        cursor.execute("SELECT permission_id FROM user_permission WHERE user_id=%s", (user_id,))
        assigned_rows = cursor.fetchall()
        assigned_ids = {row["permission_id"] for row in assigned_rows}

        # Add 'assigned' flag
        for perm in all_permissions:
            perm["assigned"] = perm["id"] in assigned_ids

    finally:
        cursor.close()
        conn.close()

    return all_permissions
