from pydantic import BaseModel,Field
class LakehouseProcessRequest(BaseModel): machine_id:str; ts:str; metrics:dict[str,float]
class GovernanceGrantRequest(BaseModel): principal:str; securable:str; privileges:list[str]
class DigitalPlatformReadinessRequest(BaseModel): availability:float=Field(ge=0,le=1); p95_latency_ms:float=Field(ge=0)
class OperationalValidationRequest(BaseModel): ci_passed:bool; migrations_passed:bool; docker_build_passed:bool; security_scan_passed:bool; load_test_passed:bool=False; recovery_drill_passed:bool=False; deployment_verified:bool=False
