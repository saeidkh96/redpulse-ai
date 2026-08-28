from __future__ import annotations
class HuggingFaceEmbeddingAdapter:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None: self.model_name=model_name; self._model=None
    def _load(self):
        if self._model is None:
            try: from sentence_transformers import SentenceTransformer
            except ImportError as exc: raise RuntimeError("Install sentence-transformers") from exc
            self._model=SentenceTransformer(self.model_name)
        return self._model
    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors=self._load().encode(texts, normalize_embeddings=True)
        return vectors.tolist()
