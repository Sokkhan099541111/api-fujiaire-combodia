from fastapi import APIRouter, Depends, HTTPException, Request
import controllers.controllerIndustryDev as controller
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/industry", tags=["Industry Development"])

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker

# ----------------------------
# Admin routes
# ----------------------------
@router.get("/")
def get_all(user=Depends(require_permission("Read Industries"))):
    return controller.get_all_industries()

@router.get("/{industry_id}")
def get_by_id(industry_id: int, user=Depends(require_permission("Read Industries"))):
    return controller.get_industry_by_id(industry_id)

@router.post("/create")
def create(request: Request, user=Depends(require_permission("Create Industries"))):
    data = request.json() if hasattr(request, "json") else {}
    return controller.create_industry(data)

@router.put("/update/{industry_id}")
def update(industry_id: int, request: Request, user=Depends(require_permission("Update Industries"))):
    data = request.json() if hasattr(request, "json") else {}
    return controller.update_industry(industry_id, data)

@router.put("/delete/{industry_id}")
def delete(industry_id: int, user=Depends(require_permission("Delete Industries"))):
    return controller.delete_industry(industry_id)

# ----------------------------
# Public routes
# ----------------------------
@router.get("/all/public")
def get_all_public():
    return controller.get_all_industries_public()
