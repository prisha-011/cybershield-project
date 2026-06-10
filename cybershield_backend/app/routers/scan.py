from fastapi import APIRouter, HTTPException

from cybershield_backend.app.config import settings
from cybershield_backend.app.models.scan import ScanCreate
from cybershield_backend.app.models.scan_response import ScanResponse
from cybershield_backend.app.services.ai_service import get_ai_security_findings
from cybershield_backend.app.services.audit_service import log_audit_event
from cybershield_backend.app.services.findings_service import analyze_repository_files
from cybershield_backend.app.services.finding_normalizer import normalize_findings
from cybershield_backend.app.services.github_service import (
    get_github_workflow_files,
    get_important_files,
    get_repository_metadata,
    get_repository_root_contents,
)
from cybershield_backend.app.services.scan_persistence_service import (
    get_all_saved_scans,
    get_saved_scan_by_id,
    save_scan_result,
)
from cybershield_backend.app.utils.github_parser import parse_github_repo_url

router = APIRouter(prefix="/api/scans", tags=["Scans"])


@router.get("/debug/env")
async def debug_env():
    return {
        "github_token_loaded": bool(settings.GITHUB_TOKEN),
        "gemini_api_key_loaded": bool(settings.GEMINI_API_KEY),
    }


@router.get("/")
async def fetch_saved_scans():
    return await get_all_saved_scans()


@router.post("/scan", response_model=ScanResponse)
async def scan_repository(payload: ScanCreate):
    repo_url = str(payload.repo_url)

    await log_audit_event(
        action="scan_started",
        resource_type="repository",
        resource_id=repo_url,
        status="success",
        actor={"type": "user", "id": None},
        details={"repo_url": repo_url},
    )

    try:
        try:
            parsed_repo = parse_github_repo_url(repo_url)
        except ValueError as e:
            await log_audit_event(
                action="scan_failed",
                resource_type="repository",
                resource_id=repo_url,
                status="failed",
                actor={"type": "user", "id": None},
                details={
                    "repo_url": repo_url,
                    "error": str(e),
                    "stage": "parse_github_repo_url",
                },
            )
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

        rule_based_findings = analyze_repository_files(
            important_files,
            simplified_contents,
            workflow_files,
        )

        ai_result = get_ai_security_findings(
            owner=owner,
            repo=repo,
            metadata=metadata,
            important_files=important_files,
            workflow_files=workflow_files,
            rule_findings=rule_based_findings,
        )

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
            "message": "Repository scanned successfully",
            "repo_url": repo_url,
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

        await log_audit_event(
            action="scan_request_completed",
            resource_type="repository",
            resource_id=repo_url,
            status="success",
            actor={"type": "user", "id": None},
            details={
                "repo_url": repo_url,
                "scan_id": saved_scan["id"],
                "owner": owner,
                "repo": repo,
                "findings_total": findings_summary["total"],
                "high": findings_summary["high"],
                "medium": findings_summary["medium"],
                "low": findings_summary["low"],
                "info": findings_summary["info"],
            },
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        await log_audit_event(
            action="scan_failed",
            resource_type="repository",
            resource_id=repo_url,
            status="failed",
            actor={"type": "user", "id": None},
            details={
                "repo_url": repo_url,
                "error": str(e),
                "stage": "scan_repository",
            },
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scan_id}")
async def fetch_saved_scan_by_id(scan_id: str):
    scan = await get_saved_scan_by_id(scan_id)

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan