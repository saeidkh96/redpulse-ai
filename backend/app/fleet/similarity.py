from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Mapping


@dataclass(frozen=True)
class MachineBehaviorProfile:
    machine_id: str
    machine_type: str | None
    manufacturer: str | None
    model: str | None
    dna: Mapping[str, float]
    operating_profile: Mapping[str, float]


@dataclass(frozen=True)
class MachineSimilarity:
    machine_id: str
    score: float
    metadata_score: float
    dna_score: float
    operating_score: float


class MachineSimilarityEngine:
    def compare(
        self,
        target: MachineBehaviorProfile,
        candidate: MachineBehaviorProfile,
    ) -> MachineSimilarity:
        metadata = self._metadata_similarity(target, candidate)
        dna = self._cosine(target.dna, candidate.dna)
        operating = self._cosine(target.operating_profile, candidate.operating_profile)

        available = []
        if target.dna and candidate.dna:
            available.append((dna, 0.50))
        if target.operating_profile and candidate.operating_profile:
            available.append((operating, 0.30))
        available.append((metadata, 0.20))

        total_weight = sum(weight for _, weight in available)
        score = sum(value * weight for value, weight in available) / total_weight

        return MachineSimilarity(
            machine_id=candidate.machine_id,
            score=round(self._clamp01(score), 4),
            metadata_score=round(metadata, 4),
            dna_score=round(dna, 4),
            operating_score=round(operating, 4),
        )

    def rank(
        self,
        target: MachineBehaviorProfile,
        candidates: list[MachineBehaviorProfile],
        *,
        minimum_similarity: float = 0.55,
        limit: int = 25,
    ) -> list[MachineSimilarity]:
        ranked = [
            self.compare(target, candidate)
            for candidate in candidates
            if candidate.machine_id != target.machine_id
        ]
        ranked = [item for item in ranked if item.score >= minimum_similarity]
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:limit]

    @staticmethod
    def _metadata_similarity(
        target: MachineBehaviorProfile,
        candidate: MachineBehaviorProfile,
    ) -> float:
        checks = [
            (target.machine_type, candidate.machine_type, 0.50),
            (target.manufacturer, candidate.manufacturer, 0.20),
            (target.model, candidate.model, 0.30),
        ]
        score = 0.0
        weight = 0.0
        for left, right, item_weight in checks:
            if left is None or right is None:
                continue
            weight += item_weight
            if left == right:
                score += item_weight
        return score / weight if weight else 0.25

    @staticmethod
    def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
        keys = set(left) & set(right)
        if not keys:
            return 0.0
        dot = sum(float(left[k]) * float(right[k]) for k in keys)
        left_norm = sqrt(sum(float(left[k]) ** 2 for k in keys))
        right_norm = sqrt(sum(float(right[k]) ** 2 for k in keys))
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        cosine = dot / (left_norm * right_norm)
        return max(0.0, min(1.0, cosine))

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))


machine_similarity_engine = MachineSimilarityEngine()
