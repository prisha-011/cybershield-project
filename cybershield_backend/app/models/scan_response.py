from typing import List, Literal

from pydantic import BaseModel


class FindingResponse(BaseModel):
    severity: Literal["high", "medium", "low", "info"]
    type: str
    title: str
    description: str
    remediation: str | None = None
    source: Literal["rule", "ai"] = "rule"


class RepositoryInfoResponse(BaseModel):
    full_name: str | None = None
    private: bool | None = None
    default_branch: str | None = None
    language: str | None = None
    stargazers_count: int | None = None
    forks_count: int | None = None
    open_issues_count: int | None = None


class RootContentItemResponse(BaseModel):
    name: str
    type: str
    path: str


class ImportantFileResponse(BaseModel):
    path: str
    logical_name: str | None = None
    exists: bool
    size: int | None = None
    type: str | None = None
    content: str | None = None


class FindingsSummaryResponse(BaseModel):
    total: int
    high: int
    medium: int
    low: int
    info: int


class ScanResponse(BaseModel):
    message: str
    repo_url: str
    owner: str
    repo: str
    normalized_url: str
    repository: RepositoryInfoResponse
    root_contents: List[RootContentItemResponse]
    important_files: List[ImportantFileResponse]
    workflow_files: List[ImportantFileResponse]
    rule_based_findings: List[FindingResponse]
    ai_findings: List[FindingResponse]
    ai_analysis_status: str
    ai_analysis_error: str | None = None
    findings_summary: FindingsSummaryResponse
    findings: List[FindingResponse]