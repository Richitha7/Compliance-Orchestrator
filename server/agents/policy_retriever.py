from __future__ import annotations
from .base import BaseAgent, AgentResult
from ..storage.vectorstore import vector_store
from ..utils.config import settings

class PolicyRetriever(BaseAgent):
    name = "policy_retriever"

    async def run(self, question: str, top_k: int | None = None) -> AgentResult:
        top_k = top_k or settings.RAG_TOP_K
        hits = vector_store.search(question, top_k)
        citations = []
        clauses = []
        for idx, score in hits:
            doc = vector_store.get_doc(idx)
            citations.append({"doc_id": doc["doc_id"], "chunk_id": doc["chunk_id"], "snippet": doc["text"][:160]})
            clauses.append(doc["text"])
        return AgentResult(data={"policy_clauses": clauses}, citations=citations)
