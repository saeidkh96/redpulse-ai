from app.mlops.serving import ModelServingRouter


def test_model_serving_router():
    router = ModelServingRouter()
    router.register("failure-risk", "1", lambda payload: {"risk": payload["x"] * 2}, default=True)
    result = router.predict("failure-risk", {"x": 0.3})
    assert result["version"] == "1"
    assert result["prediction"]["risk"] == 0.6
