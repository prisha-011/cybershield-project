from fastapi import APIRouter, HTTPException
from app.models.scan import ScanRequest
from app.utils.github_parser import parse_github_repo_url

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan")
def scan_repository(payload: ScanRequest):
    try:
        parsed_repo = parse_github_repo_url(str(payload.repo_url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    print(f"Received repo URL: {payload.repo_url}")
    print(f"Owner: {parsed_repo['owner']}, Repo: {parsed_repo['repo']}")

    return {
        "message": "Repository parsed successfully",
        "repo_url": str(payload.repo_url),
        "owner": parsed_repo["owner"],
        "repo": parsed_repo["repo"],
        "normalized_url": parsed_repo["normalized_url"]
    }