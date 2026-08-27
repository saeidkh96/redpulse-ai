from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaintenancePriorityInput:
    machine_id: str
    health_score: float
    failure_risk: float
    drift_score: float
    trajectory_score: float
    counterfactual_benefit: float
    maintenance_urgency: float
    peer_evidence_confidence: float = 0.0


@dataclass(frozen=True)
class MaintenancePriority:
    rank: int
    machine_id: str
    priority_score: float
    priority_band: str
    reason_codes: list[str]


class FleetMaintenancePrioritizationEngine:
    def prioritize(
        self,
        machines: list[MaintenancePriorityInput],
        *,
        capacity: int | None = None,
    ) -> list[MaintenancePriority]:
        scored = []
        for item in machines:
            health_pressure = 1.0 - self._clamp01(item.health_score / 100.0)
            score = (
                self._clamp01(item.failure_risk) * 0.30
                + health_pressure * 0.18
                + self._clamp01(item.drift_score) * 0.12
                + self._clamp01(item.trajectory_score) * 0.14
                + self._clamp01(item.counterfactual_benefit) * 0.14
                + self._clamp01(item.maintenance_urgency) * 0.08
                + self._clamp01(item.peer_evidence_confidence) * 0.04
            )
            scored.append((item, self._clamp01(score)))

        scored.sort(key=lambda pair: pair[1], reverse=True)
        if capacity is not None:
            scored = scored[: max(0, capacity)]

        priorities = []
        for index, (item, score) in enumerate(scored, start=1):
            reasons = self._reason_codes(item)
            priorities.append(
                MaintenancePriority(
                    rank=index,
                    machine_id=item.machine_id,
                    priority_score=round(score, 4),
                    priority_band=self._band(score),
                    reason_codes=reasons,
                )
            )
        return priorities

    def _reason_codes(self, item: MaintenancePriorityInput) -> list[str]:
        reasons = []
        if item.failure_risk >= 0.75:
            reasons.append("HIGH_FAILURE_RISK")
        if item.health_score <= 40.0:
            reasons.append("LOW_HEALTH")
        if item.drift_score >= 0.65:
            reasons.append("STRONG_DRIFT")
        if item.trajectory_score >= 0.70:
            reasons.append("FAILURE_TRAJECTORY_MATCH")
        if item.counterfactual_benefit >= 0.60:
            reasons.append("HIGH_EXPECTED_MAINTENANCE_BENEFIT")
        if item.maintenance_urgency >= 0.70:
            reasons.append("HIGH_MAINTENANCE_URGENCY")
        if item.peer_evidence_confidence >= 0.70:
            reasons.append("STRONG_CROSS_MACHINE_EVIDENCE")
        return reasons or ["COMPOSITE_FLEET_RISK"]

    @staticmethod
    def _band(score: float) -> str:
        if score >= 0.75:
            return "critical"
        if score >= 0.55:
            return "high"
        if score >= 0.35:
            return "medium"
        return "low"

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))


fleet_maintenance_prioritization_engine = FleetMaintenancePrioritizationEngine()
