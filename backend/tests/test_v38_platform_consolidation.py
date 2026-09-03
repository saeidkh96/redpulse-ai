from app.platform_v38.runtime import RetryPolicy,FailureEngine,FailureClass
from app.platform_v38.outbox import TransactionalOutbox
from app.platform_v38.events import IndustrialEvent,IdempotentConsumer
from app.platform_v38.fleet import MachineVector,FleetSimilarity
from app.platform_v38.mlops import ModelLifecycle,ModelRecord,ModelStage
from app.platform_v38.failure_intelligence import FailureEstimator
from app.platform_v38.agents import MaintenanceAgent
from app.platform_v38.integrations import IntegrationGateway,IntegrationMessage,Adapter
from app.platform_v38.security import Authorization,Principal
from app.platform_v38.sre import SLO,RuntimeMetrics
from app.platform_v38.benchmark import BenchmarkHarness
from app.platform_v38.release import V38Evidence,V38ReleaseGate

def test_v38_consolidated_capabilities():
    attempts={"n":0}
    def flaky():
        attempts["n"]+=1
        if attempts["n"]<2: raise TimeoutError("transient")
        return "ok"
    engine=FailureEngine(RetryPolicy(max_attempts=2,base_delay_seconds=0,jitter_ratio=0))
    assert engine.execute("x",{},flaky,lambda e:FailureClass.TRANSIENT)=="ok"
    outbox=TransactionalOutbox(); ev=outbox.add("maintenance","m1",{"risk":.8}); assert len(outbox.pending())==1; outbox.mark_delivered(ev.id); assert not outbox.pending()
    consumer=IdempotentConsumer(); event=IndustrialEvent("telemetry","m1",1,{"v":1}); assert consumer.consume("e1",lambda e:e.key,event)["value"]=="m1"; assert consumer.consume("e1",lambda e:None,event)["duplicate"]
    ranks=FleetSimilarity().rank(MachineVector("a",(1,0)),[MachineVector("b",(1,0)),MachineVector("c",(0,1))]); assert ranks[0][0]=="b"
    life=ModelLifecycle(); life.register(ModelRecord("risk","1",.8)); assert life.promote("risk","1").stage is ModelStage.CHAMPION
    est=FailureEstimator().estimate(.9,.8,.9,.05); assert est.risk>.5 and est.confidence==.95 and est.evidence
    proposal=MaintenanceAgent().propose("m1",list(est.evidence),est.risk); assert proposal.requires_human_approval
    gateway=IntegrationGateway(); gateway.register(Adapter.WEBHOOK,lambda m:m.idempotency_key); assert gateway.dispatch(Adapter.WEBHOOK,IntegrationMessage("risk","t1","k1",{}))=="k1"
    Authorization.require(Principal("u","t1",frozenset({"operator"})),"t1","operator")
    assert all(SLO().evaluate(.999,100).values()); metrics=RuntimeMetrics(); metrics.recovery(.2); assert metrics.mean_recovery_seconds==.2
    assert BenchmarkHarness().run(10,lambda i:i).operations==10
    evidence=V38Evidence(**{k:True for k in V38Evidence.__dataclass_fields__}); assert V38ReleaseGate().evaluate(evidence)["ready"]
