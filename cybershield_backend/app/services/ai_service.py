import json
import time
import requests

from cybershield_backend.app.config import settings

# Updated to the globally active, non-deprecated model identifier
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)
MAX_RETRIES = 4


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

    last_error = None

    for attempt in range(MAX_RETRIES):
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
                    ],
                    # Tells Google to natively output clean, structured JSON 
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                },
                timeout=45,
            )

            if response.status_code == 503:
                last_error = f"503 Service Unavailable on attempt {attempt + 1}"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue

            response.raise_for_status()

            data = response.json()
            candidates = data.get("candidates", [])

            if not candidates:
                return {
                    "status": "success",
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
                "status": "success",
                "error": None,
                "findings": cleaned_findings,
            }

        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue

    return {
        "status": "failed",
        "error": last_error,
        "findings": [],
    }