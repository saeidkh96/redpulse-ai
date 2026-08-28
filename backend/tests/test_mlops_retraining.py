from app.mlops.retraining import RetrainingContext, RetrainingPolicyEngine


def test_retraining_policy_triggers_on_drift():
    result = RetrainingPolicyEngine().decide(
        RetrainingContext(
            feature_drift_score=0.8,
            prediction_drift_score=0.7,
            quality_score=0.4,
            new_failure_samples=80,
            days_since_training=70,
        )
    )
    assert result.should_retrain is True
    assert "FEATURE_DRIFT" in result.reason_codes
