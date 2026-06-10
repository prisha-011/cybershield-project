from datetime import datetime
from typing import Any, Optional

from database.collections import get_audit_logs_collection


async def log_audit_event(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    status: str = "success",
    actor: Optional[dict[str, Any]] = None,
    details: Optional[dict[str, Any]] = None,
):
    collection = get_audit_logs_collection()

    if collection is None:
        return None

    document = {
        "timestamp": datetime.utcnow(),
        "action": action,
        "resource": {
            "type": resource_type,
            "id": resource_id,
        },
        "status": status,
        "actor": actor or {
            "type": "system",
            "id": None,
        },
        "details": details or {},
    }

    result = await collection.insert_one(document)
    return str(result.inserted_id)