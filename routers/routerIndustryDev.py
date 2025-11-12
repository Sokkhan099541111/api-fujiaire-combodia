from fastapi import APIRouter, Depends, HTTPException, Request, status
from utils.jwt_handler import get_current_user
import controllers.controllerIndustryDev as controller

router = APIRouter(prefix="/api/industry", tags=["Industry Development"])

# ----------------------------
# Permission checker
# ----------------------------
def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        permissions = user.get("permissions", [])
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}"
            )
        return user
    return permission_checker


# ----------------------------
# Admin routes (Protected)
# ----------------------------
@router.get("/", dependencies=[Depends(require_permission("Read Industries"))])
async def get_all():
    return await controller.get_all_industries()


@router.get("/{industry_id}", dependencies=[Depends(require_permission("Read Industries"))])
async def get_by_id(industry_id: int):
    return await controller.get_industry_by_id(industry_id)


@router.post("/create/", dependencies=[Depends(require_permission("Create Industries"))])
async def create(request: Request):
    data = await request.json()
    return await controller.create_industry(data)

@router.put("/update/{industry_id}", dependencies=[Depends(require_permission("Update Industries"))])
async def update(industry_id: int, request: Request):
    data = await request.json()
    return await controller.update_industry(industry_id, data)


@router.delete("/{industry_id}", dependencies=[Depends(require_permission("Delete Industries"))])
async def delete(industry_id: int):
    return await controller.delete_industry(industry_id)


# ----------------------------
# Public routes
# ----------------------------
@router.get("/all/public")
async def get_all_public():
    return await controller.get_all_industries_public()
