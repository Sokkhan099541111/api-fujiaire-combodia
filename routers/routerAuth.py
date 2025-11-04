<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.jwt_handler import create_access_token
from controllers.controllerUsers import get_user_from_db, get_user_permissions
from security import pwd_context

router = APIRouter(prefix="/api/auth", tags=["Auth"])
=======
import token
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.jwt_handler import create_access_token
from controllers.controllerUsers import get_user_from_db
from security import pwd_context
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/api/auth")
>>>>>>> 8d49c6b84cc6d05a2f74ec6138a4145acd273f6a

class LoginRequest(BaseModel):
    email: str
    password: str

<<<<<<< HEAD

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
=======
from controllers.controllerUsers import get_user_from_db, get_user_permissions

@router.post("/login")
def login(request: LoginRequest):
    user = get_user_from_db(request.email)
    if not user or not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    permissions = get_user_permissions(user["id"])

    token = create_access_token({
>>>>>>> 8d49c6b84cc6d05a2f74ec6138a4145acd273f6a
        "sub": user["email"],
        "role": user["role"],
        "user_id": user["id"],
        "permissions": permissions
    })

    return {
<<<<<<< HEAD
        "token": access_token,
=======
        "token": token,
        # "token_type": "bearer",
>>>>>>> 8d49c6b84cc6d05a2f74ec6138a4145acd273f6a
        "role": user["role"],
        "user_id": user["id"],
        "permissions": permissions
    }
<<<<<<< HEAD
=======

>>>>>>> 8d49c6b84cc6d05a2f74ec6138a4145acd273f6a
