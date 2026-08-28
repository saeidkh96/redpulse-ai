from __future__ import annotations
from app.runtime_v3.engine import PersistentJobRuntime
from app.ml_runtime_v3.models import FailureRiskModel, RemainingUsefulLifeModel

class ProductionDemoService:
    def __init__(self, runtime: PersistentJobRuntime | None = None) -> None:
        self.runtime = runtime or PersistentJobRuntime()
        self.failure_model = FailureRiskModel()
        self.rul_model = RemainingUsefulLifeModel()

    def run(self, tenant_id: str, machine_id: str, signals: dict[str, float]) -> dict:
        risk = self.failure_model.predict(signals)
        rul = self.rul_model.predict(signals)
        recommendation = "inspect" if risk["failure_risk"] >= 0.5 else "continue_monitoring"
        record = self.runtime.submit(
            tenant_id=tenant_id,
            kind="maintenance_decision",
            payload={
                "machine_id": machine_id,
                "signals": signals,
                "failure_risk": risk,
                "rul": rul,
                "recommendation": recommendation,
            },
        )
        return {
            "record_id": record.record_id,
            "machine_id": machine_id,
            "failure_risk": risk,
            "remaining_useful_life": rul,
            "recommendation": recommendation,
            "requires_approval": recommendation == "inspect",
        }

production_demo_service = ProductionDemoService()
