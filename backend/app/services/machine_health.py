import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.health.persistence import (
    PersistenceResult,
    behavioral_persistence_scorer,
)
from app.health.scoring import (
    HealthScoreInput,
    HealthScoreResult,
    machine_health_scorer,
)
from app.models.behavior_event import (
    BehaviorEvent,
    BehaviorEventType,
)
from app.repositories.behavior_event import (
    behavior_event_repository,
)
from app.services.failure_matching import (
    FailureMatch,
    failure_matching_service,
)


@dataclass(frozen=True)
class MachineHealthResult:
    machine_id: uuid.UUID
    health: HealthScoreResult
    persistence: PersistenceResult
    deviation_score: float
    drift_score: float
    failure_match_score: float
    best_failure_match: FailureMatch | None


class MachineHealthService:
    async def assess(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None = None,
        event_limit: int = 100,
        library_limit: int = 500,
    ) -> MachineHealthResult:
        if event_limit < 1:
            raise ValueError(
                "event_limit must be at least 1"
            )

        if library_limit < 1:
            raise ValueError(
                "library_limit must be at least 1"
            )

        events = (
            await behavior_event_repository.list_for_machine(
                session,
                machine_id,
                limit=event_limit,
            )
        )

        relevant_events = [
            event
            for event in events
            if event.event_type
            in {
                BehaviorEventType.DEVIATION,
                BehaviorEventType.DRIFT,
            }
        ]

        deviation_score = self._latest_score(
            relevant_events,
            BehaviorEventType.DEVIATION,
        )

        drift_score = self._latest_score(
            relevant_events,
            BehaviorEventType.DRIFT,
        )

        persistence = (
            behavioral_persistence_scorer.score(
                relevant_events
            )
        )

        best_failure_match = None
        failure_match_score = 0.0

        if relevant_events:
            matching_result = (
                await failure_matching_service.match_machine(
                    session,
                    machine_id=machine_id,
                    machine_type=machine_type,
                    event_limit=event_limit,
                    library_limit=library_limit,
                    top_k=1,
                )
            )

            if matching_result.matches:
                best_failure_match = (
                    matching_result.matches[0]
                )

                failure_match_score = (
                    best_failure_match
                    .score
                    .overall_similarity
                )

        health = machine_health_scorer.score(
            HealthScoreInput(
                deviation_score=deviation_score,
                drift_score=drift_score,
                failure_match_score=(
                    failure_match_score
                ),
                persistence_score=(
                    persistence.score
                ),
            )
        )

        return MachineHealthResult(
            machine_id=machine_id,
            health=health,
            persistence=persistence,
            deviation_score=deviation_score,
            drift_score=drift_score,
            failure_match_score=(
                failure_match_score
            ),
            best_failure_match=(
                best_failure_match
            ),
        )

    @staticmethod
    def _latest_score(
        events: list[BehaviorEvent],
        event_type: BehaviorEventType,
    ) -> float:
        candidates = [
            event
            for event in events
            if (
                event.event_type == event_type
                and event.score is not None
            )
        ]

        if not candidates:
            return 0.0

        latest = max(
            candidates,
            key=lambda event: (
                event.window_end
                or event.window_start
                or event.created_at
            ),
        )

        return max(
            0.0,
            min(
                1.0,
                float(latest.score),
            ),
        )


machine_health_service = MachineHealthService()
