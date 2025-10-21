from fastapi import APIRouter, Depends, Request, HTTPException
from controllers import controllerRole
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/roles", tags=["Roles"])


def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker


# ===============================
# Get all roles
# ===============================
@router.get("/")
async def get_all(user=Depends(require_permission("Read Roles"))):
    return await controllerRole.get_all_roles()


# ===============================
# Get one role by ID
# ===============================
@router.get("/{role_id}")
async def get_one(role_id: int, user=Depends(require_permission("Read Roles"))):
    role = await controllerRole.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


# ===============================
# Create role
# ===============================
@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Roles"))):
    data = await request.json()
    return await controllerRole.create_role(data)


# ===============================
# Update role
# ===============================
@router.put("/update/{role_id}")
async def update(role_id: int, request: Request, user=Depends(require_permission("Update Roles"))):
    data = await request.json()
    return await controllerRole.update_role(role_id, data)


# ===============================
# Delete role (soft delete)
# ===============================
@router.put("/delete/{role_id}")
async def delete(role_id: int, user=Depends(require_permission("Delete Roles"))):
    return await controllerRole.delete_role(role_id)


# ===============================
# Get current user's role info
# ===============================
@router.get("/role/me")
async def get_me(payload: dict = Depends(get_current_user)):
    return {
        "email": payload["sub"],
        "role": payload["role"],
        "user_id": payload["user_id"],
        "permissions": payload["permissions"]
    }
