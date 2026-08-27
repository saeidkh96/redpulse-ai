from app.plant.risk_forecasting import FleetRiskObservation, fleet_risk_forecasting_engine


def test_risk_forecast_projects_rising_risk():
    result = fleet_risk_forecasting_engine.forecast([
        FleetRiskObservation(1, 0.30, 80, 0.2, 0.2),
        FleetRiskObservation(2, 0.40, 75, 0.3, 0.3),
        FleetRiskObservation(3, 0.55, 68, 0.5, 0.5),
    ], horizon_steps=3)
    assert result.predicted_risk > result.current_risk
    assert result.predicted_health < 68
    assert result.confidence > 0.0
