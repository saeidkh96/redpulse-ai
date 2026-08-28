from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelMetadata:
    repo_id: str
    revision: str | None = None
    pipeline_tag: str | None = None
    library_name: str | None = None
    tags: tuple[str, ...] = ()

class ModelCardSync:
    def normalize(self, info) -> ModelMetadata:
        card = getattr(info, "card_data", None)
        tags = tuple(getattr(info, "tags", None) or ())
        return ModelMetadata(repo_id=getattr(info, "id", "unknown"), revision=getattr(info, "sha", None), pipeline_tag=getattr(info, "pipeline_tag", None), library_name=getattr(info, "library_name", None), tags=tags)
