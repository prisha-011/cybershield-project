from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ScanCreate(BaseModel):
    repo_url: HttpUrl
    repo_name: Optional[str] = None
    owner: Optional[str] = None
    branch: str = "main"


class ScanInDB(BaseModel):
    repo_url: str
    repo_name: Optional[str] = None
    owner: Optional[str] = None
    branch: str = "main"
    status: str = "pending"
    overall_score: Optional[int] = None
    summary_counts: dict = Field(
        default_factory=lambda: {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None