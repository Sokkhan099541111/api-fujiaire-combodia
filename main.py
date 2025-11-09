from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# Router imports
from routers import (
    routerUsers,
    routerAuth,
    routerRole,
    routerCategories,
    routerProduct,
    routerBanner,
    routerGallery,
    routerMission,
    routerNews,
    routerWelcome,
    routerProfileCeo,
    routerIndustryDev,
    routerContact,
    routerFormContact,
    routerChooseUs,
    routerSolution,
    routerWarranty,
    routerPermission,
    routerRolePermission,
    routerSpicification,
)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://backend.fujiairecambodia.com",
    "https://demo.fujiairecambodia.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Or ["*"] during testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly include OPTIONS
    allow_headers=["*"],
)


try:
    import controllers.controllerProduct as controllerProduct
    if not hasattr(controllerProduct, "get_all_new_products_public"):
        def _fallback_get_all_new_products_public(*args, **kwargs):
            return []
        controllerProduct.get_all_new_products_public = _fallback_get_all_new_products_public
except Exception:
    pass

# Include routers
app.include_router(routerUsers.router)
app.include_router(routerAuth.router)
app.include_router(routerRole.router)
app.include_router(routerCategories.router)
app.include_router(routerProduct.router)
app.include_router(routerBanner.router)
app.include_router(routerGallery.router)
app.include_router(routerMission.router)
app.include_router(routerNews.router)
app.include_router(routerWelcome.router)
app.include_router(routerProfileCeo.router)
app.include_router(routerIndustryDev.router)
app.include_router(routerContact.router)
app.include_router(routerFormContact.router)
app.include_router(routerChooseUs.router)
app.include_router(routerSolution.router)
app.include_router(routerWarranty.router)
app.include_router(routerPermission.router)
app.include_router(routerRolePermission.router)
app.include_router(routerSpicification.router)
app.include_router(routerGallery.router)
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")


# Include your gallery API router

app.include_router(routerGallery.router, prefix="/api/gallery", tags=["Gallery"])

# Basic root endpoint

@app.get("/")
def root():
    return {"message": "API is running securely 🎉"}
