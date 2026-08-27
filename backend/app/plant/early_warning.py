from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FleetEarlyWarningInput:
    fleet_id: str
    current_risk: float
    previous_risk: float
    current_health: float
    previous_health: float
    critical_machine_ratio: float
    hotspot_severity: float
    drift_pressure: float
    maintenance_backlog_ratio: float = 0.0


@dataclass(frozen=True)
class FleetEarlyWarningSignal:
    fleet_id: str
    warning_score: float
    warning_level: str
    risk_acceleration: float
    health_deterioration: float
    reason_codes: list[str]


class FleetEarlyWarningEngine:
    def analyze(self, item: FleetEarlyWarningInput) -> FleetEarlyWarningSignal:
        risk_acceleration = self._clamp_signed(item.current_risk - item.previous_risk)
        health_deterioration = self._clamp_signed(
            (item.previous_health - item.current_health) / 100.0
        )

        score = self._clamp01(
            (self._positive(risk_acceleration) * 0.22)
            + (self._positive(health_deterioration) * 0.18)
            + (self._clamp01(item.current_risk) * 0.18)
            + (self._clamp01(item.critical_machine_ratio) * 0.15)
            + (self._clamp01(item.hotspot_severity) * 0.12)
            + (self._clamp01(item.drift_pressure) * 0.10)
            + (self._clamp01(item.maintenance_backlog_ratio) * 0.05)
        )

        reasons = []
        if risk_acceleration >= 0.10:
            reasons.append("RISK_ACCELERATION")
        if health_deterioration >= 0.10:
            reasons.append("HEALTH_DETERIORATION")
        if item.critical_machine_ratio >= 0.20:
            reasons.append("CRITICAL_MACHINE_CONCENTRATION")
        if item.hotspot_severity >= 0.65:
            reasons.append("FAILURE_HOTSPOT_ESCALATION")
        if item.drift_pressure >= 0.65:
            reasons.append("FLEET_DRIFT_PRESSURE")
        if item.maintenance_backlog_ratio >= 0.30:
            reasons.append("MAINTENANCE_BACKLOG_PRESSURE")
        if not reasons:
            reasons.append("COMPOSITE_FLEET_WARNING")

        return FleetEarlyWarningSignal(
            fleet_id=item.fleet_id,
            warning_score=round(score, 4),
            warning_level=self._level(score),
            risk_acceleration=round(risk_acceleration, 4),
            health_deterioration=round(health_deterioration, 4),
            reason_codes=reasons,
        )

    @staticmethod
    def _level(score: float) -> str:
        if score >= 0.75:
            return "critical"
        if score >= 0.55:
            return "high"
        if score >= 0.35:
            return "elevated"
        return "normal"

    @staticmethod
    def _positive(value: float) -> float:
        return max(0.0, value)

    @staticmethod
    def _clamp_signed(value: float) -> float:
        return max(-1.0, min(1.0, float(value)))

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))


fleet_early_warning_engine = FleetEarlyWarningEngine()
