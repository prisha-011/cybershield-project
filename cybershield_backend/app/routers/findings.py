from fastapi import APIRouter, HTTPException

from app.services.findings_persistence_service import (
    get_findings_by_repo,
    get_findings_by_scan_id,
    get_high_severity_findings,
)

router = APIRouter(prefix="/api/findings", tags=["findings"])


@router.get("/scan/{scan_id}")
async def get_scan_findings(scan_id: str):
    try:
        findings = await get_findings_by_scan_id(scan_id)
        return {"scan_id": scan_id, "findings": findings, "count": len(findings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repo/{owner}/{repo}")
async def get_repository_findings(owner: str, repo: str):
    try:
        findings = await get_findings_by_repo(owner, repo)
        return {
            "owner": owner,
            "repo": repo,
            "findings": findings,
            "count": len(findings),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/severity/high")
async def get_high_findings():
    try:
        findings = await get_high_severity_findings()
        return {"severity": "high", "findings": findings, "count": len(findings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))