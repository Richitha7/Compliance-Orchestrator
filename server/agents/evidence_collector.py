from __future__ import annotations
from .base import BaseAgent, AgentResult
from ..storage.vectorstore import vector_store
from ..utils.config import settings

class EvidenceCollector(BaseAgent):
    name = "evidence_collector"

    async def run(self, question: str) -> AgentResult:
        hits = vector_store.search("product " + question, settings.RAG_TOP_K)
        citations = []
        evidence = []
        for idx, score in hits:
            doc = vector_store.get_doc(idx)
            citations.append({"doc_id": doc["doc_id"], "chunk_id": doc["chunk_id"], "snippet": doc["text"][:160]})
            evidence.append(doc["text"])
        return AgentResult(data={"evidence": evidence}, citations=citations)
