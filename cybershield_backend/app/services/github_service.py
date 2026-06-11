import base64
import requests

from fastapi import HTTPException

from cybershield_backend.app.config import settings


GITHUB_API_BASE = "https://api.github.com"
IMPORTANT_FILE_CONTENT_LIMIT = 800
WORKFLOW_FILE_CONTENT_LIMIT = 1200


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

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Repository not found on GitHub.")

    response.raise_for_status()
    return response.json()


def get_repository_root_contents(owner: str, repo: str) -> list:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents"
    response = requests.get(url, headers=get_github_headers(), timeout=20)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Repository contents not found.")

    response.raise_for_status()
    data = response.json()

    if isinstance(data, list):
        return data

    return []


def decode_github_file_content(data: dict) -> str | None:
    content = data.get("content")
    encoding = data.get("encoding")

    if not content:
        return None

    if encoding == "base64":
        try:
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        except Exception:
            return None

    return content


def get_file_content(owner: str, repo: str, path: str, content_limit: int = 800) -> dict:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=get_github_headers(), timeout=20)

    if response.status_code == 404:
        return {
            "path": path,
            "logical_name": path.split("/")[-1],
            "exists": False,
            "size": None,
            "type": "file",
            "content": None,
        }

    response.raise_for_status()

    try:
        data = response.json()
    except Exception:
        return {
            "path": path,
            "logical_name": path.split("/")[-1],
            "exists": False,
            "size": None,
            "type": "file",
            "content": None,
        }

    decoded_content = decode_github_file_content(data)

    return {
        "path": data.get("path", path),
        "logical_name": path.split("/")[-1],
        "exists": True,
        "size": data.get("size"),
        "type": data.get("type"),
        "content": decoded_content[:content_limit] if decoded_content else None,
    }


def get_important_files(owner: str, repo: str) -> list:
    important_paths = [
        "README.md",
        "README",
        "requirements.txt",
        "package.json",
        "Dockerfile",
        ".env",
        ".env.example",
        ".gitignore",
        "docker-compose.yml",
        "pyproject.toml",
    ]

    files = []
    seen_logical_names = set()

    for path in important_paths:
        file_data = get_file_content(
            owner=owner,
            repo=repo,
            path=path,
            content_limit=IMPORTANT_FILE_CONTENT_LIMIT,
        )

        logical_name = "README" if path.lower() in {"readme", "readme.md"} else file_data["logical_name"]

        if logical_name in seen_logical_names:
            continue

        file_data["logical_name"] = logical_name
        files.append(file_data)
        seen_logical_names.add(logical_name)

    return files


def get_directory_contents(owner: str, repo: str, path: str) -> list:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=get_github_headers(), timeout=20)

    if response.status_code == 404:
        return []

    response.raise_for_status()
    data = response.json()

    if isinstance(data, list):
        return data

    return []


def get_github_workflow_files(owner: str, repo: str) -> list:
    workflow_items = get_directory_contents(owner, repo, ".github/workflows")
    workflow_files = []

    for item in workflow_items:
        if item.get("type") != "file":
            continue

        path = item.get("path")
        if not path:
            continue

        file_data = get_file_content(
            owner=owner,
            repo=repo,
            path=path,
            content_limit=WORKFLOW_FILE_CONTENT_LIMIT,
        )

        workflow_files.append({
            "name": item.get("name"),
            "path": file_data.get("path"),
            "logical_name": file_data.get("logical_name"),
            "exists": file_data.get("exists"),
            "size": file_data.get("size"),
            "type": file_data.get("type"),
            "content": file_data.get("content"),
        })

    return workflow_files