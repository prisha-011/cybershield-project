import base64
import httpx
from fastapi import HTTPException
from app.config import settings


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

    response = httpx.get(url, headers=get_github_headers(), timeout=20.0)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Repository not found on GitHub.")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch repository metadata.")

    return response.json()


def get_repository_root_contents(owner: str, repo: str) -> list:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents"

    response = httpx.get(url, headers=get_github_headers(), timeout=20.0)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Repository contents not found.")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch repository contents.")

    return response.json()


def get_file_content(owner: str, repo: str, path: str) -> dict:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"

    response = httpx.get(url, headers=get_github_headers(), timeout=20.0)

    if response.status_code == 404:
        return {"exists": False, "path": path, "content": None}

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to fetch file: {path}")

    return response.json()


def decode_github_file_content(file_data: dict) -> str | None:
    if not file_data or not file_data.get("content"):
        return None

    encoding = file_data.get("encoding")
    content = file_data.get("content")

    if encoding == "base64":
        try:
            decoded_bytes = base64.b64decode(content)
            return decoded_bytes.decode("utf-8", errors="replace")
        except Exception:
            return None

    return content


def get_important_files(owner: str, repo: str) -> list:
    important_paths = [
        "README.md",
        "README",
        "package.json",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "Dockerfile",
    ]

    results = []
    seen_logical_names = set()

    for path in important_paths:
        logical_name = "README" if path.lower() in ["readme", "readme.md"] else path

        if logical_name in seen_logical_names:
            continue

        file_data = get_file_content(owner, repo, path)

        if not file_data.get("exists", True):
            continue

        decoded_content = decode_github_file_content(file_data)

        results.append({
            "path": path,
            "logical_name": logical_name,
            "exists": True,
            "size": file_data.get("size"),
            "type": file_data.get("type"),
            "content": decoded_content[:3000] if decoded_content else None
        })

        seen_logical_names.add(logical_name)

    for path in important_paths:
        logical_name = "README" if path.lower() in ["readme", "readme.md"] else path

        if logical_name not in seen_logical_names:
            results.append({
                "path": path,
                "logical_name": logical_name,
                "exists": False,
                "content": None
            })
            seen_logical_names.add(logical_name)

    return results

    


def get_directory_contents(owner: str, repo: str, path: str) -> list:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"

    response = httpx.get(url, headers=get_github_headers(), timeout=20.0)

    if response.status_code == 404:
        return []

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to fetch directory contents: {path}")

    data = response.json()

    if isinstance(data, list):
        return data

    return []


def get_github_workflow_files(owner: str, repo: str) -> list:
    workflow_dir = ".github/workflows"
    workflow_items = get_directory_contents(owner, repo, workflow_dir)

    results = []

    for item in workflow_items:
        if item.get("type") != "file":
            continue

        path = item.get("path")

        try:
            file_data = get_file_content(owner, repo, path)
            decoded_content = decode_github_file_content(file_data)

            results.append({
                "name": item.get("name"),
                "path": path,
                "exists": True,
                "size": file_data.get("size"),
                "type": file_data.get("type"),
                "content": decoded_content[:5000] if decoded_content else None
            })
        except Exception:
            results.append({
                "name": item.get("name"),
                "path": path,
                "exists": False,
                "size": None,
                "type": "file",
                "content": None
            })

    return results