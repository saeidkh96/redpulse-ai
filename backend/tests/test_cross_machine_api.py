from app.api.v1.cross_machine import router


def test_cross_machine_router_exposes_analysis_endpoint():
    paths = [route.path for route in router.routes]
    assert "/machines/{machine_id}/cross-machine-learning" in paths
