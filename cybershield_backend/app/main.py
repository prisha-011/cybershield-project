from contextlib import asynccontextmanager

from fastapi import FastAPI
from cybershield_backend.app.routers.findings import router as findings_router
from cybershield_backend.app.config import settings
from cybershield_backend.app.routers.scan import router as scan_router
from database.connection import connect_to_mongo, close_mongo_connection, get_database
from cybershield_backend.app.routers.audit import router as audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.include_router(scan_router)
app.include_router(findings_router)
app.include_router(audit_router)

@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "environment": settings.APP_ENV
    }


@app.get("/health")
async def health_check():
    db = get_database()

    return {
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "github_token_loaded": bool(settings.GITHUB_TOKEN),
        "gemini_api_key_loaded": bool(settings.GEMINI_API_KEY),
        "database_connected": db is not None
    }


@app.get("/api/db-test")
async def test_db():
    db = get_database()

    if db is None:
        return {
            "status": "error",
            "message": "Database not connected"
        }

    return {
        "status": "success",
        "message": "Database connected successfully",
        "database_name": db.name
    }