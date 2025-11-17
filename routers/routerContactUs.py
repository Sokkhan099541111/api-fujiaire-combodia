from fastapi import APIRouter, Form
from controllers.controllerContactUs import submit_contact_controller

router = APIRouter(prefix="/api/contact", tags=["Contact"])


@router.post("/")
async def send_contact(data: dict):
    return await submit_contact_controller(data)