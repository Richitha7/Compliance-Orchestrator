from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
import asyncio, random

@dataclass
class AgentResult:
    data: Dict[str, Any]
    citations: list[dict]

class BaseAgent:
    name = "base"
    min_delay = 0.2
    max_delay = 0.8

    async def run(self, **kwargs) -> AgentResult:
        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
        return AgentResult(data={}, citations=[])
