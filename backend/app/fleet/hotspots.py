from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class FleetFailureEvidence:
    machine_id: str
    failure_mode: str
    risk: float
    trajectory_similarity: float
    health_score: float


@dataclass(frozen=True)
class FleetFailureHotspot:
    failure_mode: str
    affected_machines: int
    average_risk: float
    average_trajectory_similarity: float
    severity_score: float
    machine_ids: list[str]


class FleetFailureHotspotEngine:
    def detect(
        self,
        evidence: list[FleetFailureEvidence],
        *,
        minimum_risk: float = 0.40,
    ) -> list[FleetFailureHotspot]:
        grouped: dict[str, list[FleetFailureEvidence]] = defaultdict(list)
        for item in evidence:
            if item.risk >= minimum_risk:
                grouped[item.failure_mode].append(item)

        hotspots: list[FleetFailureHotspot] = []
        for failure_mode, items in grouped.items():
            avg_risk = sum(self._clamp01(i.risk) for i in items) / len(items)
            avg_similarity = sum(
                self._clamp01(i.trajectory_similarity) for i in items
            ) / len(items)
            health_pressure = sum(
                1.0 - self._clamp01(i.health_score / 100.0) for i in items
            ) / len(items)
            spread = min(1.0, len(items) / 10.0)

            severity = (
                avg_risk * 0.45
                + avg_similarity * 0.25
                + health_pressure * 0.20
                + spread * 0.10
            )

            hotspots.append(
                FleetFailureHotspot(
                    failure_mode=failure_mode,
                    affected_machines=len(items),
                    average_risk=round(avg_risk, 4),
                    average_trajectory_similarity=round(avg_similarity, 4),
                    severity_score=round(self._clamp01(severity), 4),
                    machine_ids=sorted({i.machine_id for i in items}),
                )
            )

        hotspots.sort(
            key=lambda item: (item.severity_score, item.affected_machines),
            reverse=True,
        )
        return hotspots

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))


fleet_failure_hotspot_engine = FleetFailureHotspotEngine()
