from fastapi import APIRouter, UploadFile, File, Form
from controllers import controllerGallery

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])

# ----------------------------
# CREATE / UPLOAD IMAGE
# ----------------------------
@router.post("/create")
async def create_gallery(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    image_id: int = Form(None)
):
    return await controllerGallery.create_gallery(file, user_id, image_id)


@router.get("/")
async def get_all_gallery():
    return await controllerGallery.get_all_gallery()


@router.get("/{gallery_id}")
async def get_gallery_by_id(gallery_id: int):
   
    return await controllerGallery.get_gallery_by_id(gallery_id)

@router.put("/{gallery_id}")
async def update_gallery(
    gallery_id: int,
    image_id: int = Form(None),
    user_id: int = Form(None),
    status: int = Form(1)
):
    return await controllerGallery.update_gallery(gallery_id, image_id, user_id, status)


# ----------------------------
# DELETE GALLERY (soft delete)
# ----------------------------
@router.delete("/delete/{gallery_id}")
async def delete_gallery(gallery_id: int):
    return await controllerGallery.delete_gallery(gallery_id)
