from fastapi import APIRouter, Request
import controllers.controllerFormContact as controller

router = APIRouter(prefix="/form-contacts", tags=["Form Contact"])

@router.get("/")
async def get_all():
    return await controller.get_all_form_contacts()

@router.get("/{contact_id}")
async def get_by_id(contact_id: int):
    return await controller.get_form_contact_by_id(contact_id)

@router.post("/create")
async def create(request: Request):
    data = await request.json()
    return await controller.create_form_contact(data)

@router.put("/update/{contact_id}")
async def update(contact_id: int, request: Request):
    data = await request.json()
    return await controller.update_form_contact(contact_id, data)

@router.delete("/delete/{contact_id}")
async def delete(contact_id: int):
    return await controller.delete_form_contact(contact_id)
