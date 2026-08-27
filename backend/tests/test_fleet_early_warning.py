from app.plant.early_warning import FleetEarlyWarningInput, fleet_early_warning_engine


def test_early_warning_detects_rising_risk():
    result = fleet_early_warning_engine.analyze(
        FleetEarlyWarningInput(
            fleet_id="fleet-a",
            current_risk=0.85,
            previous_risk=0.55,
            current_health=45,
            previous_health=70,
            critical_machine_ratio=0.3,
            hotspot_severity=0.8,
            drift_pressure=0.75,
            maintenance_backlog_ratio=0.4,
        )
    )
    assert result.warning_score > 0.35
    assert "RISK_ACCELERATION" in result.reason_codes
    assert "HEALTH_DETERIORATION" in result.reason_codes
