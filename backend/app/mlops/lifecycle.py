from __future__ import annotations

from dataclasses import dataclass

from app.mlops.registry import ModelRegistry


@dataclass(frozen=True)
class PromotionResult:
    model_name: str
    promoted_version: str
    archived_versions: list[str]


class ModelLifecycleManager:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def promote_to_champion(self, model_name: str, version: str) -> PromotionResult:
        archived = []
        for item in self.registry.list_versions(model_name):
            if item.stage == "champion" and item.version != version:
                self.registry.transition_stage(model_name, item.version, "archived")
                archived.append(item.version)
        self.registry.transition_stage(model_name, version, "champion")
        return PromotionResult(
            model_name=model_name,
            promoted_version=version,
            archived_versions=archived,
        )
