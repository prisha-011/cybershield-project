from fastapi import FastAPI
from cybershield_backend.app.config import settings
from cybershield_backend.app.routers.scan import router
from database.connection import connect_to_mongo, get_database


app = FastAPI(title=settings.APP_NAME)


app.include_router(router)


@app.on_event("startup")
def startup_db():
    connect_to_mongo()


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "environment": settings.APP_ENV
    }


@app.get("/health")
def health_check():
    db = get_database()

    return {
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "github_token_loaded": bool(settings.GITHUB_TOKEN),
        "gemini_api_key_loaded": bool(settings.GEMINI_API_KEY),
        "database_connected": db is not None
    }


@app.get("/api/db-test")
def test_db():
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