from typing import List, Literal, Optional

from pydantic import BaseModel


class FindingResponse(BaseModel):
    severity: Literal["high", "medium", "low", "info"]
    type: str
    title: str
    description: str
    remediation: Optional[str] = None
    source: Literal["rule", "ai"]


class RepositoryInfoResponse(BaseModel):
    full_name: Optional[str] = None
    private: Optional[bool] = None
    default_branch: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: Optional[int] = None
    forks_count: Optional[int] = None
    open_issues_count: Optional[int] = None


class RootContentItemResponse(BaseModel):
    name: str
    type: str
    path: str


class ImportantFileResponse(BaseModel):
    path: str
    logical_name: Optional[str] = None
    exists: bool
    size: Optional[int] = None
    type: Optional[str] = None
    content: Optional[str] = None


class FindingsSummaryResponse(BaseModel):
    total: int
    high: int
    medium: int
    low: int
    info: int


class ScanResponse(BaseModel):
    scan_id: Optional[str] = None
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
    ai_analysis_error: Optional[str] = None
    findings_summary: FindingsSummaryResponse
    findings: List[FindingResponse]
    