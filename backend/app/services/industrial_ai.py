from app.knowledge.ingestion import KnowledgeIngestionService
from app.knowledge.store import InMemoryKnowledgeStore
from app.copilot.context import MachineContext
from app.copilot.service import EvidenceGroundedCopilot
from app.agents.runtime import ToolRegistry, AgentRuntime
from app.agents.planner import MaintenancePlanner
from app.integrations_gateway.gateway import IntegrationGateway

class IndustrialAIService:
    def __init__(self) -> None:
        self.store = InMemoryKnowledgeStore()
        self.ingestion = KnowledgeIngestionService()
        self.copilot = EvidenceGroundedCopilot(self.store)
        self.tools = ToolRegistry()
        self.agents = AgentRuntime(self.tools)
        self.planner = MaintenancePlanner()
        self.integrations = IntegrationGateway()

    def ingest(self, source_id: str, text: str, metadata: dict) -> dict:
        chunks = self.ingestion.chunk(source_id, text, metadata)
        return {"source_id": source_id, "chunks": self.store.upsert(chunks)}

    def ask(self, body) -> dict:
        context = MachineContext(
            machine_id=body.machine_id,
            machine_dna=body.machine_dna,
            telemetry=body.telemetry,
            health=body.health,
            failure_risk=body.failure_risk,
            maintenance_history=body.maintenance_history,
        )
        return self.copilot.answer(body.question, context)

industrial_ai_service = IndustrialAIService()
