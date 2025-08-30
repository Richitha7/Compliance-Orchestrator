from __future__ import annotations
from .base import AgentResult
from ..utils.config import settings

def aggregate(policy: AgentResult, evidence: AgentResult, vision: AgentResult, code: AgentResult, risk: AgentResult, critic: AgentResult):
    citations = policy.citations + evidence.citations + vision.citations
    open_questions = critic.data.get("open_questions", [])
    risk_score = risk.data["risk_score"]
    decision = "compliant" if risk_score < settings.RISK_THRESHOLD and not open_questions else "insufficient_evidence"
    rationale = "Risk below threshold and sufficient evidence." if decision == "compliant" else "Evidence incomplete or risk above threshold."
    return {
        "decision": decision,
        "confidence": 1.0 - risk_score,
        "risk_score": risk_score,
        "rationale": rationale,
        "citations": citations,
        "open_questions": open_questions,
        "human_interactions": []
    }
