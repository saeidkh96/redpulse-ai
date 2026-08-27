from app.api.v1.fleet_intelligence import router


def test_fleet_router_exposes_all_milestone_endpoints():
    paths = {route.path for route in router.routes}
    assert "/fleet/peer-groups" in paths
    assert "/fleet/health" in paths
    assert "/fleet/failure-hotspots" in paths
    assert "/fleet/maintenance-priorities" in paths
