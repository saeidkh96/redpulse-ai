from app.api.v1.mlops_platform import router


def test_mlops_router_exposes_platform_endpoints():
    paths = {route.path for route in router.routes}
    assert "/mlops/models" in paths
    assert "/mlops/experiments" in paths
    assert "/mlops/control-plane/assess" in paths
    assert "/mlops/models/promote" in paths
    assert "/mlops/features" in paths
