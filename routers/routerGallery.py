# routes/gallery_router.py

from fastapi import APIRouter, UploadFile, File, Form
from controllers.controllerGallery import (
    create_gallery,
    get_all_gallery,
    get_gallery_by_id,
    update_gallery,
    soft_delete_gallery,
)

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])


# ----------------------------
# CREATE (POST)
# ----------------------------
@router.post("/create")
async def create(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    image_id: int = Form(None)
):
    return await create_gallery(file, user_id, image_id)


# ----------------------------
# READ ALL
# ----------------------------
@router.get("/")
async def get_all():
    rows = await get_all_gallery()
    return {"gallery": rows}


# ----------------------------
# READ ONE
# ----------------------------
@router.get("/{gallery_id}")
async def get_one(gallery_id: int):
    row = await get_gallery_by_id(gallery_id)
    if not row:
        return {"error": "Not found"}
    return {"gallery": row}


# ----------------------------
# UPDATE
# ----------------------------
@router.put("/{gallery_id}")
async def update(
    gallery_id: int,
    image_id: int = Form(None),
    user_id: int = Form(None),
    status: int = Form(1)
):
    return await update_gallery(gallery_id, image_id, user_id, status)


# ----------------------------
# DELETE (SOFT)
# ----------------------------
@router.delete("/{gallery_id}")
async def delete(gallery_id: int):
    return await soft_delete_gallery(gallery_id)
