from __future__ import annotations
from pathlib import Path

class HuggingFaceHubAdapter:
    """Optional Hugging Face Hub boundary. huggingface_hub is imported lazily."""
    def __init__(self, token: str | None = None) -> None: self.token = token
    def model_info(self, repo_id: str):
        try: from huggingface_hub import HfApi
        except ImportError as exc: raise RuntimeError("Install requirements-huggingface.txt") from exc
        return HfApi(token=self.token).model_info(repo_id)
    def snapshot(self, repo_id: str, revision: str | None = None, cache_dir: str | Path | None = None) -> str:
        try: from huggingface_hub import snapshot_download
        except ImportError as exc: raise RuntimeError("Install requirements-huggingface.txt") from exc
        return snapshot_download(repo_id=repo_id, revision=revision, cache_dir=str(cache_dir) if cache_dir else None, token=self.token)
