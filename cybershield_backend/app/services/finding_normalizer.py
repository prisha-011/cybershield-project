from typing import List


ALLOWED_SEVERITIES = {"high", "medium", "low", "info"}
ALLOWED_SOURCES = {"rule", "ai"}


def normalize_findings(findings: List[dict]) -> List[dict]:
    normalized = []

    for finding in findings:
        severity = str(finding.get("severity", "info")).lower()
        if severity not in ALLOWED_SEVERITIES:
            severity = "info"

        source = str(finding.get("source", "rule")).lower()
        if source not in ALLOWED_SOURCES:
            source = "rule"

        normalized_finding = {
            "severity": severity,
            "type": str(finding.get("type", "general")),
            "title": str(finding.get("title", "Untitled finding")),
            "description": str(finding.get("description", "")),
            "remediation": finding.get("remediation"),
            "source": source,
        }

        normalized.append(normalized_finding)

    return normalized