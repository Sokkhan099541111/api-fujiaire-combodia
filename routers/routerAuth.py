from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.jwt_handler import create_access_token
from controllers.controllerUsers import get_user_from_db, get_user_permissions
from security import pwd_context

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    # ✅ Await async database function
    user = await get_user_from_db(request.email)

    if not user or not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ Await async function to fetch permissions
    permissions = await get_user_permissions(user["id"])

    # ✅ Create JWT token
    access_token = create_access_token({
        "sub": user["email"],
        "role": user["role"],
        "user_id": user["id"],
        "permissions": permissions
    })

    return {
        "token": access_token,
        "role": user["role"],
        "user_id": user["id"],
        "permissions": permissions
    }
