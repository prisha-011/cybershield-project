from fastapi import APIRouter, HTTPException

from app.models.scan import ScanRequest
from app.services.scan_service import run_scan
from cybershield_backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("/scan")
async def scan_repository(request: ScanRequest):
    repo_url = str(request.repo_url)

    await log_audit_event(
        action="scan_started",
        resource_type="repository",
        resource_id=repo_url,
        status="success",
        actor={"type": "user", "id": None},
        details={"repo_url": repo_url},
    )

    try:
        result = await run_scan(repo_url)

        await log_audit_event(
            action="scan_request_completed",
            resource_type="repository",
            resource_id=repo_url,
            status="success",
            actor={"type": "user", "id": None},
            details={
                "repo_url": repo_url,
                "scan_id": result.get("id"),
                "findings_total": result.get("findings_summary", {}).get("total", 0),
            },
        )

        return result

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
            },
        )
        raise HTTPException(status_code=500, detail=str(e))