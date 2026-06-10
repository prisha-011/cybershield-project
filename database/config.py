import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "cybershield_backend" / ".env"

load_dotenv(ENV_PATH)

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "cybershield_db")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in cybershield_backend/.env")