import re


def make_finding(
    severity: str,
    finding_type: str,
    title: str,
    description: str,
    remediation: str | None = None,
    source: str = "rule",
) -> dict:
    return {
        "severity": severity,
        "type": finding_type,
        "title": title,
        "description": description,
        "remediation": remediation,
        "source": source,
    }


def analyze_repository_files(important_files: list, root_contents: list, workflow_files: list) -> list:
    findings = []

    findings.extend(check_gitignore_presence(important_files))
    findings.extend(check_dependency_files(important_files))
    findings.extend(check_env_example_presence(important_files))
    findings.extend(check_hardcoded_secrets(important_files))
    findings.extend(check_github_actions_presence(root_contents))
    findings.extend(check_workflow_files(workflow_files))
    findings.extend(check_workflow_permissions(workflow_files))
    findings.extend(check_workflow_secret_risks(workflow_files))

    return findings


def check_gitignore_presence(important_files: list) -> list:
    findings = []

    gitignore_file = next((f for f in important_files if f["path"] == ".gitignore"), None)

    if not gitignore_file or not gitignore_file.get("exists"):
        findings.append(
            make_finding(
                severity="medium",
                finding_type="missing_gitignore",
                title="Missing .gitignore file",
                description="The repository does not appear to contain a .gitignore file, which increases the risk of committing secrets, environment files, or unnecessary artifacts.",
                remediation="Add a .gitignore file and include environment files, secrets, build artifacts, and local development files.",
            )
        )

    return findings


def check_dependency_files(important_files: list) -> list:
    findings = []

    package_json = next((f for f in important_files if f["path"] == "package.json" and f.get("exists")), None)
    requirements_txt = next((f for f in important_files if f["path"] == "requirements.txt" and f.get("exists")), None)

    if not package_json and not requirements_txt:
        findings.append(
            make_finding(
                severity="low",
                finding_type="missing_dependency_manifest",
                title="No dependency manifest detected",
                description="Neither package.json nor requirements.txt was found in the root files scanned, so dependency analysis may be incomplete.",
                remediation="Add and scan the correct dependency manifest so dependency security analysis can be performed.",
            )
        )

    return findings


def check_env_example_presence(important_files: list) -> list:
    findings = []

    env_example = next((f for f in important_files if f["path"] == ".env.example" and f.get("exists")), None)

    if env_example:
        findings.append(
            make_finding(
                severity="info",
                finding_type="env_example_present",
                title=".env.example file detected",
                description="The repository includes a .env.example file, which is a good sign for documenting required environment variables without exposing real secrets.",
                remediation="Keep only placeholder values in .env.example and never commit real credentials.",
            )
        )

    return findings


def check_hardcoded_secrets(important_files: list) -> list:
    findings = []

    secret_patterns = [
        r"api[_-]?key\s*=\s*[\"'][^\"']+[\"']",
        r"secret[_-]?key\s*=\s*[\"'][^\"']+[\"']",
        r"token\s*=\s*[\"'][^\"']+[\"']",
        r"password\s*=\s*[\"'][^\"']+[\"']",
        r"ghp_[A-Za-z0-9]{20,}",
        r"github_pat_[A-Za-z0-9_]+",
    ]

    for file in important_files:
        if not file.get("exists") or not file.get("content"):
            continue

        content = file["content"]

        for pattern in secret_patterns:
            matches = re.findall(pattern, content, flags=re.IGNORECASE)
            if matches:
                findings.append(
                    make_finding(
                        severity="high",
                        finding_type="possible_hardcoded_secret",
                        title=f"Possible hardcoded secret in {file['path']}",
                        description=f"The file {file['path']} contains text patterns that may indicate hardcoded credentials or tokens.",
                        remediation="Remove hardcoded secrets, rotate exposed credentials, and load them from secure environment variables or a secrets manager.",
                    )
                )
                break

    return findings


def check_github_actions_presence(root_contents: list) -> list:
    findings = []

    github_dir = next((item for item in root_contents if item["name"] == ".github" and item["type"] == "dir"), None)

    if github_dir:
        findings.append(
            make_finding(
                severity="info",
                finding_type="github_actions_possible",
                title=".github directory detected",
                description="The repository contains a .github directory. CI/CD workflows or automation files may be present and should be reviewed for secret handling and permissions.",
                remediation="Review workflow permissions, secret usage, and automation scope under the .github directory.",
            )
        )

    return findings


def check_workflow_files(workflow_files: list) -> list:
    findings = []

    if workflow_files:
        findings.append(
            make_finding(
                severity="info",
                finding_type="workflow_files_detected",
                title="GitHub Actions workflow files detected",
                description=f"{len(workflow_files)} workflow file(s) were found in .github/workflows and should be reviewed for permissions, secret handling, and unsafe execution patterns.",
                remediation="Inspect each workflow and enforce least privilege, safe secret usage, and trusted actions.",
            )
        )

    return findings


def check_workflow_permissions(workflow_files: list) -> list:
    findings = []

    for file in workflow_files:
        content = file.get("content")
        if not content:
            continue

        lowered = content.lower()

        if "permissions: write-all" in lowered:
            findings.append(
                make_finding(
                    severity="high",
                    finding_type="workflow_write_all_permissions",
                    title=f"Overly broad workflow permissions in {file['path']}",
                    description=f"The workflow file {file['path']} uses permissions: write-all, which may grant broader repository access than necessary.",
                    remediation="Replace write-all with explicit minimum permissions required by the workflow or job.",
                )
            )

        elif "permissions:" not in lowered:
            findings.append(
                make_finding(
                    severity="medium",
                    finding_type="workflow_permissions_not_explicit",
                    title=f"Workflow permissions not explicitly defined in {file['path']}",
                    description=f"The workflow file {file['path']} does not appear to define explicit permissions. Permissions should be reviewed and kept minimal.",
                    remediation="Define explicit minimal permissions for the workflow or each job instead of relying on defaults.",
                )
            )

    return findings


def check_workflow_secret_risks(workflow_files: list) -> list:
    findings = []

    risky_patterns = [
        "ghp_",
        "github_pat_",
        "api_key:",
        "secret_key:",
        "password:",
        "token:",
    ]

    for file in workflow_files:
        content = file.get("content")
        if not content:
            continue

        lowered = content.lower()

        for pattern in risky_patterns:
            if pattern in lowered:
                findings.append(
                    make_finding(
                        severity="high",
                        finding_type="possible_secret_in_workflow",
                        title=f"Possible secret exposure in workflow {file['path']}",
                        description=f"The workflow file {file['path']} contains text that may indicate a hardcoded secret or credential.",
                        remediation="Remove secrets from workflow files and use GitHub Actions secrets or another secure secret store.",
                    )
                )
                break

    return findings


def normalize_findings(findings: list) -> list:
    normalized = []

    allowed_severities = {"high", "medium", "low", "info"}

    for finding in findings:
        severity = str(finding.get("severity", "low")).lower().strip()
        if severity not in allowed_severities:
            severity = "low"

        normalized.append({
            "severity": severity,
            "type": finding.get("type", "unknown_issue"),
            "title": finding.get("title", "Untitled finding"),
            "description": finding.get("description", "No description provided."),
            "remediation": finding.get("remediation"),
            "source": finding.get("source", "rule"),
        })

    return normalized


def deduplicate_findings(findings: list) -> list:
    unique = []
    seen = set()

    for finding in findings:
        key = (
            finding.get("type"),
            finding.get("title"),
            finding.get("description"),
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(finding)

    return unique