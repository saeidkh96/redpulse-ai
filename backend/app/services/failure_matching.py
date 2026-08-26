import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.failure.fingerprint import (
    FailureFingerprintData,
    failure_fingerprint_builder,
)
from app.failure.matching import (
    FailureMatchScore,
    failure_trajectory_matcher,
)
from app.models.behavior_event import BehaviorEventType
from app.models.failure_fingerprint import FailureFingerprint
from app.repositories.behavior_event import (
    behavior_event_repository,
)
from app.repositories.failure_fingerprint import (
    failure_fingerprint_repository,
)


@dataclass(frozen=True)
class FailureMatch:
    fingerprint: FailureFingerprint
    score: FailureMatchScore


@dataclass(frozen=True)
class FailureMatchingResult:
    machine_id: uuid.UUID
    current_fingerprint: FailureFingerprintData
    matches: list[FailureMatch]
    candidate_count: int


class FailureMatchingService:
    async def match_machine(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None = None,
        failure_type: str | None = None,
        event_limit: int = 100,
        library_limit: int = 500,
        top_k: int = 5,
        minimum_similarity: float = 0.0,
    ) -> FailureMatchingResult:
        if event_limit < 1:
            raise ValueError(
                "event_limit must be at least 1"
            )

        if library_limit < 1:
            raise ValueError(
                "library_limit must be at least 1"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1"
            )

        if not 0.0 <= minimum_similarity <= 1.0:
            raise ValueError(
                "minimum_similarity must be between 0 and 1"
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

        if not relevant_events:
            raise ValueError(
                "No behavioral memory events available "
                "for failure trajectory matching"
            )

        current_fingerprint = (
            failure_fingerprint_builder.build(
                relevant_events
            )
        )

        candidates = (
            await failure_fingerprint_repository.list_library(
                session,
                failure_type=failure_type,
                machine_type=machine_type,
                limit=library_limit,
            )
        )

        matches: list[FailureMatch] = []

        for candidate in candidates:
            score = failure_trajectory_matcher.match(
                current_fingerprint,
                candidate,
            )

            if (
                score.overall_similarity
                < minimum_similarity
            ):
                continue

            matches.append(
                FailureMatch(
                    fingerprint=candidate,
                    score=score,
                )
            )

        matches.sort(
            key=lambda match: (
                match.score.overall_similarity
            ),
            reverse=True,
        )

        return FailureMatchingResult(
            machine_id=machine_id,
            current_fingerprint=current_fingerprint,
            matches=matches[:top_k],
            candidate_count=len(candidates),
        )


failure_matching_service = FailureMatchingService()
