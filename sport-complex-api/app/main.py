from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

# Import API routers
from app.api.v1 import auth, trainers, services, products, orders, clients, analytics, recommendations, documents

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(trainers.router, prefix=settings.API_V1_STR)
app.include_router(services.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(clients.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)

# Mount static files (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME, 
        "version": settings.VERSION
    }

@app.get("/")
def root():
    """
    Serve the frontend application.
    """
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")
