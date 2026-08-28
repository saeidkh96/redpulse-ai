from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any

class Predictor(Protocol):
    def predict(self, features: dict[str, float]) -> dict[str, Any]: ...

@dataclass(frozen=True)
class ModelKey:
    name: str
    version: str

class ProductionModelRouter:
    def __init__(self) -> None:
        self.models: dict[ModelKey, Predictor] = {}
        self.active: dict[str, ModelKey] = {}

    def register(self, key: ModelKey, predictor: Predictor) -> None:
        self.models[key] = predictor

    def activate(self, key: ModelKey) -> None:
        if key not in self.models:
            raise KeyError(key)
        self.active[key.name] = key

    def predict(self, name: str, features: dict[str, float]) -> dict:
        key = self.active[name]
        result = self.models[key].predict(features)
        return {"model": {"name": key.name, "version": key.version}, "prediction": result}
