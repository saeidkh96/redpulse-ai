from __future__ import annotations

class IndustrialCopilotV2:
    def __init__(self, retriever, generator=None) -> None:
        self.retriever = retriever
        self.generator = generator

    def answer(self, question: str, machine_context: dict, limit: int = 5) -> dict:
        evidence = self.retriever.search(question, limit)
        citations = [
            {"source_id": e.source_id, "chunk_id": e.chunk_id, "score": e.score}
            for e in evidence
        ]
        prompt = {
            "question": question,
            "machine_context": machine_context,
            "evidence": [e.text for e in evidence],
        }
        if self.generator:
            answer = self.generator.generate(str(prompt))
        else:
            answer = "Evidence prepared; connect an approved model provider for final generation."
        return {"answer": answer, "citations": citations, "evidence_count": len(evidence)}
