from app.platform_v40.agents import AgenticMaintenanceOrchestrator
from app.platform_v40.intelligence import IntelligenceInput, PredictiveMaintenanceEngine
from app.platform_v40.integrations import DeliveryRequest, EnterpriseIntegrationGateway, IntegrationAdapter


def run_demo() -> dict:
    decision = PredictiveMaintenanceEngine().evaluate(
        IntelligenceInput("pump-17", (0.10, 0.20, 0.15), (0.95, 0.90, 0.88), 0.85, 0.91, 0.05)
    )
    agents = AgenticMaintenanceOrchestrator()
    workflow = agents.create(decision)
    agents.approve(workflow, "demo-human-operator")
    gateway = EnterpriseIntegrationGateway()
    gateway.register(IntegrationAdapter.WEBHOOK, lambda request: {"accepted": True, "machine": request.payload["machine_id"]})
    receipt = gateway.dispatch(
        DeliveryRequest(
            IntegrationAdapter.WEBHOOK,
            "demo-tenant",
            "maintenance-approved",
            workflow.id,
            {"machine_id": workflow.machine_id, "risk": workflow.risk},
        )
    )
    agents.mark_dispatched(workflow)
    agents.verify(workflow, recovered=True)
    return {"decision": decision, "workflow": workflow, "delivery": receipt}


if __name__ == "__main__":
    print(run_demo())
