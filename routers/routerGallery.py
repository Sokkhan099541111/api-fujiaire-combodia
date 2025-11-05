from fastapi import APIRouter, UploadFile, File, Form
from controllers import controllerGallery

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])

# CREATE / UPLOAD IMAGE
@router.post("/create")
async def create_gallery(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    image_id: int = Form(None)
):
    return await controllerGallery.create_gallery(file, user_id, image_id)

# GET ALL ACTIVE GALLERY
@router.get("/")
async def get_all():
    return await controllerGallery.get_all_gallery()

# GET BY ID
@router.get("/{gallery_id}")
async def get_by_id(gallery_id: int):
    return await controllerGallery.get_gallery_by_id(gallery_id)

# UPDATE GALLERY (expects Form data)
@router.put("/{gallery_id}")
async def update_gallery(
    gallery_id: int,
    user_id: int = Form(None),
    image_id: int = Form(None),
    status: int = Form(1)
):
    return await controllerGallery.update_gallery(gallery_id, image_id, user_id, status)

# DELETE GALLERY
@router.delete("/{gallery_id}")
async def delete_gallery(gallery_id: int):
    return await controllerGallery.delete_gallery(gallery_id)
