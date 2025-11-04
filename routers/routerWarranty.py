from fastapi import APIRouter, Depends, HTTPException, Request
from controllers import controllerWarranty
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/warranties", tags=["warranties"])

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker

# -------------------------------
# Get all warranties
# -------------------------------
@router.get("/")
async def get_all(user=Depends(require_permission("Read Warranties"))):
    return await controllerWarranty.get_all_warranties()

# -------------------------------
# Get one warranty by ID
# -------------------------------
@router.get("/{warranty_id}")
async def get_one(warranty_id: int, user=Depends(require_permission("Read Warranties"))):
    return await controllerWarranty.get_warranty_by_id(warranty_id)

# -------------------------------
# Create a warranty
# -------------------------------
@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Warranties"))):
    data = await request.json()
    return await controllerWarranty.create_warranty(data)

# -------------------------------
# Update a warranty
# -------------------------------
@router.put("/update/{warranty_id}")
async def update(warranty_id: int, request: Request, user=Depends(require_permission("Update Warranties"))):
    data = await request.json()
    return await controllerWarranty.update_warranty(warranty_id, data)

# -------------------------------
# Soft delete a warranty
# -------------------------------
@router.put("/delete/{warranty_id}")
async def delete(warranty_id: int, user=Depends(require_permission("Delete Warranties"))):
    return await controllerWarranty.delete_warranty(warranty_id)

# -------------------------------
# Get all public warranties
# -------------------------------
@router.get("/all/public")
async def get_all_public():
    return await controllerWarranty.get_all_warranties_public()
