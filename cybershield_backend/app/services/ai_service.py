import json
from google import genai
from fastapi import HTTPException
from app.config import settings


def normalize_ai_findings(ai_findings: list) -> list:
    normalized = []

    for item in ai_findings:
        if not isinstance(item, dict):
            continue

        severity = str(item.get("severity", "low")).lower().strip()
        if severity not in {"high", "medium", "low", "info"}:
            severity = "low"

        normalized.append({
            "severity": severity,
            "type": item.get("type", "ai_generated_finding"),
            "title": item.get("title", "AI-generated finding"),
            "description": item.get("description", "No description provided."),
            "remediation": item.get("remediation"),
            "source": "ai",
        })

    return normalized


def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=settings.GEMINI_API_KEY)


def build_security_prompt(
    owner: str,
    repo: str,
    metadata: dict,
    important_files: list,
    workflow_files: list,
    rule_findings: list,
) -> str:
    prompt = f"""
You are a cybersecurity code review assistant.

Analyze this GitHub repository evidence and return additional security findings.

Repository:
- Owner: {owner}
- Repo: {repo}
- Default branch: {metadata.get("default_branch")}
- Primary language: {metadata.get("language")}

Rule-based findings already detected:
{json.dumps(rule_findings, indent=2)}

Important files:
{json.dumps(important_files, indent=2)}

Workflow files:
{json.dumps(workflow_files, indent=2)}

Return output only as valid JSON in this format:
[
{{
    "severity": "high|medium|low|info",
    "type": "short_machine_name",
    "title": "Short finding title",
    "description": "What is risky and why",
    "remediation": "How to fix it"
}}
]

Rules:
- Return only JSON.
- Do not include markdown.
- Do not repeat the exact same findings unless you add new value.
- Focus on secrets exposure, insecure CI/CD, unsafe dependency practices, missing validation, risky config, and obvious security weaknesses.
"""
    return prompt



def get_ai_security_findings(
    owner: str,
    repo: str,
    metadata: dict,
    important_files: list,
    workflow_files: list,
    rule_findings: list,
) -> dict:
    try:
        client = get_gemini_client()

        prompt = build_security_prompt(
            owner=owner,
            repo=repo,
            metadata=metadata,
            important_files=important_files,
            workflow_files=workflow_files,
            rule_findings=rule_findings,
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        text = (response.text or "").strip()

        if not text:
            return {
                "findings": [],
                "status": "empty_response",
                "error": "Gemini returned an empty response."
            }

        if text.startswith("```json"):
            text = text.replace("```json", "", 1).strip()
        if text.startswith("```"):
            text = text.replace("```", "", 1).strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        parsed = json.loads(text)

        if isinstance(parsed, list):
            return {
                "findings": normalize_ai_findings(parsed),
                "status": "success",
                "error": None
            }

        return {
            "findings": [],
            "status": "invalid_format",
            "error": "Gemini response was not a JSON list."
        }

    except Exception as e:
        error_message = str(e)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            error_message = "Gemini quota exceeded. AI analysis was skipped."

        return {
            "findings": [],
            "status": "failed",
            "error": error_message
        }