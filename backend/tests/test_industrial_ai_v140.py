from app.knowledge.ingestion import KnowledgeIngestionService
from app.knowledge.store import InMemoryKnowledgeStore
from app.copilot.context import MachineContext
from app.copilot.service import EvidenceGroundedCopilot
from app.agents.runtime import AgentRuntime, ToolRegistry, RunStatus
from app.agents.planner import MaintenancePlanner
from app.enterprise.security import Principal, RBAC

def test_rag_retrieval_and_citations():
    store = InMemoryKnowledgeStore()
    chunks = KnowledgeIngestionService(chunk_size=80, overlap=10).chunk(
        "manual-1", "Bearing temperature above 90 C requires inspection of lubrication and alignment."
    )
    store.upsert(chunks)
    result = EvidenceGroundedCopilot(store).answer(
        "bearing temperature inspection",
        MachineContext(machine_id="M-1"),
    )
    assert result["evidence_count"] >= 1
    assert result["citations"][0]["source_id"] == "manual-1"

def test_agent_human_approval_and_audit():
    tools = ToolRegistry()
    tools.register("echo", lambda value: value)
    runtime = AgentRuntime(tools)
    run = runtime.create("inspect machine")
    runtime.require_approval(run, "sensitive action")
    assert run.status == RunStatus.WAITING_APPROVAL
    runtime.approve(run.run_id, "engineer")
    assert runtime.execute_tool(run.run_id, "echo", value="ok") == "ok"
    runtime.complete(run.run_id)
    assert run.status == RunStatus.COMPLETED
    assert len(run.audit) >= 4

def test_planner_has_post_maintenance_verification():
    plan = MaintenancePlanner().plan("repair pump")
    assert plan[-1]["action"] == "verify_post_maintenance_outcome"

def test_rbac():
    rbac = RBAC()
    principal = Principal("u1", "tenant-a", frozenset({"approver"}))
    assert rbac.allowed(principal, "approve_maintenance")
    assert not rbac.allowed(principal, "propose_maintenance")
