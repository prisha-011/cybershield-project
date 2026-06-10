from pydantic import BaseModel, HttpUrl

class ScanRequest(BaseModel):
    repo_url: HttpUrl