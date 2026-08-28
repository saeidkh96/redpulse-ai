from pydantic import BaseModel, Field
class TwinCreateRequest(BaseModel):
    machine_id:str; telemetry:dict[str,float]=Field(default_factory=dict); health_score:float=1.0; deviation_score:float=0.0; drift_score:float=0.0
class TwinScenarioRequest(BaseModel):
    machine_id:str; name:str='what-if'; overrides:dict[str,float]=Field(default_factory=dict); horizon_hours:float=24.0
class FusionRequest(BaseModel): modalities:dict[str,tuple[float,float]]
class RULRequest(BaseModel): health_score:float; drift_score:float; max_hours:float=1000.0
