from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class KnowledgeChunk:
    chunk_id: str
    source_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class RetrievedEvidence:
    chunk_id: str
    source_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
