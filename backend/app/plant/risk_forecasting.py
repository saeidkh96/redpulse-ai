from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class FleetRiskObservation:
    step: int
    risk_score: float
    health_score: float
    drift_pressure: float
    hotspot_severity: float


@dataclass(frozen=True)
class FleetRiskForecast:
    horizon_steps: int
    current_risk: float
    predicted_risk: float
    predicted_health: float
    risk_trend: float
    health_trend: float
    confidence: float
    forecast_state: str


class FleetRiskForecastingEngine:
    def forecast(
        self,
        observations: list[FleetRiskObservation],
        *,
        horizon_steps: int = 5,
    ) -> FleetRiskForecast:
        if len(observations) < 2:
            raise ValueError("at least two observations are required")
        if horizon_steps < 1:
            raise ValueError("horizon_steps must be at least 1")

        ordered = sorted(observations, key=lambda item: item.step)

        risk_slopes = []
        health_slopes = []
        for left, right in zip(ordered, ordered[1:]):
            delta = right.step - left.step
            if delta <= 0:
                continue
            risk_slopes.append((right.risk_score - left.risk_score) / delta)
            health_slopes.append((right.health_score - left.health_score) / delta)

        if not risk_slopes:
            raise ValueError("observations require increasing step values")

        risk_trend = mean(risk_slopes)
        health_trend = mean(health_slopes)

        latest = ordered[-1]
        context_pressure = self._clamp01(
            latest.drift_pressure * 0.45
            + latest.hotspot_severity * 0.55
        )

        projected_risk = self._clamp01(
            latest.risk_score
            + (risk_trend * horizon_steps)
            + (context_pressure * 0.05 * min(horizon_steps, 10))
        )
        projected_health = self._clamp100(
            latest.health_score
            + (health_trend * horizon_steps)
            - (context_pressure * 2.5 * min(horizon_steps, 10))
        )

        sample_confidence = min(1.0, len(ordered) / 10.0)
        horizon_penalty = min(0.45, max(0, horizon_steps - 5) * 0.03)
        confidence = self._clamp01(
            0.35 + sample_confidence * 0.50 - horizon_penalty
        )

        return FleetRiskForecast(
            horizon_steps=horizon_steps,
            current_risk=round(self._clamp01(latest.risk_score), 4),
            predicted_risk=round(projected_risk, 4),
            predicted_health=round(projected_health, 2),
            risk_trend=round(risk_trend, 4),
            health_trend=round(health_trend, 4),
            confidence=round(confidence, 4),
            forecast_state=self._state(projected_risk, projected_health),
        )

    @staticmethod
    def _state(risk: float, health: float) -> str:
        if risk >= 0.80 or health <= 30.0:
            return "critical"
        if risk >= 0.60 or health <= 50.0:
            return "high_risk"
        if risk >= 0.40 or health <= 70.0:
            return "degrading"
        return "stable"

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _clamp100(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


fleet_risk_forecasting_engine = FleetRiskForecastingEngine()
