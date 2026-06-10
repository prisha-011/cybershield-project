from fastapi import APIRouter, HTTPException

from app.services.audit_read_service import (
    get_all_audit_logs,
    get_audit_logs_by_action,
    get_audit_logs_by_resource,
)

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/")
async def list_audit_logs():
    try:
        logs = await get_all_audit_logs()
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/action/{action}")
async def list_audit_logs_by_action(action: str):
    try:
        logs = await get_audit_logs_by_action(action)
        return {"action": action, "logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource/{resource_type}/{resource_id}")
async def list_audit_logs_by_resource(resource_type: str, resource_id: str):
    try:
        logs = await get_audit_logs_by_resource(resource_type, resource_id)
        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "logs": logs,
            "count": len(logs),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    