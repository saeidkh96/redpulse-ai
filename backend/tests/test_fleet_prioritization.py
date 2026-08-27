from app.fleet.prioritization import (
    MaintenancePriorityInput,
    fleet_maintenance_prioritization_engine,
)


def test_prioritization_respects_capacity_and_risk():
    result = fleet_maintenance_prioritization_engine.prioritize([
        MaintenancePriorityInput("healthy", 90, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2),
        MaintenancePriorityInput("critical", 20, 0.95, 0.9, 0.85, 0.8, 0.9, 0.8),
        MaintenancePriorityInput("medium", 60, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4),
    ], capacity=2)
    assert len(result) == 2
    assert result[0].machine_id == "critical"
    assert "HIGH_FAILURE_RISK" in result[0].reason_codes
