from __future__ import annotations

from collections.abc import Callable
from typing import Any


InferenceHandler = Callable[[dict[str, Any]], dict[str, Any]]


class ModelServingRouter:
    def __init__(self) -> None:
        self._handlers: dict[tuple[str, str], InferenceHandler] = {}
        self._defaults: dict[str, str] = {}

    def register(self, model_name: str, version: str, handler: InferenceHandler, *, default: bool = False) -> None:
        self._handlers[(model_name, version)] = handler
        if default or model_name not in self._defaults:
            self._defaults[model_name] = version

    def set_default(self, model_name: str, version: str) -> None:
        if (model_name, version) not in self._handlers:
            raise LookupError(f"Model handler is not registered: {model_name}:{version}")
        self._defaults[model_name] = version

    def predict(self, model_name: str, payload: dict[str, Any], version: str | None = None) -> dict[str, Any]:
        resolved = version or self._defaults.get(model_name)
        if resolved is None:
            raise LookupError(f"No serving version configured for model: {model_name}")
        try:
            handler = self._handlers[(model_name, resolved)]
        except KeyError as exc:
            raise LookupError(f"Model handler is not registered: {model_name}:{resolved}") from exc
        result = handler(payload)
        return {
            "model_name": model_name,
            "version": resolved,
            "prediction": result,
        }
