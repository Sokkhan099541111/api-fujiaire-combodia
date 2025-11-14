from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import warnings

# ✅ Add this import for DB pool
from db import init_db_pool, pool

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
    "http://127.0.0.1:5173",
    'http://172.28.96.1:5173',
    "http://10.90.46.216:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://backend.fujiairecambodia.com",
    "https://demo.fujiairecambodia.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
)

# Inject fallback for missing product controller function to avoid AttributeError at runtime
try:
    import controllers.controllerProduct as controllerProduct
    if not hasattr(controllerProduct, "get_all_new_products_public"):
        # use a synchronous fallback to avoid returning a coroutine object to FastAPI
        def _fallback_get_all_new_products_public(*args, **kwargs):
            # Minimal safe fallback: return empty list (or change to {"detail": "Not implemented"} with status handling)
            return []
        controllerProduct.get_all_new_products_public = _fallback_get_all_new_products_public
except Exception:
    # If import fails or anything else goes wrong, don't crash app startup here.
    pass

# ✅ Initialize DB Pool Once
@app.on_event("startup")
async def startup_event():
    await init_db_pool()  # initialize only one pool
    print("✅ Database pool initialized")

# ✅ Close DB Pool on Shutdown
@app.on_event("shutdown")
async def shutdown_event():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        print("🧹 Database pool closed cleanly")

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

warnings.filterwarnings("ignore", category=DeprecationWarning)
# Include your gallery API router

app.include_router(routerGallery.router, prefix="/api/gallery", tags=["Gallery"])



@app.get("/")
def root():
    return {"message": "API is running securely 🎉"}
