from typing import List


def analyze_repository_files(
    important_files: List[dict],
    root_contents: List[dict],
    workflow_files: List[dict],
) -> List[dict]:
    findings = []

    file_paths = {item.get("path", "").lower() for item in important_files if item.get("path")}
    root_names = {item.get("name", "").lower() for item in root_contents if item.get("name")}
    workflow_paths = {item.get("path", "").lower() for item in workflow_files if item.get("path")}

    if ".env" in file_paths:
        findings.append({
            "severity": "high",
            "type": "secret_exposure",
            "title": "Potential environment file exposure",
            "description": "A .env file was found in the repository files.",
            "remediation": "Remove sensitive environment files from the repository and use secret management.",
            "source": "rule",
        })

    if "dockerfile" not in root_names:
        findings.append({
            "severity": "info",
            "type": "deployment",
            "title": "No Dockerfile detected",
            "description": "No Dockerfile was found in the repository root.",
            "remediation": "Add a Dockerfile if containerized deployment is planned.",
            "source": "rule",
        })

    if ".github/workflows" not in " ".join(workflow_paths):
        findings.append({
            "severity": "low",
            "type": "ci_cd",
            "title": "No GitHub Actions workflow detected",
            "description": "No GitHub Actions workflow files were found.",
            "remediation": "Add CI/CD workflows for automated testing and security checks.",
            "source": "rule",
        })

    for item in important_files:
        path = item.get("path", "").lower()
        content = (item.get("content") or "").lower()

        if path.endswith("requirements.txt") and "django" in content and "gunicorn" not in content:
            findings.append({
                "severity": "low",
                "type": "deployment",
                "title": "Gunicorn not listed in requirements",
                "description": "Django appears in requirements.txt but gunicorn was not detected.",
                "remediation": "Add gunicorn for production deployment if applicable.",
                "source": "rule",
            })

        if path.endswith(".py") and "debug=true" in content:
            findings.append({
                "severity": "medium",
                "type": "configuration",
                "title": "Debug mode may be enabled",
                "description": "A possible debug=true setting was found in a Python-related file.",
                "remediation": "Disable debug mode in production environments.",
                "source": "rule",
            })

        if "secret_key" in content or "api_key" in content:
            findings.append({
                "severity": "high",
                "type": "secret_exposure",
                "title": "Possible hardcoded secret detected",
                "description": "Potential secret-related keywords were found in repository file contents.",
                "remediation": "Move secrets to environment variables or a dedicated secret manager.",
                "source": "rule",
            })

    return findings