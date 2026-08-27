from dataclasses import dataclass
from enum import Enum

from app.maintenance.outcome import LearnedInterventionProfile


class CrossMachineEvidenceScope(str, Enum):
    PEER_GROUP = "peer_group"
    MACHINE_TYPE = "machine_type"
    GLOBAL = "global"


@dataclass(frozen=True)
class PeerMachineEvidence:
    machine_id: str
    machine_type: str | None
    manufacturer: str | None
    model: str | None
    similarity_score: float
    intervention_type: str
    outcome_score: float
    outcome_label: str | None


@dataclass(frozen=True)
class CrossMachineInterventionEvidence:
    intervention_type: str
    peer_support: int
    weighted_success_score: float
    weighted_similarity: float
    historical_profile: LearnedInterventionProfile | None
    evidence_score: float


@dataclass(frozen=True)
class CrossMachineRecommendation:
    target_machine_id: str
    machine_type: str | None
    evidence_scope: CrossMachineEvidenceScope
    peer_count: int
    interventions: list[CrossMachineInterventionEvidence]
    recommended_intervention: str | None
    recommendation_confidence: float


class CrossMachineLearningEngine:
    def analyze(
        self,
        *,
        target_machine_id: str,
        machine_type: str | None,
        peer_evidence: list[PeerMachineEvidence],
        historical_profiles: list[LearnedInterventionProfile],
        evidence_scope: CrossMachineEvidenceScope,
    ) -> CrossMachineRecommendation:
        profile_by_type = {
            profile.intervention_type: profile for profile in historical_profiles
        }
        grouped: dict[str, list[PeerMachineEvidence]] = {}
        for item in peer_evidence:
            grouped.setdefault(item.intervention_type, []).append(item)

        intervention_types = set(grouped) | set(profile_by_type)
        ranked: list[CrossMachineInterventionEvidence] = []

        for intervention_type in intervention_types:
            peers = grouped.get(intervention_type, [])
            profile = profile_by_type.get(intervention_type)

            total_similarity = sum(max(0.0, p.similarity_score) for p in peers)
            if total_similarity > 0:
                weighted_success = sum(
                    max(-1.0, min(1.0, p.outcome_score))
                    * max(0.0, p.similarity_score)
                    for p in peers
                ) / total_similarity
                weighted_similarity = total_similarity / len(peers)
            else:
                weighted_success = 0.0
                weighted_similarity = 0.0

            peer_component = self._clamp01(
                (max(0.0, weighted_success) * 0.65)
                + (weighted_similarity * 0.35)
            )

            if profile is None:
                historical_component = 0.0
                profile_confidence = 0.0
            else:
                historical_component = self._clamp01(
                    (max(0.0, profile.average_recovery_score) * 0.45)
                    + (profile.success_rate * 0.35)
                    + (profile.confidence * 0.20)
                )
                profile_confidence = self._clamp01(profile.confidence)

            support_factor = self._clamp01((len(peers) + (profile.sample_count if profile else 0)) / 20.0)
            scope_factor = {
                CrossMachineEvidenceScope.PEER_GROUP: 1.0,
                CrossMachineEvidenceScope.MACHINE_TYPE: 0.90,
                CrossMachineEvidenceScope.GLOBAL: 0.75,
            }[evidence_scope]

            evidence_score = self._clamp01(
                (
                    (peer_component * 0.60)
                    + (historical_component * 0.40)
                )
                * (0.60 + (0.40 * support_factor))
                * scope_factor
            )

            ranked.append(
                CrossMachineInterventionEvidence(
                    intervention_type=intervention_type,
                    peer_support=len(peers),
                    weighted_success_score=round(weighted_success, 4),
                    weighted_similarity=round(weighted_similarity, 4),
                    historical_profile=profile,
                    evidence_score=round(evidence_score, 4),
                )
            )

        ranked.sort(
            key=lambda item: (
                item.evidence_score,
                item.peer_support,
                item.weighted_similarity,
            ),
            reverse=True,
        )

        best = ranked[0] if ranked else None
        confidence = 0.0
        if best is not None:
            profile_confidence = (
                best.historical_profile.confidence
                if best.historical_profile is not None
                else 0.0
            )
            confidence = self._clamp01(
                (best.evidence_score * 0.65)
                + (best.weighted_similarity * 0.20)
                + (profile_confidence * 0.15)
            )

        return CrossMachineRecommendation(
            target_machine_id=target_machine_id,
            machine_type=machine_type,
            evidence_scope=evidence_scope,
            peer_count=len({item.machine_id for item in peer_evidence}),
            interventions=ranked,
            recommended_intervention=best.intervention_type if best else None,
            recommendation_confidence=round(confidence, 4),
        )

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))


cross_machine_learning_engine = CrossMachineLearningEngine()
