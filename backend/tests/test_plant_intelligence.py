from app.plant.site_intelligence import PlantFleetInput, plant_intelligence_engine


def test_plant_intelligence_aggregates_multiple_fleets():
    result = plant_intelligence_engine.summarize([
        PlantFleetInput("site-a", "fleet-1", 80, 0.2, 1, 2, 10, 1),
        PlantFleetInput("site-a", "fleet-2", 40, 0.8, 3, 4, 10, 3),
    ])
    assert len(result) == 1
    assert result[0].fleet_count == 2
    assert result[0].machine_count == 20
    assert result[0].plant_health_score == 60.0
    assert result[0].plant_risk_score == 0.5
