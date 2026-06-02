from fastapi import FastAPI
from app.config import settings
from app.routers import scan

app = FastAPI(title=settings.APP_NAME)

app.include_router(scan.router)

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "environment": settings.APP_ENV
    }

@app.get("/health")
def health_check():
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "github_token_loaded": bool(settings.GITHUB_TOKEN),
        "gemini_api_key_loaded": bool(settings.GEMINI_API_KEY)
    }