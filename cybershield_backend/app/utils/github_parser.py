from urllib.parse import urlparse


def parse_github_repo_url(repo_url: str) -> dict:
    parsed = urlparse(str(repo_url))

    if parsed.scheme not in ["http", "https"]:
        raise ValueError("Only HTTP/HTTPS GitHub URLs are supported.")

    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only github.com repository URLs are allowed.")

    path_parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL format.")

    owner = path_parts[0]
    repo = path_parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    normalized_url = f"https://github.com/{owner}/{repo}"

    return {
        "owner": owner,
        "repo": repo,
        "normalized_url": normalized_url
    }