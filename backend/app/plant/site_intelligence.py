from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class PlantFleetInput:
    site_id: str
    fleet_id: str
    fleet_health_score: float
    fleet_risk_score: float
    critical_machine_count: int
    degraded_machine_count: int
    machine_count: int
    maintenance_backlog: int = 0


@dataclass(frozen=True)
class SiteFleetSummary:
    fleet_id: str
    fleet_health_score: float
    fleet_risk_score: float
    critical_machine_count: int
    degraded_machine_count: int
    machine_count: int
    maintenance_backlog: int


@dataclass(frozen=True)
class PlantIntelligenceSummary:
    site_id: str
    fleet_count: int
    machine_count: int
    plant_health_score: float
    plant_risk_score: float
    critical_machine_count: int
    degraded_machine_count: int
    maintenance_backlog: int
    operational_pressure: float
    fleets: list[SiteFleetSummary]


class PlantIntelligenceEngine:
    def summarize(self, fleets: list[PlantFleetInput]) -> list[PlantIntelligenceSummary]:
        grouped: dict[str, list[PlantFleetInput]] = defaultdict(list)
        for fleet in fleets:
            grouped[fleet.site_id].append(fleet)

        summaries = []
        for site_id, site_fleets in grouped.items():
            total_machines = sum(max(0, f.machine_count) for f in site_fleets)
            if total_machines:
                health = sum(
                    self._clamp100(f.fleet_health_score) * max(0, f.machine_count)
                    for f in site_fleets
                ) / total_machines
                risk = sum(
                    self._clamp01(f.fleet_risk_score) * max(0, f.machine_count)
                    for f in site_fleets
                ) / total_machines
            else:
                health = 100.0
                risk = 0.0

            critical = sum(max(0, f.critical_machine_count) for f in site_fleets)
            degraded = sum(max(0, f.degraded_machine_count) for f in site_fleets)
            backlog = sum(max(0, f.maintenance_backlog) for f in site_fleets)

            critical_ratio = critical / max(1, total_machines)
            degraded_ratio = degraded / max(1, total_machines)
            backlog_pressure = min(1.0, backlog / max(1, total_machines))

            operational_pressure = self._clamp01(
                (risk * 0.45)
                + (critical_ratio * 0.25)
                + (degraded_ratio * 0.15)
                + (backlog_pressure * 0.15)
            )

            fleet_summaries = [
                SiteFleetSummary(
                    fleet_id=f.fleet_id,
                    fleet_health_score=round(self._clamp100(f.fleet_health_score), 2),
                    fleet_risk_score=round(self._clamp01(f.fleet_risk_score), 4),
                    critical_machine_count=max(0, f.critical_machine_count),
                    degraded_machine_count=max(0, f.degraded_machine_count),
                    machine_count=max(0, f.machine_count),
                    maintenance_backlog=max(0, f.maintenance_backlog),
                )
                for f in sorted(
                    site_fleets,
                    key=lambda item: (
                        item.fleet_risk_score,
                        -item.fleet_health_score,
                        item.critical_machine_count,
                    ),
                    reverse=True,
                )
            ]

            summaries.append(
                PlantIntelligenceSummary(
                    site_id=site_id,
                    fleet_count=len(site_fleets),
                    machine_count=total_machines,
                    plant_health_score=round(health, 2),
                    plant_risk_score=round(risk, 4),
                    critical_machine_count=critical,
                    degraded_machine_count=degraded,
                    maintenance_backlog=backlog,
                    operational_pressure=round(operational_pressure, 4),
                    fleets=fleet_summaries,
                )
            )

        summaries.sort(
            key=lambda item: (item.operational_pressure, item.plant_risk_score),
            reverse=True,
        )
        return summaries

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _clamp100(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


plant_intelligence_engine = PlantIntelligenceEngine()
