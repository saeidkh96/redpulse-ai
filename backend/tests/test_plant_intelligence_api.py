from app.api.v1.plant_intelligence import router


def test_plant_router_exposes_all_endpoints():
    paths = {route.path for route in router.routes}
    assert "/plant/sites/summary" in paths
    assert "/plant/fleet-early-warning" in paths
    assert "/plant/fleet-risk-forecast" in paths
    assert "/plant/maintenance-plan" in paths
