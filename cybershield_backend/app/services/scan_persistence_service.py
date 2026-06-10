from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from app.services.findings_persistence_service import save_findings
from cybershield_backend.app.services.audit_service import log_audit_event
from database.collections import get_scan_runs_collection
from app.services.findings_persistence_service import (
    get_findings_by_scan_id,
    save_findings,
)

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

    return scan


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