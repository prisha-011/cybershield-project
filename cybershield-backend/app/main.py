from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import scan


app = FastAPI(title=settings.APP_NAME)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], # In production you'd specify your React URL, but "*" is perfect for the hackathon dev environment
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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