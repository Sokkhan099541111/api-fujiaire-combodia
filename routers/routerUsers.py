from fastapi import APIRouter, Depends, HTTPException, Request
import controllers.controllerUsers as user_ctrl
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker

# -------------------------------
# Get all users
# -------------------------------
@router.get("/")
async def get_all(user=Depends(require_permission("Read Users"))):
    return await user_ctrl.get_all_users()

# -------------------------------
# Get one user by ID
# -------------------------------
@router.get("/{user_id}")
async def get_one(user_id: int, user=Depends(require_permission("Read Users"))):
    return await user_ctrl.get_user_by_id(user_id)

# -------------------------------
# Create a new user
# -------------------------------
@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Users"))):
    data = await request.json()
    return await user_ctrl.create_user(data)

# -------------------------------
# Update an existing user
# -------------------------------
@router.put("/update/{user_id}")
async def update(user_id: int, request: Request, user=Depends(require_permission("Update Users"))):
    data = await request.json()
    return await user_ctrl.update_user(user_id, data)

# -------------------------------
# Soft delete user
# -------------------------------
@router.put("/delete/{user_id}")
async def delete(user_id: int, user=Depends(require_permission("Delete Users"))):
    return await user_ctrl.delete_user(user_id)
