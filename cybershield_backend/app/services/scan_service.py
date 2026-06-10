from bson import ObjectId

from app.models.scan import ScanCreate, ScanInDB
from database.collections import get_scan_runs_collection


async def create_scan(scan_data: ScanCreate):
    collection = get_scan_runs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    scan_document = ScanInDB(
        repo_url=str(scan_data.repo_url),
        repo_name=scan_data.repo_name,
        owner=scan_data.owner,
        branch=scan_data.branch
    ).model_dump()

    result = await collection.insert_one(scan_document)
    created_scan = await collection.find_one({"_id": result.inserted_id})

    created_scan["id"] = str(created_scan["_id"])
    del created_scan["_id"]

    return created_scan


async def get_all_scans():
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


async def get_scan_by_id(scan_id: str):
    collection = get_scan_runs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    scan = await collection.find_one({"_id": ObjectId(scan_id)})

    if not scan:
        return None

    scan["id"] = str(scan["_id"])
    del scan["_id"]

    return scan