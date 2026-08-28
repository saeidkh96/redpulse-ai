from __future__ import annotations
import os

class SecretProvider:
    def get(self, name: str) -> str:
        raise NotImplementedError

class EnvironmentSecretProvider(SecretProvider):
    def get(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise KeyError(f"missing secret: {name}")
        return value
