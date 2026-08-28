from app.mlops.lifecycle import ModelLifecycleManager
from app.mlops.registry import ModelRegistry, ModelVersion


def test_lifecycle_archives_old_champion(tmp_path):
    registry = ModelRegistry(tmp_path / "registry.json")
    registry.register(ModelVersion("risk", "1", "a", "sklearn", stage="champion"))
    registry.register(ModelVersion("risk", "2", "b", "sklearn", stage="challenger"))
    result = ModelLifecycleManager(registry).promote_to_champion("risk", "2")
    assert result.promoted_version == "2"
    assert "1" in result.archived_versions
