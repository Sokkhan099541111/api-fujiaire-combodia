from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from utils.jwt_handler import decode_access_token, security

def require_permission(permission: str):
    def permission_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        payload = decode_access_token(token)

        user_permissions = payload.get("permissions", [])
        if permission not in user_permissions:
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")

        return payload  # Optional: return the whole user data
    return permission_dependency
