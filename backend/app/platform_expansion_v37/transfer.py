from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TransferCandidate:
    source_machine_id: str
    target_machine_id: str
    similarity: float
    source_evidence_score: float
    source_sample_count: int


@dataclass(frozen=True, slots=True)
class TransferDecision:
    accepted: bool
    confidence: float
    reason: str


class FleetKnowledgeTransferGate:
    def evaluate(
        self,
        candidate: TransferCandidate,
        *,
        min_similarity: float = 0.75,
        min_evidence_score: float = 0.60,
        min_samples: int = 5,
    ) -> TransferDecision:
        similarity = max(0.0, min(1.0, float(candidate.similarity)))
        evidence = max(0.0, min(1.0, float(candidate.source_evidence_score)))
        support = min(1.0, max(0, candidate.source_sample_count) / max(1, min_samples * 2))
        confidence = (similarity * 0.50) + (evidence * 0.35) + (support * 0.15)

        checks = {
            "similarity": similarity >= min_similarity,
            "evidence": evidence >= min_evidence_score,
            "support": candidate.source_sample_count >= min_samples,
        }
        accepted = all(checks.values())
        reason = "transfer_supported" if accepted else "insufficient_transfer_evidence"
        return TransferDecision(accepted=accepted, confidence=round(confidence, 4), reason=reason)
