from fastapi import APIRouter, Request, Depends, HTTPException, status
from utils.jwt_handler import get_current_user
import controllers.controllerBanner as controllerBanner

router = APIRouter(prefix="/api/banners", tags=["Banners"])

# -----------------------------
# Permission dependency
# -----------------------------
def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        permissions = user.get("permissions", [])
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return user
    return permission_checker


# -----------------------------
# ADMIN ROUTES (Protected)
# -----------------------------
@router.get("/", dependencies=[Depends(require_permission("Read banners"))])
async def get_all():
    return await controllerBanner.get_all_banners()


@router.get("/{banner_id}", dependencies=[Depends(require_permission("Read banners"))])
async def get_by_id(banner_id: int):
    return await controllerBanner.get_banner_by_id(banner_id)


@router.post("/", dependencies=[Depends(require_permission("Create banners"))])
async def create_banner(request: Request):
    data = await request.json()
    return await controllerBanner.create_banner(data)


@router.put("/update/{banner_id}", dependencies=[Depends(require_permission("Update banners"))])
async def update_banner(banner_id: int, request: Request):
    data = await request.json()
    return await controllerBanner.update_banner(banner_id, data)


@router.delete("/{banner_id}", dependencies=[Depends(require_permission("Delete banners"))])
async def delete_banner(banner_id: int):
    return await controllerBanner.delete_banner(banner_id)


@router.put("/set-type/{banner_id}", dependencies=[Depends(require_permission("Update banners"))])
async def set_banner_type(banner_id: int, request: Request):
    data = await request.json()
    banner_type = data.get("type")

    if banner_type is None:
        raise HTTPException(status_code=400, detail="Field 'type' is required")

    return await controllerBanner.set_banner_type(banner_id, banner_type)


# -----------------------------
# PUBLIC ROUTES (No auth)
# -----------------------------
@router.get("/all/public")
async def get_all_public():
    return await controllerBanner.get_all_banners_public()


@router.get("/all/public/{banner_type}")
async def get_public_by_type(banner_type: int):
    return await controllerBanner.get_banner_by_type(banner_type)
