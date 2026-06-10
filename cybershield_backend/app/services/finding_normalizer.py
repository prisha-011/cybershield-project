SEVERITY_ORDER = {
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
}

def get_severity_rank(severity: str) -> int:
    return SEVERITY_ORDER.get(str(severity).lower().strip(), 0)


def build_finding_key(finding: dict) -> str:
    finding_type = str(finding.get("type", "")).strip().lower()
    title = str(finding.get("title", "")).strip().lower()
    description = str(finding.get("description", "")).strip().lower()

    if "gitignore" in finding_type or "gitignore" in title or "gitignore" in description:
        return "missing_gitignore"

    if "dependency" in finding_type or "package.json" in description or "requirements.txt" in description:
        return "missing_dependency_manifest"

    if "workflow" in finding_type and "permission" in title:
        return "workflow_permissions"

    if "secret" in finding_type or "token" in description or "credential" in description:
        return "possible_secret_exposure"

    if finding_type:
        return finding_type

    return title


def choose_better_finding(existing: dict, incoming: dict) -> dict:
    existing_rank = get_severity_rank(existing.get("severity"))
    incoming_rank = get_severity_rank(incoming.get("severity"))

    if incoming_rank > existing_rank:
        better = dict(incoming)
        other = dict(existing)
    else:
        better = dict(existing)
        other = dict(incoming)

    if not better.get("remediation") and other.get("remediation"):
        better["remediation"] = other["remediation"]

    if better.get("source") == "ai" and other.get("source") == "rule":
        better["source"] = "rule"

    return better


def deduplicate_findings(findings: list) -> list:
    deduped = {}

    for finding in findings:
        key = build_finding_key(finding)

        if key not in deduped:
            deduped[key] = finding
        else:
            deduped[key] = choose_better_finding(deduped[key], finding)

    return list(deduped.values())


def sort_findings(findings: list) -> list:
    return sorted(
        findings,
        key=lambda item: (
            -get_severity_rank(item.get("severity")),
            str(item.get("title", "")).lower()
        )
    )



def normalize_findings(findings: list) -> list:
    deduped = deduplicate_findings(findings)
    sorted_findings = sort_findings(deduped)
    return sorted_findings