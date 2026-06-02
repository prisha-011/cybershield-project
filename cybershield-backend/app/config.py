import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "CyberShield Backend")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

settings = Settings()