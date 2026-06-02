from fastapi import APIRouter
from app.models.scan import ScanRequest

router = APIRouter(prefix="/api", tags=["scan"])

@router.post("/scan")
def scan_repository(payload: ScanRequest):
    print(f"Received repo URL: {payload.repo_url}")

    return {
        "message": "Repository URL received successfully",
        "repo_url": payload.repo_url
    }