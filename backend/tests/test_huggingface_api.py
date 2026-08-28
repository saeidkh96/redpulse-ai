def test_huggingface_routes_exist():
    from app.main import app
    paths=app.openapi()["paths"]
    assert "/api/v1/huggingface/models/inspect" in paths
    assert "/api/v1/huggingface/models/pull" in paths
    assert "/api/v1/huggingface/generate" in paths
