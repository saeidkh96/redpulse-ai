from dataclasses import dataclass
from enum import Enum

from app.explainability.failure_explanation import (
    FailureExplanation,
)
from app.services.failure_prediction import (
    FailurePredictionResult,
)


class MaintenancePriority(str, Enum):
    ROUTINE = "routine"
    SCHEDULED = "scheduled"
    URGENT = "urgent"
    IMMEDIATE = "immediate"


class MaintenanceActionType(str, Enum):
    MONITOR = "monitor"
    INSPECT = "inspect"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    STOP_AND_INSPECT = "stop_and_inspect"


@dataclass(frozen=True)
class MaintenanceDecisionInput:
    prediction: FailurePredictionResult
    explanation: FailureExplanation


@dataclass(frozen=True)
class MaintenanceDecision:
    priority: MaintenancePriority
    action_type: MaintenanceActionType
    urgency_score: float
    recommended_action: str
    predicted_failure: str | None
    affected_signals: list[str]
    root_cause_hints: list[str]
    rationale: list[str]


class MaintenanceDecisionEngine:
    def decide(
        self,
        value: MaintenanceDecisionInput,
    ) -> MaintenanceDecision:
        prediction = value.prediction
        explanation = value.explanation

        urgency_score = self._urgency_score(
            risk_score=prediction.risk.risk_score,
            confidence=prediction.risk.confidence,
            failure_match_score=(
                prediction.failure_match_score
            ),
        )

        priority = self._priority(
            urgency_score
        )

        action_type = self._action_type(
            priority
        )

        affected_signals = self._affected_signals(
            explanation
        )

        root_cause_hints = [
            hint.cause
            for hint in explanation.root_cause_hints[:5]
        ]

        recommended_action = (
            self._recommended_action(
                priority=priority,
                predicted_failure=(
                    prediction.likely_failure_type
                ),
                affected_signals=affected_signals,
            )
        )

        rationale = self._rationale(
            prediction=prediction,
            explanation=explanation,
            urgency_score=urgency_score,
        )

        return MaintenanceDecision(
            priority=priority,
            action_type=action_type,
            urgency_score=urgency_score,
            recommended_action=recommended_action,
            predicted_failure=(
                prediction.likely_failure_type
            ),
            affected_signals=affected_signals,
            root_cause_hints=root_cause_hints,
            rationale=rationale,
        )

    @staticmethod
    def _urgency_score(
        *,
        risk_score: float,
        confidence: float,
        failure_match_score: float,
    ) -> float:
        risk_score = max(
            0.0,
            min(1.0, float(risk_score)),
        )

        confidence = max(
            0.0,
            min(1.0, float(confidence)),
        )

        failure_match_score = max(
            0.0,
            min(1.0, float(failure_match_score)),
        )

        score = (
            risk_score * 0.55
            + confidence * 0.20
            + failure_match_score * 0.25
        )

        return round(
            max(0.0, min(1.0, score)),
            4,
        )

    @staticmethod
    def _priority(
        urgency_score: float,
    ) -> MaintenancePriority:
        if urgency_score >= 0.75:
            return MaintenancePriority.IMMEDIATE

        if urgency_score >= 0.55:
            return MaintenancePriority.URGENT

        if urgency_score >= 0.30:
            return MaintenancePriority.SCHEDULED

        return MaintenancePriority.ROUTINE

    @staticmethod
    def _action_type(
        priority: MaintenancePriority,
    ) -> MaintenanceActionType:
        mapping = {
            MaintenancePriority.ROUTINE: (
                MaintenanceActionType.MONITOR
            ),
            MaintenancePriority.SCHEDULED: (
                MaintenanceActionType.INSPECT
            ),
            MaintenancePriority.URGENT: (
                MaintenanceActionType
                .SCHEDULE_MAINTENANCE
            ),
            MaintenancePriority.IMMEDIATE: (
                MaintenanceActionType
                .STOP_AND_INSPECT
            ),
        }

        return mapping[priority]

    @staticmethod
    def _affected_signals(
        explanation: FailureExplanation,
    ) -> list[str]:
        signals: list[str] = []

        for item in explanation.evidence:
            if item.category.value not in {
                "sensor",
                "drift",
                "correlation",
            }:
                continue

            if item.name not in signals:
                signals.append(item.name)

        return signals[:5]

    @staticmethod
    def _recommended_action(
        *,
        priority: MaintenancePriority,
        predicted_failure: str | None,
        affected_signals: list[str],
    ) -> str:
        failure = (
            predicted_failure
            or "the detected degradation pattern"
        )

        signal_text = (
            ", ".join(affected_signals[:3])
            if affected_signals
            else "the affected machine signals"
        )

        if priority == MaintenancePriority.IMMEDIATE:
            return (
                "Stop the machine when operationally safe "
                f"and inspect {failure}, focusing on "
                f"{signal_text}."
            )

        if priority == MaintenancePriority.URGENT:
            return (
                "Schedule maintenance at the earliest "
                f"available window for {failure}, focusing "
                f"on {signal_text}."
            )

        if priority == MaintenancePriority.SCHEDULED:
            return (
                "Plan a targeted inspection during the "
                f"next maintenance window for {failure}, "
                f"focusing on {signal_text}."
            )

        return (
            "Continue monitoring the machine and review "
            f"{signal_text} for changes."
        )

    @staticmethod
    def _rationale(
        *,
        prediction: FailurePredictionResult,
        explanation: FailureExplanation,
        urgency_score: float,
    ) -> list[str]:
        rationale = [
            (
                "Predicted failure risk score: "
                f"{prediction.risk.risk_score:.4f}"
            ),
            (
                "Prediction confidence: "
                f"{prediction.risk.confidence:.4f}"
            ),
            (
                "Maintenance urgency score: "
                f"{urgency_score:.4f}"
            ),
        ]

        if prediction.likely_failure_type:
            rationale.append(
                "Likely failure pattern: "
                f"{prediction.likely_failure_type}"
            )

        if explanation.primary_driver:
            rationale.append(
                "Primary failure driver: "
                f"{explanation.primary_driver}"
            )

        if explanation.root_cause_hints:
            rationale.append(
                "Leading root-cause hint: "
                f"{explanation.root_cause_hints[0].cause}"
            )

        return rationale


maintenance_decision_engine = (
    MaintenanceDecisionEngine()
)
