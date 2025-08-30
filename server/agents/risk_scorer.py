from __future__ import annotations
from .base import BaseAgent, AgentResult

class RiskScorer(BaseAgent):
    name = "risk_scorer"

    async def run(self, policy: dict, evidence: dict, vision: dict, code: dict) -> AgentResult:
        score = 0.5
        if any("MFA" in c for c in policy.get("policy_clauses", [])):
            score -= 0.1
        if any("MFA" in e for e in evidence.get("evidence", [])):
            score -= 0.1
        if "otp" in vision.get("ocr_text", "").lower():
            score -= 0.1
        if any(code.get("code_flags", [])):
            score -= 0.1
        score = max(0.0, min(1.0, score))
        return AgentResult(data={"risk_score": score}, citations=[])
