from app.api.v1.data_platform import router

def test_data_platform_router_exposes_endpoints():
    paths = {route.path for route in router.routes}
    assert "/data-platform/events/publish" in paths
    assert "/data-platform/events/recent" in paths
    assert "/data-platform/analytics/run" in paths
