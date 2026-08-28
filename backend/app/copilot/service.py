from __future__ import annotations
from typing import Protocol
from app.knowledge.store import InMemoryKnowledgeStore
from .context import MachineContext

class Generator(Protocol):
    def generate(self, prompt: str) -> str: ...

class EvidenceGroundedCopilot:
    def __init__(self, store: InMemoryKnowledgeStore, generator: Generator | None = None) -> None:
        self.store = store
        self.generator = generator

    def answer(self, question: str, context: MachineContext, limit: int = 5) -> dict:
        evidence = self.store.search(question, limit)
        citations = [
            {"source_id": e.source_id, "chunk_id": e.chunk_id, "score": e.score}
            for e in evidence
        ]
        evidence_text = "\n\n".join(
            f"[{i+1}] {e.source_id}: {e.text}" for i, e in enumerate(evidence)
        )
        prompt = (
            "You are RedPulse Industrial AI Copilot. Use only the supplied machine context "
            "and evidence. If evidence is insufficient, say so.\n\n"
            f"MACHINE CONTEXT\n{context.as_prompt_context()}\n\n"
            f"EVIDENCE\n{evidence_text or 'No retrieved evidence.'}\n\n"
            f"QUESTION\n{question}"
        )
        if self.generator:
            answer = self.generator.generate(prompt)
        else:
            answer = (
                "Evidence-grounded context prepared. Connect the configured Hugging Face/model "
                "gateway to generate the final natural-language response."
            )
        return {"answer": answer, "citations": citations, "evidence_count": len(evidence)}
