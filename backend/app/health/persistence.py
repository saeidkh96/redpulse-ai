from dataclasses import dataclass

from app.models.behavior_event import (
    BehaviorEvent,
    BehaviorEventType,
)


@dataclass(frozen=True)
class PersistenceResult:
    score: float
    event_count: int
    deviation_count: int
    drift_count: int
    anomalous_count: int
    duration_seconds: float | None


class BehavioralPersistenceScorer:
    MAX_EVENT_COUNT = 10

    def score(
        self,
        events: list[BehaviorEvent],
    ) -> PersistenceResult:
        relevant_events = [
            event
            for event in events
            if event.event_type
            in {
                BehaviorEventType.DEVIATION,
                BehaviorEventType.DRIFT,
            }
        ]

        if not relevant_events:
            return PersistenceResult(
                score=0.0,
                event_count=0,
                deviation_count=0,
                drift_count=0,
                anomalous_count=0,
                duration_seconds=None,
            )

        deviation_count = sum(
            1
            for event in relevant_events
            if event.event_type
            == BehaviorEventType.DEVIATION
        )

        drift_count = sum(
            1
            for event in relevant_events
            if event.event_type
            == BehaviorEventType.DRIFT
        )

        anomalous_count = sum(
            1
            for event in relevant_events
            if getattr(
                event.severity,
                "value",
                event.severity,
            )
            == "anomalous"
        )

        event_component = min(
            len(relevant_events)
            / self.MAX_EVENT_COUNT,
            1.0,
        )

        anomaly_component = (
            anomalous_count
            / len(relevant_events)
        )

        type_component = (
            1.0
            if deviation_count > 0
            and drift_count > 0
            else 0.5
        )

        duration_seconds = self._duration(
            relevant_events
        )

        score = (
            event_component * 0.40
            + anomaly_component * 0.35
            + type_component * 0.25
        )

        return PersistenceResult(
            score=round(
                min(max(score, 0.0), 1.0),
                4,
            ),
            event_count=len(relevant_events),
            deviation_count=deviation_count,
            drift_count=drift_count,
            anomalous_count=anomalous_count,
            duration_seconds=duration_seconds,
        )

    @staticmethod
    def _duration(
        events: list[BehaviorEvent],
    ) -> float | None:
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

        if not starts or not ends:
            return None

        return max(
            0.0,
            (
                max(ends)
                - min(starts)
            ).total_seconds(),
        )


behavioral_persistence_scorer = (
    BehavioralPersistenceScorer()
)
