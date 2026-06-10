import json
import requests

from cybershield_backend.app.config import settings


GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def build_ai_prompt(
    owner: str,
    repo: str,
    metadata: dict,
    important_files: list,
    workflow_files: list,
    rule_findings: list,
) -> str:
    return f"""
You are a cybersecurity audit assistant.

Analyze this GitHub repository and return a JSON array of additional security findings.

Repository owner: {owner}
Repository name: {repo}
Metadata: {json.dumps(metadata, default=str)}
Important files: {json.dumps(important_files, default=str)}
Workflow files: {json.dumps(workflow_files, default=str)}
Existing rule-based findings: {json.dumps(rule_findings, default=str)}

Return only a JSON array.
Each finding must have:
- severity: one of high, medium, low, info
- type: short machine-friendly category
- title: short title
- description: concise explanation
- remediation: short fix recommendation
- source: ai
""".strip()


def extract_json_array(text: str):
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = [line for line in lines if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end < start:
        return []

    json_text = text[start:end + 1]

    try:
        data = json.loads(json_text)
        if isinstance(data, list):
            return data
    except Exception:
        return []

    return []


def get_ai_security_findings(
    owner: str,
    repo: str,
    metadata: dict,
    important_files: list,
    workflow_files: list,
    rule_findings: list,
) -> dict:
    if not settings.GEMINI_API_KEY:
        return {
            "status": "skipped",
            "error": "GEMINI_API_KEY not configured",
            "findings": [],
        }

    prompt = build_ai_prompt(
        owner=owner,
        repo=repo,
        metadata=metadata,
        important_files=important_files,
        workflow_files=workflow_files,
        rule_findings=rule_findings,
    )

    try:
        response = requests.post(
            GEMINI_API_URL,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": settings.GEMINI_API_KEY,
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
            timeout=45,
        )
        response.raise_for_status()

        data = response.json()
        candidates = data.get("candidates", [])

        if not candidates:
            return {
                "status": "completed",
                "error": None,
                "findings": [],
            }

        text = (
            candidates[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        findings = extract_json_array(text)

        cleaned_findings = []
        for finding in findings:
            if not isinstance(finding, dict):
                continue

            cleaned_findings.append({
                "severity": str(finding.get("severity", "info")).lower(),
                "type": str(finding.get("type", "general")),
                "title": str(finding.get("title", "Untitled AI finding")),
                "description": str(finding.get("description", "")),
                "remediation": finding.get("remediation"),
                "source": "ai",
            })

        return {
            "status": "completed",
            "error": None,
            "findings": cleaned_findings,
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "findings": [],
        }