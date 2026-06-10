from fastapi import APIRouter, HTTPException
from cybershield_backend.app.config import settings
from cybershield_backend.app.models.scan import ScanRequest
from cybershield_backend.app.models.scan_response import ScanResponse
from cybershield_backend.app.services.ai_service import get_ai_security_findings
from cybershield_backend.app.services.findings_service import analyze_repository_files
from cybershield_backend.app.services.finding_normalizer import normalize_findings
from cybershield_backend.app.services.github_service import (
    get_github_workflow_files,
    get_important_files,
    get_repository_metadata,
    get_repository_root_contents,
)
from cybershield_backend.app.services.scan_persistence_service import (
    save_scan_result,
    get_all_saved_scans,
    get_saved_scan_by_id,
)
from cybershield_backend.app.utils.github_parser import parse_github_repo_url

router = APIRouter(prefix="/api", tags=["scan"])


@router.get("/debug/env")
def debug_env():
    return {
        "github_token_loaded": bool(settings.GITHUB_TOKEN),
        "gemini_api_key_loaded": bool(settings.GEMINI_API_KEY),
    }

@router.get("/scans")
async def fetch_saved_scans():
    return await get_all_saved_scans()


@router.get("/scans/{scan_id}")
async def fetch_saved_scan_by_id(scan_id: str):
    scan = await get_saved_scan_by_id(scan_id)

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan

@router.post("/scan", response_model=ScanResponse)
async def scan_repository(payload: ScanRequest):
    try:
        parsed_repo = parse_github_repo_url(str(payload.repo_url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    owner = parsed_repo["owner"]
    repo = parsed_repo["repo"]

    metadata = get_repository_metadata(owner, repo)
    contents = get_repository_root_contents(owner, repo)
    important_files = get_important_files(owner, repo)
    workflow_files = get_github_workflow_files(owner, repo)

    simplified_contents = [
        {
            "name": item["name"],
            "type": item["type"],
            "path": item["path"],
        }
        for item in contents
    ]

    findings = analyze_repository_files(important_files, simplified_contents, workflow_files)

    ai_result = get_ai_security_findings(
        owner=owner,
        repo=repo,
        metadata=metadata,
        important_files=important_files,
        workflow_files=workflow_files,
        rule_findings=findings,
    )

    rule_based_findings = findings
    ai_findings = ai_result["findings"]
    all_findings = normalize_findings(rule_based_findings + ai_findings)

    findings_summary = {
        "total": len(all_findings),
        "high": len([f for f in all_findings if f["severity"] == "high"]),
        "medium": len([f for f in all_findings if f["severity"] == "medium"]),
        "low": len([f for f in all_findings if f["severity"] == "low"]),
        "info": len([f for f in all_findings if f["severity"] == "info"]),
    }

    response_data = {
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
        "important_files": important_files,
        "workflow_files": workflow_files,
        "rule_based_findings": rule_based_findings,
        "ai_findings": ai_findings,
        "ai_analysis_status": ai_result["status"],
        "ai_analysis_error": ai_result["error"],
        "findings_summary": findings_summary,
        "findings": all_findings,
    }
    

    saved_scan = await save_scan_result(response_data)
    response_data["scan_id"] = saved_scan["id"]
    return response_data