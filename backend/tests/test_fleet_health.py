from app.fleet.health import MachineFleetState, fleet_health_engine


def test_fleet_health_classifies_machine_states():
    result = fleet_health_engine.summarize([
        MachineFleetState("a", 92, 0.10, 0.10),
        MachineFleetState("b", 60, 0.55, 0.50),
        MachineFleetState("c", 25, 0.90, 0.80),
    ])
    assert result.machine_count == 3
    assert result.critical_machine_count == 1
    assert result.degraded_machine_count == 1
    assert result.healthy_machine_count == 1
