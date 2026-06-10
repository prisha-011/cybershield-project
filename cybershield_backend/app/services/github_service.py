import base64

import requests

from cybershield_backend.app.config import settings

GITHUB_API_BASE = "https://api.github.com"


def get_github_headers():
    headers = {
        "Accept": "application/vnd.github+json"
    }

    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    return headers


def get_repository_metadata(owner: str, repo: str) -> dict:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    response = requests.get(url, headers=get_github_headers(), timeout=20)
    response.raise_for_status()
    return response.json()


def get_repository_root_contents(owner: str, repo: str) -> list:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents"
    response = requests.get(url, headers=get_github_headers(), timeout=20)
    response.raise_for_status()
    return response.json()


def get_file_content(owner: str, repo: str, path: str) -> dict | None:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=get_github_headers(), timeout=20)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json()

    content = data.get("content")
    decoded_content = None

    if content and data.get("encoding") == "base64":
        try:
            decoded_content = base64.b64decode(content).decode("utf-8", errors="ignore")
        except Exception:
            decoded_content = None

    return {
        "path": data.get("path"),
        "logical_name": path.split("/")[-1],
        "exists": True,
        "size": data.get("size"),
        "type": data.get("type"),
        "content": decoded_content,
    }


def get_important_files(owner: str, repo: str) -> list:
    important_paths = [
        "README.md",
        "requirements.txt",
        "package.json",
        "Dockerfile",
        ".env",
        ".gitignore",
        "docker-compose.yml",
        "pyproject.toml",
    ]

    files = []

    for path in important_paths:
        file_data = get_file_content(owner, repo, path)
        if file_data:
            files.append(file_data)

    return files


def get_github_workflow_files(owner: str, repo: str) -> list:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows"
    response = requests.get(url, headers=get_github_headers(), timeout=20)

    if response.status_code == 404:
        return []

    response.raise_for_status()
    workflow_items = response.json()

    workflow_files = []

    for item in workflow_items:
        path = item.get("path")
        if not path:
            continue

        file_data = get_file_content(owner, repo, path)
        if file_data:
            workflow_files.append(file_data)

    return workflow_files