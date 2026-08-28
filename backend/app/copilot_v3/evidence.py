from dataclasses import dataclass

@dataclass(frozen=True)
class Citation:
    source_id: str
    chunk_id: str
    score: float

class CitationFormatter:
    def format(self, citations: list[Citation]) -> list[dict]:
        return [
            {"source_id": c.source_id, "chunk_id": c.chunk_id, "score": round(c.score, 6)}
            for c in citations
        ]
