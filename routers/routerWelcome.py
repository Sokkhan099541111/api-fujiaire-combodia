from fastapi import APIRouter, Depends, HTTPException, Request
from controllers import controllerWelcome
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/welcome", tags=["Welcome"])

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker

# -------------------------------
# Get all welcome entries
# -------------------------------
@router.get("/")
async def get_all(user=Depends(require_permission("Read Welcome"))):
    return await controllerWelcome.get_all_welcome()

# -------------------------------
# Get welcome by ID
# -------------------------------
@router.get("/{welcome_id}")
async def get_by_id(welcome_id: int, user=Depends(require_permission("Read Welcome"))):
    return await controllerWelcome.get_welcome_by_id(welcome_id)

# -------------------------------
# Create welcome entry
# -------------------------------
@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Welcome"))):
    data = await request.json()
    return await controllerWelcome.create_welcome(data)

# -------------------------------
# Update welcome entry
# -------------------------------
@router.put("/update/{welcome_id}")
async def update(welcome_id: int, request: Request, user=Depends(require_permission("Update Welcome"))):
    data = await request.json()
    return await controllerWelcome.update_welcome(welcome_id, data)

# -------------------------------
# Soft delete welcome entry
# -------------------------------
@router.put("/delete/{welcome_id}")
async def delete(welcome_id: int, user=Depends(require_permission("Delete Welcome"))):
    return await controllerWelcome.delete_welcome(welcome_id)

# -------------------------------
# Get all public welcome entries
# -------------------------------
@router.get("/all/public")
async def get_all_public():
    return await controllerWelcome.get_all_welcome_public()
