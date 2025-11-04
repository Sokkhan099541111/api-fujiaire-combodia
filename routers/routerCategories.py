from fastapi import APIRouter, Depends, Request, HTTPException
from controllers import controllerCategories
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories"])

# -------------------------
# 🔒 Permission dependency
# -------------------------
def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if "permissions" not in user or permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker


# -------------------------
# 📦 Admin Category Routes
# -------------------------
@router.get("/")
async def get_all(user=Depends(require_permission("Read Categories"))):
    """Get all categories (admin only)"""
    return await controllerCategories.get_all_categories()


@router.get("/{category_id}")
async def get_by_id(category_id: int, user=Depends(require_permission("Read Categories"))):
    """Get a single category by ID (admin only)"""
    category = await controllerCategories.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Categories"))):
    """Create a new category (admin only)"""
    data = await request.json()
    return await controllerCategories.create_category(data)


@router.put("/update/{category_id}")
async def update(category_id: int, request: Request, user=Depends(require_permission("Update Categories"))):
    """Update a category (admin only)"""
    data = await request.json()
    return await controllerCategories.update_category(category_id, data)


@router.put("/delete/{category_id}")
async def delete(category_id: int, user=Depends(require_permission("Delete Categories"))):
    """Soft delete a category (admin only)"""
    return await controllerCategories.delete_category(category_id)


# -------------------------
# 🌍 Public Category Route
# -------------------------
@router.get("/all/public")
async def get_all_public():
    return await controllerCategories.get_all_categories_public()
