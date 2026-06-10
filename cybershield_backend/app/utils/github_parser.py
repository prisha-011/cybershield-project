from urllib.parse import urlparse


def parse_github_repo_url(url: str) -> dict:
    parsed = urlparse(url)

    if parsed.netloc not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub repository URLs are supported")

    path_parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL")

    owner = path_parts[0]
    repo = path_parts[1].replace(".git", "")

    return {
        "owner": owner,
        "repo": repo,
        "normalized_url": f"https://github.com/{owner}/{repo}"
    }