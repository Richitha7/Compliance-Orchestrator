from __future__ import annotations
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

Decision = Literal["compliant", "non_compliant", "insufficient_evidence"]

class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    snippet: str

class HumanInteraction(BaseModel):
    timestamp: str
    type: Literal["clarification", "approval", "upload_request"]
    prompt: str
    response: str
    status: Literal["approved", "denied", "provided", "timeout"]

class FinalDecision(BaseModel):
    decision: Decision
    confidence: float
    risk_score: float
    rationale: str
    citations: List[Citation]
    open_questions: List[str]
    human_interactions: List[HumanInteraction]

class HitlRequest(BaseModel):
    session_id: str
    request_id: str
    type: Literal["clarification", "approval", "upload_request"]
    prompt: str
    required_artifact: Optional[Literal["image","text"]] = None

class HitlResponse(BaseModel):
    session_id: str
    request_id: str
    response_type: Literal["clarification","approval","upload"]
    payload: Optional[str] = None

class ProgressUpdate(BaseModel):
    stage: str
    status: str
    meta: Dict[str, Any] = {}

class AskRequest(BaseModel):
    session_id: str
    question: str
    attachments: Optional[List[str]] = None

class AskResponse(BaseModel):
    job_id: str

class HistoryEntry(BaseModel):
    timestamp: str
    event: str
    data: Dict[str, Any] = {}

class SessionHistory(BaseModel):
    session_id: str
    entries: List[HistoryEntry] = []
