from app.lakehouse_v32 import MedallionPipeline
from app.governance_v33 import UnityCatalogGovernance
from app.databricks_deploy_v34 import AssetBundlePlanner,DatabricksJobSpec,DeploymentTarget
from app.streaming_scale_v35 import EventEnvelope,FleetPartitionPlanner,MicroBatchProcessor
from app.orchestration_v36 import DagSpec,PipelineTask,RetrainingOrchestrator
from app.mlops_v37 import ModelRegistry,ModelVersion,PromotionGate
from app.platform_hardening_v39 import PlatformHardening,SLO
from app.operational_validation_v40 import OperationalEvidence,OperationalValidator
def test_medallion():
 r=MedallionPipeline().process({'machine_id':'M1','ts':'2026-08-29T00:00:00Z','metrics':{'temperature':65,'vibration':2.1}}); assert set(r)=={'bronze','silver','gold'}
def test_governance():
 g=UnityCatalogGovernance(); g.grant('eng','redpulse.gold',['SELECT']); assert g.can('eng','redpulse.gold','select')
def test_dab():
 r=AssetBundlePlanner().render(DeploymentTarget('dev','https://example','redpulse','industrial'),[DatabricksJobSpec('job','./job.py')]); assert 'job' in r['resources']['jobs']
def test_scale():
 assert sorted(FleetPartitionPlanner.partition(['A','B'],2))==[0,1]; e=[EventEnvelope('t',str(i),{'i':i}) for i in range(5)]; assert MicroBatchProcessor(2).run(e,lambda b:len(b))==[2,2,1]
def test_orchestration():
 d=DagSpec('d','@daily',[PipelineTask('a'),PipelineTask('b',('a',))]); d.validate(); assert RetrainingOrchestrator().plan('m',.8,.5)['should_retrain']
def test_mlops():
 r=ModelRegistry(); r.register(ModelVersion('m','1',{'f1':.8})); r.promote('m','1'); assert PromotionGate.evaluate(.8,.9,.2,.1)['promote']
def test_validation():
 assert PlatformHardening.evaluate_slo(.999,100,SLO())['ready']; out=OperationalValidator().evaluate(OperationalEvidence(True,True,True,True)); assert out['ready'] and not out['production_validated']
