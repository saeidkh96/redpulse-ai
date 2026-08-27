from app.fleet.hotspots import FleetFailureEvidence, fleet_failure_hotspot_engine


def test_failure_hotspots_rank_shared_failure_mode():
    result = fleet_failure_hotspot_engine.detect([
        FleetFailureEvidence("a", "bearing", 0.9, 0.9, 30),
        FleetFailureEvidence("b", "bearing", 0.8, 0.8, 40),
        FleetFailureEvidence("c", "cooling", 0.5, 0.4, 70),
    ])
    assert result[0].failure_mode == "bearing"
    assert result[0].affected_machines == 2
