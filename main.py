from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# === Import Routers ===
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

# === Initialize App ===
app = FastAPI(redoc_url=None, docs_url=None, openapi_url=None)
app.router.redirect_slashes = True  # ✅ Prevents 307 redirect errors for /api/... vs /api...

# === Request Logging Middleware ===
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"➡️ {request.method} {request.url}")
    response = await call_next(request)
    print(f"⬅️ {response.status_code}")
    return response

# === CORS Configuration ===
origins = [
    "http://localhost:5173",
    "https://backend.fujiairecambodia.com",
    "https://demo.fujiairecambodia.com",
    "https://fujiaire-combodia-xzwba.ondigitalocean.app",  # ✅ App Platform domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Can set to ["*"] for temporary debugging
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# === Handle Missing Product Function (Safe Import) ===
try:
    import controllers.controllerProduct as controllerProduct
    if not hasattr(controllerProduct, "get_all_new_products_public"):
        def _fallback_get_all_new_products_public(*args, **kwargs):
            return []
        controllerProduct.get_all_new_products_public = _fallback_get_all_new_products_public
except Exception as e:
    print(f"⚠️ Product controller import issue: {e}")

# === OPTIONS Preflight Handler (Fix OPTIONS Repeated Calls) ===
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return {}

# === Include All Routers (No Duplicates) ===
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

# === Static Files for Uploads ===
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

# === Root Endpoint ===
@app.get("/")
def root():
    return {"message": "API is running securely 🎉"}
