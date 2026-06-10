from database.collections import get_audit_logs_collection


async def get_all_audit_logs():
    collection = get_audit_logs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    logs = []
    cursor = collection.find().sort("timestamp", -1)

    async for log in cursor:
        log["id"] = str(log["_id"])
        del log["_id"]
        logs.append(log)

    return logs


async def get_audit_logs_by_action(action: str):
    collection = get_audit_logs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    logs = []
    cursor = collection.find({"action": action}).sort("timestamp", -1)

    async for log in cursor:
        log["id"] = str(log["_id"])
        del log["_id"]
        logs.append(log)

    return logs


async def get_audit_logs_by_resource(resource_type: str, resource_id: str):
    collection = get_audit_logs_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    logs = []
    cursor = collection.find(
        {
            "resource.type": resource_type,
            "resource.id": resource_id,
        }
    ).sort("timestamp", -1)

    async for log in cursor:
        log["id"] = str(log["_id"])
        del log["_id"]
        logs.append(log)

    return logs