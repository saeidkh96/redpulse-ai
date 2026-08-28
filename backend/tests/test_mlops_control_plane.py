from app.mlops.control_plane import MLOpsControlPlane
from app.mlops.registry import ModelRegistry, ModelVersion


def test_control_plane_uses_champion_and_monitoring(tmp_path):
    registry = ModelRegistry(tmp_path / "registry.json")
    registry.register(ModelVersion("risk", "1", "file://risk", "sklearn", stage="champion"))
    plane = MLOpsControlPlane(registry)
    result = plane.assess(
        model_name="risk",
        reference_predictions=[0.1, 0.2, 0.15],
        current_predictions=[0.6, 0.7, 0.8],
        new_failure_samples=60,
        days_since_training=70,
    )
    assert result.champion_version == "1"
