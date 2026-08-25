from app.deviation.engine import deviation_engine


def test_normal_behavior() -> None:
    result = deviation_engine.compare(
        baseline_sensors={
            "vibration": {
                "mean": 2.0,
                "std": 0.2,
            },
            "temperature": {
                "mean": 60.0,
                "std": 2.0,
            },
        },
        baseline_correlations={
            "rpm__vibration": 0.40,
        },
        current_sensors={
            "vibration": {
                "mean": 2.05,
                "std": 0.21,
            },
            "temperature": {
                "mean": 60.5,
                "std": 2.1,
            },
        },
        current_correlations={
            "rpm__vibration": 0.42,
        },
    )

    assert result.severity == "normal"
    assert result.overall_score < 0.20


def test_warning_behavior() -> None:
    result = deviation_engine.compare(
        baseline_sensors={
            "vibration": {
                "mean": 2.0,
                "std": 0.2,
            },
        },
        baseline_correlations={
            "rpm__vibration": 0.40,
        },
        current_sensors={
            "vibration": {
                "mean": 2.35,
                "std": 0.30,
            },
        },
        current_correlations={
            "rpm__vibration": 0.65,
        },
    )

    assert result.severity == "warning"
    assert 0.20 <= result.overall_score < 0.50


def test_anomalous_behavior() -> None:
    result = deviation_engine.compare(
        baseline_sensors={
            "vibration": {
                "mean": 2.0,
                "std": 0.2,
            },
            "temperature": {
                "mean": 60.0,
                "std": 2.0,
            },
        },
        baseline_correlations={
            "rpm__vibration": 0.40,
        },
        current_sensors={
            "vibration": {
                "mean": 3.0,
                "std": 0.7,
            },
            "temperature": {
                "mean": 68.0,
                "std": 4.5,
            },
        },
        current_correlations={
            "rpm__vibration": 0.95,
        },
    )

    assert result.severity == "anomalous"
    assert result.overall_score >= 0.50


def test_missing_current_sensor_is_ignored() -> None:
    result = deviation_engine.compare(
        baseline_sensors={
            "vibration": {
                "mean": 2.0,
                "std": 0.2,
            },
            "temperature": {
                "mean": 60.0,
                "std": 2.0,
            },
        },
        baseline_correlations={},
        current_sensors={
            "vibration": {
                "mean": 2.0,
                "std": 0.2,
            },
        },
        current_correlations={},
    )

    assert "vibration" in result.sensor_deviations
    assert "temperature" not in result.sensor_deviations
