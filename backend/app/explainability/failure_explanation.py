from dataclasses import dataclass
from enum import Enum
from typing import Any


class EvidenceCategory(str, Enum):
    SENSOR = "sensor"
    DEVIATION = "deviation"
    DRIFT = "drift"
    PERSISTENCE = "persistence"
    HISTORICAL_MATCH = "historical_match"
    CORRELATION = "correlation"
    TRAJECTORY = "trajectory"


@dataclass(frozen=True)
class ExplanationEvidence:
    category: EvidenceCategory
    name: str
    contribution: float
    value: float | None
    description: str


@dataclass(frozen=True)
class RootCauseHint:
    cause: str
    confidence: float
    supporting_evidence: list[str]


@dataclass(frozen=True)
class FailureExplanation:
    summary: str
    primary_driver: str | None
    evidence: list[ExplanationEvidence]
    root_cause_hints: list[RootCauseHint]


class FailureExplanationEngine:
    def explain(
        self,
        *,
        prediction_evidence: dict[str, Any],
        risk_components: dict[str, float],
        dominant_sensors: list[dict] | None = None,
        drift_signature: dict | None = None,
        correlation_signature: dict | None = None,
        trajectory_summary: dict | None = None,
    ) -> FailureExplanation:
        dominant_sensors = dominant_sensors or []
        drift_signature = drift_signature or {}
        correlation_signature = (
            correlation_signature or {}
        )
        trajectory_summary = trajectory_summary or {}

        evidence: list[ExplanationEvidence] = []

        self._add_behavioral_evidence(
            evidence=evidence,
            prediction_evidence=prediction_evidence,
            risk_components=risk_components,
        )

        self._add_sensor_evidence(
            evidence=evidence,
            dominant_sensors=dominant_sensors,
        )

        self._add_drift_signal_evidence(
            evidence=evidence,
            drift_signature=drift_signature,
        )

        self._add_correlation_evidence(
            evidence=evidence,
            correlation_signature=(
                correlation_signature
            ),
        )

        self._add_trajectory_evidence(
            evidence=evidence,
            trajectory_summary=trajectory_summary,
        )

        evidence.sort(
            key=lambda item: item.contribution,
            reverse=True,
        )

        primary_driver = (
            evidence[0].name
            if evidence
            else None
        )

        root_cause_hints = self._root_cause_hints(
            evidence
        )

        summary = self._summary(
            prediction_evidence=prediction_evidence,
            primary_driver=primary_driver,
            root_cause_hints=root_cause_hints,
        )

        return FailureExplanation(
            summary=summary,
            primary_driver=primary_driver,
            evidence=evidence,
            root_cause_hints=root_cause_hints,
        )

    @staticmethod
    def _add_behavioral_evidence(
        *,
        evidence: list[ExplanationEvidence],
        prediction_evidence: dict[str, Any],
        risk_components: dict[str, float],
    ) -> None:
        mapping = (
            (
                "deviation",
                "deviation_score",
                EvidenceCategory.DEVIATION,
                "Behavioral deviation",
            ),
            (
                "drift",
                "drift_score",
                EvidenceCategory.DRIFT,
                "Behavioral drift",
            ),
            (
                "persistence",
                "persistence_score",
                EvidenceCategory.PERSISTENCE,
                "Behavioral persistence",
            ),
        )

        for (
            component_name,
            value_name,
            category,
            display_name,
        ) in mapping:
            contribution = float(
                risk_components.get(
                    component_name,
                    0.0,
                )
            )

            value = prediction_evidence.get(
                value_name
            )

            if (
                contribution <= 0.0
                and value is None
            ):
                continue

            evidence.append(
                ExplanationEvidence(
                    category=category,
                    name=display_name,
                    contribution=round(
                        contribution,
                        4,
                    ),
                    value=(
                        float(value)
                        if value is not None
                        else None
                    ),
                    description=(
                        f"{display_name} contributes "
                        "to the predicted failure risk."
                    ),
                )
            )

        historical = prediction_evidence.get(
            "historical_failure"
        )

        if historical:
            similarity = float(
                historical.get(
                    "similarity",
                    0.0,
                )
            )

            evidence.append(
                ExplanationEvidence(
                    category=(
                        EvidenceCategory
                        .HISTORICAL_MATCH
                    ),
                    name="Historical failure match",
                    contribution=round(
                        float(
                            risk_components.get(
                                "failure_match",
                                0.0,
                            )
                        ),
                        4,
                    ),
                    value=similarity,
                    description=(
                        "Current behavior resembles a "
                        "historical failure trajectory."
                    ),
                )
            )

    @staticmethod
    def _add_sensor_evidence(
        *,
        evidence: list[ExplanationEvidence],
        dominant_sensors: list[dict],
    ) -> None:
        for sensor in dominant_sensors[:5]:
            name = sensor.get("sensor")

            if not name:
                continue

            mean_score = float(
                sensor.get(
                    "mean_score",
                    0.0,
                )
            )

            occurrences = int(
                sensor.get(
                    "occurrences",
                    1,
                )
            )

            contribution = min(
                1.0,
                mean_score
                * min(
                    1.0,
                    occurrences / 3.0,
                ),
            )

            evidence.append(
                ExplanationEvidence(
                    category=EvidenceCategory.SENSOR,
                    name=f"Sensor: {name}",
                    contribution=round(
                        contribution,
                        4,
                    ),
                    value=mean_score,
                    description=(
                        f"{name} repeatedly appears among "
                        "the strongest abnormal sensors."
                    ),
                )
            )

    @staticmethod
    def _add_drift_signal_evidence(
        *,
        evidence: list[ExplanationEvidence],
        drift_signature: dict,
    ) -> None:
        signals = drift_signature.get(
            "dominant_signals",
            [],
        )

        for signal in signals[:5]:
            name = signal.get("signal")

            if not name:
                continue

            mean_score = float(
                signal.get(
                    "mean_score",
                    0.0,
                )
            )

            evidence.append(
                ExplanationEvidence(
                    category=EvidenceCategory.DRIFT,
                    name=f"Drift signal: {name}",
                    contribution=round(
                        mean_score,
                        4,
                    ),
                    value=mean_score,
                    description=(
                        f"{name} is a dominant signal "
                        "in the observed behavioral drift."
                    ),
                )
            )

    @staticmethod
    def _add_correlation_evidence(
        *,
        evidence: list[ExplanationEvidence],
        correlation_signature: dict,
    ) -> None:
        relationships = (
            correlation_signature.get(
                "relationships",
                [],
            )
        )

        for relationship in relationships[:5]:
            name = relationship.get(
                "relationship"
            )

            if not name:
                continue

            delta = abs(
                float(
                    relationship.get(
                        "mean_delta",
                        0.0,
                    )
                )
            )

            evidence.append(
                ExplanationEvidence(
                    category=(
                        EvidenceCategory.CORRELATION
                    ),
                    name=(
                        f"Correlation shift: {name}"
                    ),
                    contribution=round(
                        min(delta, 1.0),
                        4,
                    ),
                    value=delta,
                    description=(
                        f"The relationship {name} changed "
                        "relative to expected behavior."
                    ),
                )
            )

    @staticmethod
    def _add_trajectory_evidence(
        *,
        evidence: list[ExplanationEvidence],
        trajectory_summary: dict,
    ) -> None:
        duration = trajectory_summary.get(
            "duration_seconds"
        )

        event_count = trajectory_summary.get(
            "event_count"
        )

        if (
            duration is None
            and event_count is None
        ):
            return

        count = int(event_count or 0)

        contribution = min(
            1.0,
            count / 10.0,
        )

        evidence.append(
            ExplanationEvidence(
                category=EvidenceCategory.TRAJECTORY,
                name="Failure trajectory persistence",
                contribution=round(
                    contribution,
                    4,
                ),
                value=(
                    float(duration)
                    if duration is not None
                    else None
                ),
                description=(
                    "Abnormal behavior persists across "
                    f"{count} behavioral events."
                ),
            )
        )

    @staticmethod
    def _root_cause_hints(
        evidence: list[ExplanationEvidence],
    ) -> list[RootCauseHint]:
        hints: list[RootCauseHint] = []

        sensors = [
            item
            for item in evidence
            if item.category
            == EvidenceCategory.SENSOR
        ]

        drift_signals = [
            item
            for item in evidence
            if (
                item.category
                == EvidenceCategory.DRIFT
                and item.name.startswith(
                    "Drift signal:"
                )
            )
        ]

        correlations = [
            item
            for item in evidence
            if item.category
            == EvidenceCategory.CORRELATION
        ]

        if sensors:
            strongest = sensors[0]

            hints.append(
                RootCauseHint(
                    cause=strongest.name.replace(
                        "Sensor: ",
                        "",
                    ),
                    confidence=round(
                        min(
                            strongest.contribution,
                            1.0,
                        ),
                        4,
                    ),
                    supporting_evidence=[
                        strongest.description
                    ],
                )
            )

        if drift_signals:
            strongest = drift_signals[0]

            hints.append(
                RootCauseHint(
                    cause=strongest.name.replace(
                        "Drift signal: ",
                        "",
                    ),
                    confidence=round(
                        min(
                            strongest.contribution,
                            1.0,
                        ),
                        4,
                    ),
                    supporting_evidence=[
                        strongest.description
                    ],
                )
            )

        if correlations:
            strongest = correlations[0]

            hints.append(
                RootCauseHint(
                    cause=strongest.name.replace(
                        "Correlation shift: ",
                        "",
                    ),
                    confidence=round(
                        min(
                            strongest.contribution,
                            1.0,
                        ),
                        4,
                    ),
                    supporting_evidence=[
                        strongest.description
                    ],
                )
            )

        hints.sort(
            key=lambda item: item.confidence,
            reverse=True,
        )

        return hints[:5]

    @staticmethod
    def _summary(
        *,
        prediction_evidence: dict[str, Any],
        primary_driver: str | None,
        root_cause_hints: list[RootCauseHint],
    ) -> str:
        state = prediction_evidence.get(
            "machine_health_state",
            "unknown",
        )

        if primary_driver is None:
            return (
                "No significant failure-driving evidence "
                "was identified."
            )

        summary = (
            f"Machine health is {state}. "
            f"The strongest failure-risk driver is "
            f"{primary_driver}."
        )

        if root_cause_hints:
            summary += (
                " Leading root-cause hint: "
                f"{root_cause_hints[0].cause}."
            )

        return summary


failure_explanation_engine = (
    FailureExplanationEngine()
)
