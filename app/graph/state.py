from pydantic import BaseModel
from typing import Optional

class CivicState(BaseModel):
    complaint: str

    classification: Optional[dict] = None
    evidence: Optional[dict] = None
    department: Optional[str] = None
    response: Optional[str] = None
    task: Optional[dict] = None