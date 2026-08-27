from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class PlantMaintenanceInput:
    site_id: str
    fleet_id: str
    machine_id: str
    fleet_priority_score: float
    fleet_warning_score: float
    forecast_risk: float
    counterfactual_benefit: float
    maintenance_urgency: float
    expected_downtime_hours: float
    available_capacity_units: float = 1.0


@dataclass(frozen=True)
class PlantMaintenanceAction:
    rank: int
    site_id: str
    fleet_id: str
    machine_id: str
    plant_priority_score: float
    priority_band: str
    expected_downtime_hours: float
    reason_codes: list[str]


@dataclass(frozen=True)
class PlantMaintenancePlan:
    site_id: str
    selected_actions: list[PlantMaintenanceAction]
    deferred_machine_ids: list[str]
    used_capacity_units: float
    total_capacity_units: float


class PlantMaintenanceEngine:
    def plan(
        self,
        items: list[PlantMaintenanceInput],
        *,
        capacity_by_site: dict[str, float],
    ) -> list[PlantMaintenancePlan]:
        grouped: dict[str, list[PlantMaintenanceInput]] = defaultdict(list)
        for item in items:
            grouped[item.site_id].append(item)

        plans = []
        for site_id, site_items in grouped.items():
            capacity = max(0.0, float(capacity_by_site.get(site_id, 0.0)))
            ranked = sorted(
                (
                    (item, self._score(item))
                    for item in site_items
                ),
                key=lambda pair: pair[1],
                reverse=True,
            )

            selected = []
            deferred = []
            used = 0.0

            for item, score in ranked:
                units = max(0.0, float(item.available_capacity_units))
                if used + units <= capacity:
                    selected.append((item, score))
                    used += units
                else:
                    deferred.append(item.machine_id)

            actions = [
                PlantMaintenanceAction(
                    rank=index,
                    site_id=item.site_id,
                    fleet_id=item.fleet_id,
                    machine_id=item.machine_id,
                    plant_priority_score=round(score, 4),
                    priority_band=self._band(score),
                    expected_downtime_hours=max(0.0, item.expected_downtime_hours),
                    reason_codes=self._reasons(item),
                )
                for index, (item, score) in enumerate(selected, start=1)
            ]

            plans.append(
                PlantMaintenancePlan(
                    site_id=site_id,
                    selected_actions=actions,
                    deferred_machine_ids=deferred,
                    used_capacity_units=round(used, 4),
                    total_capacity_units=round(capacity, 4),
                )
            )

        plans.sort(
            key=lambda plan: (
                len(plan.selected_actions),
                plan.used_capacity_units,
            ),
            reverse=True,
        )
        return plans

    def _score(self, item: PlantMaintenanceInput) -> float:
        downtime_penalty = min(1.0, max(0.0, item.expected_downtime_hours) / 24.0)
        return self._clamp01(
            self._clamp01(item.fleet_priority_score) * 0.28
            + self._clamp01(item.fleet_warning_score) * 0.16
            + self._clamp01(item.forecast_risk) * 0.20
            + self._clamp01(item.counterfactual_benefit) * 0.16
            + self._clamp01(item.maintenance_urgency) * 0.14
            - downtime_penalty * 0.06
        )

    def _reasons(self, item: PlantMaintenanceInput) -> list[str]:
        reasons = []
        if item.fleet_priority_score >= 0.70:
            reasons.append("HIGH_FLEET_PRIORITY")
        if item.fleet_warning_score >= 0.60:
            reasons.append("FLEET_EARLY_WARNING")
        if item.forecast_risk >= 0.70:
            reasons.append("HIGH_FORECAST_RISK")
        if item.counterfactual_benefit >= 0.60:
            reasons.append("HIGH_EXPECTED_INTERVENTION_BENEFIT")
        if item.maintenance_urgency >= 0.70:
            reasons.append("HIGH_MAINTENANCE_URGENCY")
        return reasons or ["COMPOSITE_PLANT_PRIORITY"]

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


plant_maintenance_engine = PlantMaintenanceEngine()
