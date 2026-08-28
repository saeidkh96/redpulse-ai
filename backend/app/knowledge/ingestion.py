from __future__ import annotations
import hashlib
from .models import KnowledgeChunk

class KnowledgeIngestionService:
    def __init__(self, chunk_size: int = 900, overlap: int = 120) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, source_id: str, text: str, metadata: dict | None = None) -> list[KnowledgeChunk]:
        clean = " ".join(text.split())
        if not clean:
            return []
        step = self.chunk_size - self.overlap
        chunks = []
        for i, start in enumerate(range(0, len(clean), step)):
            part = clean[start:start + self.chunk_size]
            if not part:
                break
            digest = hashlib.sha1(f"{source_id}:{i}:{part}".encode()).hexdigest()[:16]
            chunks.append(KnowledgeChunk(
                chunk_id=digest,
                source_id=source_id,
                text=part,
                metadata={**(metadata or {}), "chunk_index": i},
            ))
            if start + self.chunk_size >= len(clean):
                break
        return chunks
