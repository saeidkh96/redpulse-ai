from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MachineFleetState:
    machine_id: str
    health_score: float
    failure_risk: float
    drift_score: float
    anomaly_score: float = 0.0


@dataclass(frozen=True)
class FleetHealthSummary:
    machine_count: int
    fleet_health_score: float
    fleet_risk_score: float
    critical_machine_count: int
    degraded_machine_count: int
    healthy_machine_count: int
    machines: list[MachineFleetState]


class FleetHealthEngine:
    def summarize(self, machines: list[MachineFleetState]) -> FleetHealthSummary:
        if not machines:
            return FleetHealthSummary(0, 100.0, 0.0, 0, 0, 0, [])

        fleet_health = sum(self._clamp100(m.health_score) for m in machines) / len(machines)
        fleet_risk = sum(self._clamp01(m.failure_risk) for m in machines) / len(machines)

        critical = sum(
            1 for m in machines
            if m.health_score < 35.0 or m.failure_risk >= 0.80
        )
        degraded = sum(
            1 for m in machines
            if not (m.health_score < 35.0 or m.failure_risk >= 0.80)
            and (m.health_score < 70.0 or m.failure_risk >= 0.50)
        )
        healthy = len(machines) - critical - degraded

        ordered = sorted(
            machines,
            key=lambda m: (m.failure_risk, -m.health_score, m.drift_score),
            reverse=True,
        )

        return FleetHealthSummary(
            machine_count=len(machines),
            fleet_health_score=round(fleet_health, 2),
            fleet_risk_score=round(fleet_risk, 4),
            critical_machine_count=critical,
            degraded_machine_count=degraded,
            healthy_machine_count=healthy,
            machines=ordered,
        )

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _clamp100(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


fleet_health_engine = FleetHealthEngine()
