from fastapi import APIRouter, Depends, HTTPException, Request
from controllers import controllerProduct
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return permission_checker

@router.get("/")
async def get_all(user=Depends(require_permission("Read Products"))):
    return await controllerProduct.get_all_products()

@router.get("/{product_id}")
async def get_one(product_id: int, user=Depends(require_permission("Read Products"))):
    return await controllerProduct.get_product_by_id(product_id)

@router.post("/create")
async def create(request: Request, user=Depends(require_permission("Create Products"))):
    data = await request.json()
    return await controllerProduct.create_product(data)

@router.put("/update/{product_id}")
async def update(product_id: int, request: Request, user=Depends(require_permission("Update Products"))):
    data = await request.json()
    return await controllerProduct.update_product(product_id, data)

@router.put("/delete/{product_id}")
async def delete(product_id: int, user=Depends(require_permission("Delete Products"))):
    return await controllerProduct.delete_product(product_id)


@router.get("/all/public")
async def get_all_public():
    return await controllerProduct.get_all_products_public()

@router.get("/all/public/{slug}")
async def get_all_public_id(slug: str):
    return await controllerProduct.get_product_by_slug(slug)


@router.get("/category/{category}/all/public")
async def get_all_products_by_category_public(category: str):
    return await controllerProduct.get_all_products_by_category_public(category)

@router.get("/new/all/public")
async def get_all_new_products_public():
    return await controllerProduct.get_all_new_products_public()

@router.put("/update/product/category/{product_id}")
async def update_category(product_id: int, request: Request, user=Depends(require_permission("Update Products"))):
    data = await request.json()
    return await controllerProduct.update_product_category(product_id, data)

@router.put("/update/product/new/{product_id}")
async def update_new(product_id: int, request: Request, user=Depends(require_permission("Update Products"))):
    data = await request.json()
    return await controllerProduct.update_product_new(product_id, data)