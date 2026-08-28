from __future__ import annotations
import math
import re
from collections import Counter
from .models import KnowledgeChunk, RetrievedEvidence

_TOKEN = re.compile(r"[A-Za-z0-9_\-]+")

def _vector(text: str) -> Counter[str]:
    return Counter(t.lower() for t in _TOKEN.findall(text))

def _cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0

class InMemoryKnowledgeStore:
    def __init__(self) -> None:
        self._chunks: dict[str, KnowledgeChunk] = {}

    def upsert(self, chunks: list[KnowledgeChunk]) -> int:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk
        return len(chunks)

    def search(self, query: str, limit: int = 5) -> list[RetrievedEvidence]:
        q = _vector(query)
        ranked = []
        for chunk in self._chunks.values():
            score = _cosine(q, _vector(chunk.text))
            if score > 0:
                ranked.append(RetrievedEvidence(
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    text=chunk.text,
                    score=round(score, 6),
                    metadata=chunk.metadata,
                ))
        return sorted(ranked, key=lambda x: x.score, reverse=True)[:limit]

    def count(self) -> int:
        return len(self._chunks)
