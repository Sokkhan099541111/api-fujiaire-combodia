from fastapi import APIRouter
from pydantic import BaseModel
from controllers.controllerContactUs import submit_contact_controller

router = APIRouter(prefix="/api/contact", tags=["Contact"])


class ContactForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str


@router.post("/")
async def send_contact(data: ContactForm):
    return await submit_contact_controller(data.dict())
