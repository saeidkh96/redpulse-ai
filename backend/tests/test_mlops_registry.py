from app.mlops.registry import ModelRegistry, ModelVersion


def test_registry_register_and_promote(tmp_path):
    registry = ModelRegistry(tmp_path / "registry.json")
    registry.register(ModelVersion("failure-risk", "1", "file://model", "sklearn"))
    registry.transition_stage("failure-risk", "1", "champion")
    champion = registry.champion("failure-risk")
    assert champion is not None
    assert champion.version == "1"
