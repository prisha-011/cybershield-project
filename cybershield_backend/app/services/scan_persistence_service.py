from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from cybershield_backend.app.services.audit_service import log_audit_event
from cybershield_backend.app.services.findings_persistence_service import (
    get_findings_by_scan_id,
    save_findings,
)
from database.collections import get_scan_runs_collection


async def save_scan_result(scan_data: dict):
    collection = get_scan_runs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    findings = scan_data.get("findings") or []
    findings_summary = scan_data.get("findings_summary") or {
        "total": len(findings),
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }

    document = {
        "repo_url": scan_data.get("repo_url"),
        "owner": scan_data.get("owner"),
        "repo": scan_data.get("repo"),
        "normalized_url": scan_data.get("normalized_url"),
        "repository": scan_data.get("repository"),
        "root_contents": scan_data.get("root_contents") or [],
        "important_files": scan_data.get("important_files") or [],
        "workflow_files": scan_data.get("workflow_files") or [],
        "rule_based_findings": scan_data.get("rule_based_findings") or [],
        "ai_findings": scan_data.get("ai_findings") or [],
        "findings_summary": findings_summary,
        "findings_count": len(findings),
        "ai_analysis_status": scan_data.get("ai_analysis_status") or "not_started",
        "ai_analysis_error": scan_data.get("ai_analysis_error"),
        "status": "completed",
        "created_at": datetime.utcnow(),
    }

    result = await collection.insert_one(document)
    scan_id = str(result.inserted_id)

    await save_findings(scan_id, scan_data)

    saved_scan = await collection.find_one({"_id": result.inserted_id})

    if not saved_scan:
        raise Exception("Saved scan could not be retrieved")

    saved_scan["id"] = str(saved_scan["_id"])
    del saved_scan["_id"]

    saved_scan["findings"] = await get_findings_by_scan_id(saved_scan["id"])

    await log_audit_event(
        action="scan_completed",
        resource_type="scan_run",
        resource_id=scan_id,
        status="success",
        actor={"type": "system", "id": None},
        details={
            "repo_url": saved_scan.get("repo_url"),
            "owner": saved_scan.get("owner"),
            "repo": saved_scan.get("repo"),
            "findings_total": len(saved_scan["findings"]),
        },
    )

    return saved_scan


async def get_all_saved_scans():
    collection = get_scan_runs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    scans = []
    cursor = collection.find().sort("created_at", -1)

    async for scan in cursor:
        scan["id"] = str(scan["_id"])
        del scan["_id"]
        scans.append(scan)

    return scans


async def get_saved_scan_by_id(scan_id: str):
    collection = get_scan_runs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    try:
        object_id = ObjectId(scan_id)
    except InvalidId:
        return None

    scan = await collection.find_one({"_id": object_id})

    if not scan:
        return None

    scan["id"] = str(scan["_id"])
    del scan["_id"]

    scan["findings"] = await get_findings_by_scan_id(scan["id"])

    if "findings_summary" not in scan or not scan["findings_summary"]:
        findings = scan["findings"]
        scan["findings_summary"] = {
            "total": len(findings),
            "high": sum(1 for f in findings if f.get("severity") == "high"),
            "medium": sum(1 for f in findings if f.get("severity") == "medium"),
            "low": sum(1 for f in findings if f.get("severity") == "low"),
            "info": sum(1 for f in findings if f.get("severity") == "info"),
        }

    if "ai_analysis_status" not in scan:
        scan["ai_analysis_status"] = "not_started"

    if "ai_analysis_error" not in scan:
        scan["ai_analysis_error"] = None

    return scan