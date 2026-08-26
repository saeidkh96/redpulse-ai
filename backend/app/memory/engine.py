from dataclasses import dataclass

from app.models.behavior_event import (
    BehaviorEventType,
    BehaviorSeverity,
)


@dataclass(frozen=True)
class MemoryDecision:
    should_store: bool
    event_type: BehaviorEventType | None
    severity: BehaviorSeverity | None
    summary: str | None
    evidence: dict


class BehavioralMemoryEngine:
    MIN_DEVIATION_SCORE = 0.20
    MIN_DRIFT_SCORE = 0.30

    def from_deviation(
        self,
        *,
        overall_score: float,
        severity: str,
        sensor_deviations: dict,
        correlation_shifts: dict,
    ) -> MemoryDecision:
        if (
            overall_score < self.MIN_DEVIATION_SCORE
            and severity == "normal"
        ):
            return MemoryDecision(
                should_store=False,
                event_type=None,
                severity=None,
                summary=None,
                evidence={},
            )

        mapped_severity = self._map_severity(
            severity
        )

        ranked_sensors = sorted(
            sensor_deviations.items(),
            key=lambda item: float(
                item[1].get(
                    "mean_zscore",
                    0.0,
                )
            ),
            reverse=True,
        )

        top_sensors = [
            {
                "sensor": sensor,
                "mean_zscore": float(
                    data.get(
                        "mean_zscore",
                        0.0,
                    )
                ),
                "score": float(
                    data.get(
                        "score",
                        0.0,
                    )
                ),
            }
            for sensor, data in ranked_sensors[:3]
        ]

        ranked_correlations = sorted(
            correlation_shifts.items(),
            key=lambda item: float(
                item[1].get(
                    "delta",
                    0.0,
                )
            ),
            reverse=True,
        )

        top_correlations = [
            {
                "relationship": relationship,
                "delta": float(
                    data.get(
                        "delta",
                        0.0,
                    )
                ),
            }
            for relationship, data in ranked_correlations[:3]
        ]

        summary = (
            "Behavioral deviation detected "
            f"with score {overall_score:.3f} "
            f"and severity {severity}"
        )

        return MemoryDecision(
            should_store=True,
            event_type=BehaviorEventType.DEVIATION,
            severity=mapped_severity,
            summary=summary,
            evidence={
                "overall_score": overall_score,
                "top_sensors": top_sensors,
                "top_correlation_shifts": top_correlations,
            },
        )

    def from_drift(
        self,
        *,
        overall_score: float,
        state: str,
        signals: dict,
    ) -> MemoryDecision:
        if (
            overall_score < self.MIN_DRIFT_SCORE
            and state == "stable"
        ):
            return MemoryDecision(
                should_store=False,
                event_type=None,
                severity=None,
                summary=None,
                evidence={},
            )

        mapped_severity = (
            BehaviorSeverity.WARNING
            if state == "emerging"
            else BehaviorSeverity.ANOMALOUS
            if state == "drifting"
            else BehaviorSeverity.INFO
        )

        ranked_signals = sorted(
            signals.items(),
            key=lambda item: float(
                item[1].get(
                    "score",
                    0.0,
                )
            ),
            reverse=True,
        )

        top_signals = [
            {
                "signal": signal,
                "score": float(
                    data.get(
                        "score",
                        0.0,
                    )
                ),
                "state": str(
                    data.get(
                        "state",
                        "stable",
                    )
                ),
            }
            for signal, data in ranked_signals[:5]
        ]

        summary = (
            "Slow behavioral drift detected "
            f"with score {overall_score:.3f} "
            f"and state {state}"
        )

        return MemoryDecision(
            should_store=True,
            event_type=BehaviorEventType.DRIFT,
            severity=mapped_severity,
            summary=summary,
            evidence={
                "overall_score": overall_score,
                "state": state,
                "top_signals": top_signals,
            },
        )

    @staticmethod
    def _map_severity(
        severity: str,
    ) -> BehaviorSeverity:
        mapping = {
            "normal": BehaviorSeverity.NORMAL,
            "warning": BehaviorSeverity.WARNING,
            "anomalous": BehaviorSeverity.ANOMALOUS,
            "critical": BehaviorSeverity.CRITICAL,
        }

        return mapping.get(
            severity,
            BehaviorSeverity.INFO,
        )


behavioral_memory_engine = BehavioralMemoryEngine()
