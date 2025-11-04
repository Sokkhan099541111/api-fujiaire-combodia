from fastapi import APIRouter, Depends, HTTPException, Request
from controllers import controllerSolution
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/solutions", tags=["solutions"])

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker

# ===============================
# Admin routes
# ===============================
@router.get("/")
async def get_all(user=Depends(require_permission("Read Solutions"))):
    return await controllerSolution.get_all_solutions()

@router.get("/{solution_id}")
async def get_one(solution_id: int, user=Depends(require_permission("Read Solutions"))):
    solution = await controllerSolution.get_solution_by_id(solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution

@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Solutions"))):
    data = await request.json()
    return await controllerSolution.create_solution(data)

@router.put("/update/{solution_id}")
async def update(solution_id: int, request: Request, user=Depends(require_permission("Update Solutions"))):
    data = await request.json()
    return await controllerSolution.update_solution(solution_id, data)

@router.put("/delete/{solution_id}")
async def delete(solution_id: int, user=Depends(require_permission("Delete Solutions"))):
    return await controllerSolution.delete_solution(solution_id)

# ===============================
# Public routes
# ===============================
@router.get("/all/public")
async def get_all_public():
    return await controllerSolution.get_all_solutions_public()

@router.get("/all/public/{solution_id}")
async def get_public_by_id(solution_id: int):
    solution = await controllerSolution.get_solution_public_by_id(solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution
