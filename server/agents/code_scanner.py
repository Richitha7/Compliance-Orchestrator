from __future__ import annotations
from .base import BaseAgent, AgentResult

class CodeScanner(BaseAgent):
    name = "code_scanner"

    async def run(self, code_snippets: list[str] | None) -> AgentResult:
        code_snippets = code_snippets or []
        flags = []
        for i, code in enumerate(code_snippets):
            if "MFA" in code or "two_factor" in code:
                flags.append({"index": i, "finding": "Found MFA reference"})
        return AgentResult(data={"code_flags": flags}, citations=[])
