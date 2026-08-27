import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.fleet.cross_machine import (
    CrossMachineEvidenceScope,
    CrossMachineRecommendation,
    PeerMachineEvidence,
    cross_machine_learning_engine,
)
from app.models.machine import Machine
from app.repositories.cross_machine import cross_machine_repository
from app.services.maintenance_outcome import maintenance_outcome_service


@dataclass(frozen=True)
class CrossMachineLearningResult:
    machine_id: uuid.UUID
    recommendation: CrossMachineRecommendation
    evidence_note: str


class CrossMachineLearningService:
    async def analyze(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        peer_limit: int = 100,
        history_limit: int = 1000,
    ) -> CrossMachineLearningResult:
        target = await cross_machine_repository.get_machine(
            session,
            machine_id=machine_id,
        )
        if target is None:
            raise LookupError(f"Machine {machine_id} was not found")

        peers = await cross_machine_repository.list_peer_machines(
            session,
            target=target,
            limit=peer_limit,
        )

        peer_evidence = await self._build_peer_evidence(
            session,
            target=target,
            peers=peers,
            history_limit=history_limit,
        )

        profiles, scope = await self._load_profiles(
            session,
            target=target,
            history_limit=history_limit,
            has_peers=bool(peers),
        )

        recommendation = cross_machine_learning_engine.analyze(
            target_machine_id=str(target.id),
            machine_type=target.machine_type,
            peer_evidence=peer_evidence,
            historical_profiles=profiles,
            evidence_scope=scope,
        )

        return CrossMachineLearningResult(
            machine_id=machine_id,
            recommendation=recommendation,
            evidence_note=(
                "Cross-machine evidence is derived from completed maintenance outcomes "
                "of comparable machines. v0.6.0 uses deterministic metadata similarity "
                "and machine-type history; behavioral peer grouping is planned separately."
            ),
        )

    async def _build_peer_evidence(
        self,
        session: AsyncSession,
        *,
        target: Machine,
        peers: list[Machine],
        history_limit: int,
    ) -> list[PeerMachineEvidence]:
        peer_by_id = {peer.id: peer for peer in peers}
        records = await cross_machine_repository.list_completed_interventions_for_machines(
            session,
            machine_ids=list(peer_by_id),
            limit=history_limit,
        )

        evidence: list[PeerMachineEvidence] = []
        for record in records:
            peer = peer_by_id.get(record.machine_id)
            if peer is None:
                continue

            verification = record.verification_result or {}
            if "recovery_score" not in verification:
                continue

            evidence.append(
                PeerMachineEvidence(
                    machine_id=str(peer.id),
                    machine_type=peer.machine_type,
                    manufacturer=peer.manufacturer,
                    model=peer.model,
                    similarity_score=self._metadata_similarity(target, peer),
                    intervention_type=record.intervention_type,
                    outcome_score=float(verification.get("recovery_score", 0.0)),
                    outcome_label=record.outcome_label,
                )
            )
        return evidence

    async def _load_profiles(
        self,
        session: AsyncSession,
        *,
        target: Machine,
        history_limit: int,
        has_peers: bool,
    ):
        if target.machine_type is not None:
            profiles = await maintenance_outcome_service.learn(
                session,
                machine_type=target.machine_type,
                limit=history_limit,
            )
            if profiles:
                scope = (
                    CrossMachineEvidenceScope.PEER_GROUP
                    if has_peers
                    else CrossMachineEvidenceScope.MACHINE_TYPE
                )
                return profiles, scope

        profiles = await maintenance_outcome_service.learn(
            session,
            limit=history_limit,
        )
        return profiles, CrossMachineEvidenceScope.GLOBAL

    @staticmethod
    def _metadata_similarity(target: Machine, peer: Machine) -> float:
        score = 0.0
        weight = 0.0

        if target.machine_type is not None and peer.machine_type is not None:
            weight += 0.50
            if target.machine_type == peer.machine_type:
                score += 0.50

        if target.manufacturer is not None and peer.manufacturer is not None:
            weight += 0.20
            if target.manufacturer == peer.manufacturer:
                score += 0.20

        if target.model is not None and peer.model is not None:
            weight += 0.30
            if target.model == peer.model:
                score += 0.30

        if weight == 0.0:
            return 0.25
        return round(score / weight, 4)


cross_machine_learning_service = CrossMachineLearningService()
