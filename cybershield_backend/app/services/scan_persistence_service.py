from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from database.collections import get_scan_runs_collection


async def save_scan_result(scan_data: dict):
    collection = get_scan_runs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    document = {
        "repo_url": scan_data.get("repo_url"),
        "owner": scan_data.get("owner"),
        "repo": scan_data.get("repo"),
        "normalized_url": scan_data.get("normalized_url"),
        "repository": scan_data.get("repository"),
        "root_contents": scan_data.get("root_contents"),
        "important_files": scan_data.get("important_files"),
        "workflow_files": scan_data.get("workflow_files"),
        "rule_based_findings": scan_data.get("rule_based_findings"),
        "ai_findings": scan_data.get("ai_findings"),
        "findings": scan_data.get("findings"),
        "findings_summary": scan_data.get("findings_summary"),
        "ai_analysis_status": scan_data.get("ai_analysis_status"),
        "ai_analysis_error": scan_data.get("ai_analysis_error"),
        "status": "completed",
        "created_at": datetime.utcnow(),
    }

    result = await collection.insert_one(document)
    saved_scan = await collection.find_one({"_id": result.inserted_id})

    saved_scan["id"] = str(saved_scan["_id"])
    del saved_scan["_id"]

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

    return scan