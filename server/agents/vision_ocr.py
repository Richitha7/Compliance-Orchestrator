from __future__ import annotations
from .base import BaseAgent, AgentResult
from ..utils.ocr import ocr_image

class VisionOCR(BaseAgent):
    name = "vision_ocr"

    async def run(self, image_path: str | None) -> AgentResult:
        if not image_path:
            return AgentResult(data={"ocr_text": ""}, citations=[])
        text = ocr_image(image_path)
        cit = [{"doc_id": "artifact:"+image_path, "chunk_id": "ocr", "snippet": text[:160]}] if text else []
        return AgentResult(data={"ocr_text": text}, citations=cit)
