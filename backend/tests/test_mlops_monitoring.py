from app.mlops.monitoring import ModelMonitoringEngine


def test_monitoring_detects_distribution_shift():
    engine = ModelMonitoringEngine()
    result = engine.analyze(
        reference_predictions=[0.1, 0.2, 0.15, 0.18],
        current_predictions=[0.7, 0.8, 0.75, 0.9],
        reference_features={"vibration": [1.0, 1.1, 0.9, 1.05]},
        current_features={"vibration": [2.0, 2.1, 1.9, 2.2]},
    )
    assert result.prediction_drift_score > 0.5
    assert result.state in {"degraded", "critical"}
