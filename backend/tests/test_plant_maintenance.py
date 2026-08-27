from app.plant.maintenance import PlantMaintenanceInput, plant_maintenance_engine


def test_plant_maintenance_respects_site_capacity():
    plans = plant_maintenance_engine.plan([
        PlantMaintenanceInput(
            "site-a", "fleet-1", "m-critical",
            0.95, 0.9, 0.9, 0.8, 0.9, 2, 1
        ),
        PlantMaintenanceInput(
            "site-a", "fleet-1", "m-low",
            0.2, 0.2, 0.2, 0.1, 0.2, 1, 1
        ),
    ], capacity_by_site={"site-a": 1})

    assert len(plans) == 1
    assert plans[0].selected_actions[0].machine_id == "m-critical"
    assert "m-low" in plans[0].deferred_machine_ids
