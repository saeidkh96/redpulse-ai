from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from app.models.behavior_event import BehaviorEvent, BehaviorEventType


@dataclass(frozen=True)
class FailureFingerprintData:
    baseline_version: str | None
    trajectory_start: datetime | None
    trajectory_end: datetime | None

    dominant_sensors: list[dict]
    deviation_signature: dict
    drift_signature: dict
    correlation_signature: dict
    trajectory_summary: dict
    evidence: dict


class FailureFingerprintBuilder:
    def build(
        self,
        events: list[BehaviorEvent],
    ) -> FailureFingerprintData:
        if not events:
            raise ValueError(
                "events must not be empty"
            )

        ordered_events = sorted(
            events,
            key=lambda event: (
                event.window_start
                or event.created_at
            ),
        )

        baseline_version = self._baseline_version(
            ordered_events
        )

        trajectory_start = min(
            (
                event.window_start
                for event in ordered_events
                if event.window_start is not None
            ),
            default=None,
        )

        trajectory_end = max(
            (
                event.window_end
                for event in ordered_events
                if event.window_end is not None
            ),
            default=None,
        )

        dominant_sensors = (
            self._dominant_sensors(
                ordered_events
            )
        )

        deviation_signature = (
            self._deviation_signature(
                ordered_events
            )
        )

        drift_signature = (
            self._drift_signature(
                ordered_events
            )
        )

        correlation_signature = (
            self._correlation_signature(
                ordered_events
            )
        )

        trajectory_summary = (
            self._trajectory_summary(
                ordered_events
            )
        )

        evidence = {
            "event_ids": [
                str(event.id)
                for event in ordered_events
            ],
            "event_count": len(
                ordered_events
            ),
            "event_types": [
                event.event_type.value
                for event in ordered_events
            ],
            "severities": [
                event.severity.value
                for event in ordered_events
            ],
        }

        return FailureFingerprintData(
            baseline_version=baseline_version,
            trajectory_start=trajectory_start,
            trajectory_end=trajectory_end,
            dominant_sensors=dominant_sensors,
            deviation_signature=deviation_signature,
            drift_signature=drift_signature,
            correlation_signature=correlation_signature,
            trajectory_summary=trajectory_summary,
            evidence=evidence,
        )

    @staticmethod
    def _baseline_version(
        events: list[BehaviorEvent],
    ) -> str | None:
        versions = [
            event.baseline_version
            for event in events
            if event.baseline_version is not None
        ]

        if not versions:
            return None

        counts = Counter(versions)

        return counts.most_common(1)[0][0]

    @staticmethod
    def _dominant_sensors(
        events: list[BehaviorEvent],
    ) -> list[dict]:
        sensor_scores: dict[
            str,
            list[float],
        ] = {}

        sensor_zscores: dict[
            str,
            list[float],
        ] = {}

        for event in events:
            top_sensors = event.evidence.get(
                "top_sensors",
                [],
            )

            for item in top_sensors:
                sensor = item.get("sensor")

                if not sensor:
                    continue

                sensor_scores.setdefault(
                    sensor,
                    [],
                ).append(
                    float(
                        item.get(
                            "score",
                            0.0,
                        )
                    )
                )

                sensor_zscores.setdefault(
                    sensor,
                    [],
                ).append(
                    float(
                        item.get(
                            "mean_zscore",
                            0.0,
                        )
                    )
                )

        ranked = []

        for sensor, scores in sensor_scores.items():
            zscores = sensor_zscores.get(
                sensor,
                [],
            )

            ranked.append(
                {
                    "sensor": sensor,
                    "occurrences": len(scores),
                    "mean_score": (
                        sum(scores)
                        / len(scores)
                    ),
                    "max_score": max(scores),
                    "mean_zscore": (
                        sum(zscores)
                        / len(zscores)
                        if zscores
                        else 0.0
                    ),
                    "max_zscore": (
                        max(zscores)
                        if zscores
                        else 0.0
                    ),
                }
            )

        ranked.sort(
            key=lambda item: (
                item["occurrences"],
                item["max_score"],
                item["max_zscore"],
            ),
            reverse=True,
        )

        return ranked[:5]

    @staticmethod
    def _deviation_signature(
        events: list[BehaviorEvent],
    ) -> dict:
        deviations = [
            event
            for event in events
            if event.event_type.value
            == "deviation"
        ]

        scores = [
            float(event.score)
            for event in deviations
            if event.score is not None
        ]

        return {
            "event_count": len(
                deviations
            ),
            "mean_score": (
                sum(scores) / len(scores)
                if scores
                else 0.0
            ),
            "max_score": (
                max(scores)
                if scores
                else 0.0
            ),
            "severities": [
                event.severity.value
                for event in deviations
            ],
        }

    @staticmethod
    def _drift_signature(
        events: list[BehaviorEvent],
    ) -> dict:
        drifts = [
            event
            for event in events
            if event.event_type.value
            == "drift"
        ]

        scores = [
            float(event.score)
            for event in drifts
            if event.score is not None
        ]

        states = [
            event.evidence.get(
                "state",
                "unknown",
            )
            for event in drifts
        ]

        signal_scores: dict[
            str,
            list[float],
        ] = {}

        for event in drifts:
            top_signals = event.evidence.get(
                "top_signals",
                [],
            )

            for item in top_signals:
                signal = item.get(
                    "signal"
                )

                if not signal:
                    continue

                signal_scores.setdefault(
                    signal,
                    [],
                ).append(
                    float(
                        item.get(
                            "score",
                            0.0,
                        )
                    )
                )

        dominant_signals = [
            {
                "signal": signal,
                "occurrences": len(
                    values
                ),
                "mean_score": (
                    sum(values)
                    / len(values)
                ),
                "max_score": max(
                    values
                ),
            }
            for signal, values
            in signal_scores.items()
        ]

        dominant_signals.sort(
            key=lambda item: (
                item["occurrences"],
                item["max_score"],
            ),
            reverse=True,
        )

        return {
            "event_count": len(drifts),
            "mean_score": (
                sum(scores) / len(scores)
                if scores
                else 0.0
            ),
            "max_score": (
                max(scores)
                if scores
                else 0.0
            ),
            "states": states,
            "dominant_signals": (
                dominant_signals[:5]
            ),
        }

    @staticmethod
    def _correlation_signature(
        events: list[BehaviorEvent],
    ) -> dict:
        relationship_deltas: dict[
            str,
            list[float],
        ] = {}

        for event in events:
            shifts = event.evidence.get(
                "top_correlation_shifts",
                [],
            )

            for item in shifts:
                relationship = item.get(
                    "relationship"
                )

                if not relationship:
                    continue

                relationship_deltas.setdefault(
                    relationship,
                    [],
                ).append(
                    float(
                        item.get(
                            "delta",
                            0.0,
                        )
                    )
                )

        relationships = [
            {
                "relationship": relationship,
                "occurrences": len(
                    values
                ),
                "mean_delta": (
                    sum(values)
                    / len(values)
                ),
                "max_delta": max(
                    values
                ),
            }
            for relationship, values
            in relationship_deltas.items()
        ]

        relationships.sort(
            key=lambda item: (
                item["occurrences"],
                item["max_delta"],
            ),
            reverse=True,
        )

        return {
            "relationships": (
                relationships[:10]
            )
        }

    @staticmethod
    def _trajectory_summary(
        events: list[BehaviorEvent],
    ) -> dict:
        deviation_scores = [
            float(event.score)
            for event in events
            if (
                event.event_type
                == BehaviorEventType.DEVIATION
                and event.score is not None
            )
        ]

        drift_scores = [
            float(event.score)
            for event in events
            if (
                event.event_type
                == BehaviorEventType.DRIFT
                and event.score is not None
            )
        ]

        starts = [
            event.window_start
            for event in events
            if event.window_start is not None
        ]

        ends = [
            event.window_end
            for event in events
            if event.window_end is not None
        ]

        duration_seconds = None

        if starts and ends:
            duration_seconds = (
                max(ends)
                - min(starts)
            ).total_seconds()

        return {
            "event_count": len(events),
            "duration_seconds": duration_seconds,
            "deviation_event_count": len(
                deviation_scores
            ),
            "drift_event_count": len(
                drift_scores
            ),
            "max_deviation_score": (
                max(deviation_scores)
                if deviation_scores
                else None
            ),
            "mean_deviation_score": (
                sum(deviation_scores)
                / len(deviation_scores)
                if deviation_scores
                else None
            ),
            "max_drift_score": (
                max(drift_scores)
                if drift_scores
                else None
            ),
            "mean_drift_score": (
                sum(drift_scores)
                / len(drift_scores)
                if drift_scores
                else None
            ),
        }


failure_fingerprint_builder = (
    FailureFingerprintBuilder()
)

