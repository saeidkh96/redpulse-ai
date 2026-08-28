from pydantic import BaseModel, Field


class RegisterModelRequest(BaseModel):
    model_name: str
    version: str
    artifact_uri: str
    framework: str
    metrics: dict[str, float] = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)


class ExperimentRunRequest(BaseModel):
    experiment_name: str
    parameters: dict = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    tags: dict[str, str] = Field(default_factory=dict)


class MonitoringRequest(BaseModel):
    reference_predictions: list[float]
    current_predictions: list[float]
    reference_features: dict[str, list[float]] = Field(default_factory=dict)
    current_features: dict[str, list[float]] = Field(default_factory=dict)


class ControlPlaneRequest(MonitoringRequest):
    model_name: str
    new_failure_samples: int = Field(default=0, ge=0)
    days_since_training: int = Field(default=0, ge=0)


class PromotionRequest(BaseModel):
    model_name: str
    version: str


class FeatureWriteRequest(BaseModel):
    entity_id: str
    feature_group: str
    features: dict
