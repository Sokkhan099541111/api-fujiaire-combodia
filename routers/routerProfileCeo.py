from fastapi import APIRouter, Request
import controllers.controllerProfileCeo as controller

router = APIRouter(prefix="/api/ceo", tags=["Profile CEO"])

@router.get("/")
async def get_all():
    return await controller.get_all_ceos()

@router.get("/{ceo_id}")
async def get_by_id(ceo_id: int):
    return await controller.get_ceo_by_id(ceo_id)

@router.post("/create")
async def create(request: Request):
    data = await request.json()
    return await controller.create_ceo(data)

@router.put("/update/{ceo_id}")
async def update(ceo_id: int, request: Request):
    data = await request.json()
    return await controller.update_ceo(ceo_id, data)

@router.put("/delete/{ceo_id}")
async def delete(ceo_id: int):
    return await controller.delete_ceo(ceo_id)


@router.get("/all/public")
async def get_all_public():
    return await controller.get_all_ceos_public()

@router.get("/get_testimonial_public/all/public/{publisher_id}")
async def get_all_by_type_public(publisher_id: int):
    return await controller.get_testimonial_public(publisher_id)

@router.put("/set-testimonial/{publisher}")
async def set_testimonial(publisher: int, request: Request):
    data = await request.json()
    return await controller.set_testimonial(publisher, data)