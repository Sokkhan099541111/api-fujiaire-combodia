from fastapi import APIRouter, Depends, HTTPException, Request
from controllers import controllerMission
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/missions", tags=["Mission"])


# ✅ Permission dependency
def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker


# ✅ Use await for all async controller calls
@router.get("/")
async def get_all(user=Depends(require_permission("Read Missions"))):
    return await controllerMission.get_all_missions()


@router.get("/{mission_id}")
async def get_one(mission_id: int, user=Depends(require_permission("Read Missions"))):
    return await controllerMission.get_mission_by_id(mission_id)


@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Missions"))):
    data = await request.json()
    return await controllerMission.create_mission(data)


@router.put("/update/{mission_id}")
async def update(mission_id: int, request: Request, user=Depends(require_permission("Update Missions"))):
    data = await request.json()
    return await controllerMission.update_mission(mission_id, data)


@router.put("/delete/{mission_id}")
async def delete(mission_id: int, user=Depends(require_permission("Delete Missions"))):
    return await controllerMission.delete_mission(mission_id)


@router.get("/all/public")
async def get_all_public():
    return await controllerMission.get_all_missions_public()
