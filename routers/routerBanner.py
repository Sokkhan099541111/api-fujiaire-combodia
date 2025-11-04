from fastapi import APIRouter
import controllers.controllerBanner as controllerBanner

router = APIRouter(prefix="/api/banners", tags=["Banners"])

@router.get("/all/public")
async def get_all():
    return await controllerBanner.get_all_banners()

@router.get("/all/public/{banner_type}")
async def get_by_type(banner_type: int):
    return await controllerBanner.get_banner_by_type(banner_type)

@router.get("/{banner_id}")
async def get_by_id(banner_id: int):
    return await controllerBanner.get_banner_by_id(banner_id)
