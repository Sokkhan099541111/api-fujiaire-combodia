from fastapi import APIRouter, Request
import controllers.controllerContact as controller

router = APIRouter(prefix="/api/contacts", tags=["Contact Us"])

# ----------------------------------------
# Admin Routes
# ----------------------------------------
@router.get("/")
async def get_all():
    return await controller.get_all_contacts()

@router.get("/{contact_id}")
async def get_by_id(contact_id: int):
    return await controller.get_contact_by_id(contact_id)

@router.post("/create")
async def create(request: Request):
    data = await request.json()
    return await controller.create_contact(data)

@router.put("/update/{contact_id}")
async def update(contact_id: int, request: Request):
    data = await request.json()
    return await controller.update_contact(contact_id, data)

@router.delete("/delete/{contact_id}")
async def delete(contact_id: int):
    return await controller.delete_contact(contact_id)

# ----------------------------------------
# Public Route (Optional)
# ----------------------------------------
@router.get("/all/public")
async def get_all_public():
    """Return all contacts (for public site display)."""
    return await controller.get_all_contacts()
