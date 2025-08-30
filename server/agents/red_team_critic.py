from __future__ import annotations
from .base import BaseAgent, AgentResult

class RedTeamCritic(BaseAgent):
    name = "red_team_critic"

    async def run(self, merged: dict) -> AgentResult:
        open_q = []
        if not merged.get("vision", {}).get("ocr_text"):
            open_q.append("Missing screenshot evidence for MFA configuration.")
        if not merged.get("code", {}).get("code_flags"):
            open_q.append("No code/config proof of MFA enforcement.")
        return AgentResult(data={"open_questions": open_q}, citations=[])
