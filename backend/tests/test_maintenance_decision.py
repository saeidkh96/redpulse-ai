from types import SimpleNamespace

from app.maintenance.decision import (
    MaintenanceActionType,
    MaintenanceDecisionEngine,
    MaintenanceDecisionInput,
    MaintenancePriority,
)


def make_prediction(
    *,
    risk_score: float,
    confidence: float,
    failure_match_score: float,
):
    return SimpleNamespace(
        risk=SimpleNamespace(
            risk_score=risk_score,
            confidence=confidence,
        ),
        failure_match_score=failure_match_score,
        likely_failure_type=(
            "spindle_bearing_degradation"
        ),
    )


def make_explanation():
    return SimpleNamespace(
        primary_driver="Behavioral drift",
        root_cause_hints=[
            SimpleNamespace(
                cause="Possible bearing degradation",
                confidence=0.82,
                supporting_evidence=[
                    "vibration",
                    "temperature",
                ],
            )
        ],
        evidence=[
            SimpleNamespace(
                category=SimpleNamespace(
                    value="sensor"
                ),
                name="Sensor: vibration",
            ),
            SimpleNamespace(
                category=SimpleNamespace(
                    value="drift"
                ),
                name="Behavioral drift",
            ),
            SimpleNamespace(
                category=SimpleNamespace(
                    value="deviation"
                ),
                name="Behavioral deviation",
            ),
        ],
    )


def decide(
    *,
    risk_score: float,
    confidence: float,
    failure_match_score: float,
):
    engine = MaintenanceDecisionEngine()

    return engine.decide(
        MaintenanceDecisionInput(
            prediction=make_prediction(
                risk_score=risk_score,
                confidence=confidence,
                failure_match_score=(
                    failure_match_score
                ),
            ),
            explanation=make_explanation(),
        )
    )


def test_low_urgency_is_routine():
    result = decide(
        risk_score=0.20,
        confidence=0.20,
        failure_match_score=0.20,
    )

    assert (
        result.priority
        == MaintenancePriority.ROUTINE
    )
    assert (
        result.action_type
        == MaintenanceActionType.MONITOR
    )


def test_moderate_urgency_is_scheduled():
    result = decide(
        risk_score=0.40,
        confidence=0.40,
        failure_match_score=0.40,
    )

    assert (
        result.priority
        == MaintenancePriority.SCHEDULED
    )
    assert (
        result.action_type
        == MaintenanceActionType.INSPECT
    )


def test_high_urgency_is_urgent():
    result = decide(
        risk_score=0.65,
        confidence=0.65,
        failure_match_score=0.65,
    )

    assert (
        result.priority
        == MaintenancePriority.URGENT
    )
    assert (
        result.action_type
        == MaintenanceActionType.SCHEDULE_MAINTENANCE
    )


def test_critical_urgency_is_immediate():
    result = decide(
        risk_score=0.85,
        confidence=0.90,
        failure_match_score=0.95,
    )

    assert (
        result.priority
        == MaintenancePriority.IMMEDIATE
    )
    assert (
        result.action_type
        == MaintenanceActionType.STOP_AND_INSPECT
    )


def test_urgency_score_formula():
    result = decide(
        risk_score=0.80,
        confidence=0.70,
        failure_match_score=0.90,
    )

    expected = (
        0.80 * 0.55
        + 0.70 * 0.20
        + 0.90 * 0.25
    )

    assert result.urgency_score == round(
        expected,
        4,
    )


def test_decision_contains_recommended_action():
    result = decide(
        risk_score=0.85,
        confidence=0.90,
        failure_match_score=0.95,
    )

    assert result.recommended_action
    assert isinstance(
        result.recommended_action,
        str,
    )

    assert (
        "spindle_bearing_degradation"
        in result.recommended_action
    )


def test_decision_extracts_affected_signals():
    result = decide(
        risk_score=0.65,
        confidence=0.75,
        failure_match_score=0.80,
    )

    assert "Sensor: vibration" in (
        result.affected_signals
    )

    assert "Behavioral drift" in (
        result.affected_signals
    )

    assert "Behavioral deviation" not in (
        result.affected_signals
    )


def test_decision_extracts_root_cause_hints():
    result = decide(
        risk_score=0.65,
        confidence=0.75,
        failure_match_score=0.80,
    )

    assert result.root_cause_hints == [
        "Possible bearing degradation"
    ]


def test_decision_contains_rationale():
    result = decide(
        risk_score=0.65,
        confidence=0.75,
        failure_match_score=0.80,
    )

    assert result.rationale
    assert len(result.rationale) >= 5

    assert any(
        "Maintenance urgency score"
        in item
        for item in result.rationale
    )

    assert any(
        "Primary failure driver"
        in item
        for item in result.rationale
    )


def test_input_values_are_clamped():
    result = decide(
        risk_score=2.0,
        confidence=-1.0,
        failure_match_score=3.0,
    )

    expected = (
        1.0 * 0.55
        + 0.0 * 0.20
        + 1.0 * 0.25
    )

    assert result.urgency_score == round(
        expected,
        4,
    )

    assert (
        result.priority
        == MaintenancePriority.IMMEDIATE
    )
