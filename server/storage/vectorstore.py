from __future__ import annotations
import os, json, numpy as np
from typing import List, Tuple, Dict
from ..utils.config import settings

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None  # type: ignore

try:
    import faiss  # type: ignore
except Exception:
    faiss = None  # type: ignore

class VectorStore:
    def __init__(self):
        self.model = None
        self.index = None
        self.docs: List[Dict] = []
        os.makedirs(settings.INDEX_DIR, exist_ok=True)

    def load_model(self):
        if SentenceTransformer and self.model is None:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def _embed(self, texts: List[str]) -> np.ndarray:
        if self.model is None:
            self.load_model()
        if self.model:
            return np.array(self.model.encode(texts, normalize_embeddings=True), dtype="float32")
        # crude fallback: bag-of-chars
        return np.array([np.frombuffer(t.encode('utf-8'), dtype=np.uint8)[:64].astype('float32').mean() * np.ones(384) for t in texts], dtype="float32")

    def add_documents(self, docs: List[Dict]):
        self.docs.extend(docs)
        embeddings = self._embed([d["text"] for d in docs])
        if faiss:
            if self.index is None:
                self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)

    def search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        q = self._embed([query])
        if faiss and self.index is not None:
            sims, idxs = self.index.search(q, top_k)
            return [(int(idxs[0][i]), float(sims[0][i])) for i in range(min(top_k, len(self.docs)))]
        # numpy fallback
        E = self._embed([d["text"] for d in self.docs])
        sims = (E @ q.T).squeeze()
        idxs = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i])) for i in idxs]

    def get_doc(self, idx: int) -> Dict:
        return self.docs[idx]

vector_store = VectorStore()
