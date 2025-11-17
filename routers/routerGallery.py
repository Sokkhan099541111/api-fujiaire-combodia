from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from controllers.controllerGallery import (
    create_gallery,
    get_all_gallery,
    get_gallery_by_id,
    update_gallery,
    soft_delete_gallery,
)

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    image_id: Optional[int] = Form(None),
):
    result = await create_gallery(file, user_id, image_id)
    # If create_gallery returns JSONResponse on error, handle here:
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all():
    rows = await get_all_gallery()
    return {"gallery": rows}


@router.get("/{gallery_id}", status_code=status.HTTP_200_OK)
async def get_one(gallery_id: int):
    row = await get_gallery_by_id(gallery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    return {"gallery": row}


@router.put("/{gallery_id}", status_code=status.HTTP_200_OK)
async def update(
    gallery_id: int,
    image_id: Optional[int] = Form(None),
    user_id: Optional[int] = Form(None),
    status: int = Form(1),
):
    # Validate inputs if needed, e.g. user_id required
    result = await update_gallery(gallery_id, image_id, user_id, status)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete("/{gallery_id}", status_code=status.HTTP_200_OK)
async def delete(gallery_id: int):
    result = await soft_delete_gallery(gallery_id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


