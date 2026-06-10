from datetime import datetime

from database.collections import get_findings_collection


async def save_findings(scan_id: str, scan_data: dict):
    collection = get_findings_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    findings = scan_data.get("findings") or []
    repo_url = scan_data.get("repo_url")
    owner = scan_data.get("owner")
    repo = scan_data.get("repo")

    saved_findings = []

    for finding in findings:
        document = {
            "scan_id": scan_id,
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo,
            "title": finding.get("title"),
            "description": finding.get("description"),
            "severity": finding.get("severity"),
            "category": finding.get("category"),
            "source": finding.get("source"),
            "file_path": finding.get("file_path"),
            "line_number": finding.get("line_number"),
            "recommendation": finding.get("recommendation"),
            "status": "open",
            "created_at": datetime.utcnow(),
        }

        result = await collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        saved_findings.append(document)

    return saved_findings


async def get_findings_by_scan_id(scan_id: str):
    collection = get_findings_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    findings = []
    cursor = collection.find({"scan_id": scan_id}).sort("created_at", -1)

    async for finding in cursor:
        finding["id"] = str(finding["_id"])
        del finding["_id"]
        findings.append(finding)

    return findings


async def get_findings_by_repo(owner: str, repo: str):
    collection = get_findings_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    findings = []
    cursor = collection.find({"owner": owner, "repo": repo}).sort("created_at", -1)

    async for finding in cursor:
        finding["id"] = str(finding["_id"])
        del finding["_id"]
        findings.append(finding)

    return findings


async def get_high_severity_findings():
    collection = get_findings_collection()

    if collection is None:
        raise Exception("Database connection is not available")

    findings = []
    cursor = collection.find({"severity": "high"}).sort("created_at", -1)

    async for finding in cursor:
        finding["id"] = str(finding["_id"])
        del finding["_id"]
        findings.append(finding)

    return findings