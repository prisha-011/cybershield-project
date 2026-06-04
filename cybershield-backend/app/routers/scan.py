from fastapi import APIRouter, HTTPException
from app.models.scan import ScanRequest
from app.utils.github_parser import parse_github_repo_url
from app.services.github_service import (
    get_repository_metadata,
    get_repository_root_contents,
    get_important_files,
)

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan")
def scan_repository(payload: ScanRequest):
    try:
        parsed_repo = parse_github_repo_url(str(payload.repo_url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    owner = parsed_repo["owner"]
    repo = parsed_repo["repo"]

    metadata = get_repository_metadata(owner, repo)
    contents = get_repository_root_contents(owner, repo)
    important_files = get_important_files(owner, repo)

    simplified_contents = [
        {
            "name": item["name"],
            "type": item["type"],
            "path": item["path"]
        }
        for item in contents
    ]

    return {
        "message": "Repository fetched successfully",
        "repo_url": str(payload.repo_url),
        "owner": owner,
        "repo": repo,
        "normalized_url": parsed_repo["normalized_url"],
        "repository": {
            "full_name": metadata.get("full_name"),
            "private": metadata.get("private"),
            "default_branch": metadata.get("default_branch"),
            "language": metadata.get("language"),
            "stargazers_count": metadata.get("stargazers_count"),
            "forks_count": metadata.get("forks_count"),
            "open_issues_count": metadata.get("open_issues_count"),
        },
        "root_contents": simplified_contents,
        "important_files": important_files
    }