from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


class Settings(BaseSettings):
    APP_NAME: str = "CyberShield Backend"
    APP_ENV: str = "development"
    GITHUB_TOKEN: str | None = None
    # OPENROUTER_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )




print("Using env file:", ENV_FILE)
print("Env file exists:", ENV_FILE.exists())

settings = Settings()