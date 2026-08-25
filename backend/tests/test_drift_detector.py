from app.drift.detector import drift_detector


def test_stable_signal() -> None:
    result = drift_detector.analyze_signal(
        [
            1.00,
            1.02,
            0.99,
            1.01,
            1.00,
        ]
    )

    assert result.state == "stable"
    assert result.score < 0.30


def test_emerging_drift_signal() -> None:
    result = drift_detector.analyze_signal(
        [
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
        ]
    )

    assert result.state in {
        "emerging",
        "drifting",
    }


def test_strong_drift_signal() -> None:
    result = drift_detector.analyze_signal(
        [
            1.0,
            1.5,
            2.0,
            2.5,
            3.0,
        ]
    )

    assert result.state == "drifting"
    assert result.score >= 0.60


def test_negative_drift_signal() -> None:
    result = drift_detector.analyze_signal(
        [
            10.0,
            9.0,
            8.0,
            7.0,
            6.0,
        ]
    )

    assert result.state == "drifting"


def test_multi_signal_report() -> None:
    result = drift_detector.analyze(
        {
            "vibration": [
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
            ],
            "temperature": [
                60.0,
                60.2,
                60.4,
                60.6,
                60.8,
            ],
            "load": [
                65.0,
                65.1,
                64.9,
                65.0,
                65.1,
            ],
        }
    )

    assert "vibration" in result.signals
    assert "temperature" in result.signals
    assert "load" in result.signals

    assert 0.0 <= result.overall_score <= 1.0


def test_empty_history_rejected() -> None:
    try:
        drift_detector.analyze({})
    except ValueError as exc:
        assert str(exc) == (
            "signal_history must not be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_short_histories_rejected() -> None:
    try:
        drift_detector.analyze(
            {
                "vibration": [1.0, 1.1],
            }
        )
    except ValueError as exc:
        assert str(exc) == (
            "at least one signal with three values is required"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )
