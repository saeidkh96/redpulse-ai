from __future__ import annotations
from pathlib import Path
from .hub import HuggingFaceHubAdapter

class ModelCache:
    def __init__(self, root: str | Path = "artifacts/huggingface/cache", hub: HuggingFaceHubAdapter | None = None) -> None:
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True); self.hub = hub or HuggingFaceHubAdapter()
    def pull(self, repo_id: str, revision: str | None = None) -> Path:
        return Path(self.hub.snapshot(repo_id, revision=revision, cache_dir=self.root))
