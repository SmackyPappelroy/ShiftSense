from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    customer: str
    site: Optional[str] = None


class WorkspaceOut(BaseModel):
    id: int
    name: str
    customer: str
    site: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class FindingOut(BaseModel):
    id: int
    category: str
    severity: str
    confidence: float
    title: str
    description: str
    evidence: List[Dict[str, Any]]
    recommendation: str
    expected_gain: Optional[str]
    risk: Optional[str]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
