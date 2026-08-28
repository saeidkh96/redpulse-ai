from pathlib import Path
from app.production_engineering_v31.core import DurableJsonStore,PersistentRecord,ConsumerRuntime,StreamMessage,ReleaseGate
from app.production_engineering_v31.mlops import ModelRegistryV31,ModelVersion
from app.digital_twin_v31.core import TwinState,Scenario,MachineDigitalTwin,FleetDigitalTwin
from app.advanced_predictive_v31.core import UncertaintyEstimator,MultimodalFusionEngine,CausalMaintenanceEstimator,ProbabilisticRUL

def test_phase3(tmp_path:Path):
    store=DurableJsonStore(tmp_path/'s.json'); store.upsert(PersistentRecord('r','t','job',{'x':1})); assert store.get('r').payload['x']==1
    assert ConsumerRuntime().process(StreamMessage('t','k',{'x':1}),lambda m:2)['status']=='processed'
    reg=ModelRegistryV31(); reg.register(ModelVersion('risk','1',.8)); reg.promote('risk','1'); assert reg.champion('risk').version=='1'
    assert ReleaseGate().evaluate({'compile':1,'tests':1,'lint':1,'security':1,'docker_build':1})['release_ready']

def test_phase4():
    twin=MachineDigitalTwin(TwinState('m1',telemetry={'load':.6,'vibration':.4},health_score=.8,drift_score=.2)); out=twin.simulate(Scenario('stress',{'load':.9},48)); assert 0<=out.projected_risk<=1
    fleet=FleetDigitalTwin(); fleet.register(twin); assert fleet.simulate(Scenario('x',{},24))['risk_ranking']==['m1']

def test_phase5():
    assert UncertaintyEstimator().interval(.7,.1).lower==.6
    assert 0<=MultimodalFusionEngine().fuse({'a':(.8,.9),'b':(.5,.4)})['fused_score']<=1
    assert CausalMaintenanceEstimator().estimate('repair',.8,.5,10).expected_risk_delta<0
    r=ProbabilisticRUL().estimate(.8,.2); assert r['p10_hours']<=r['mean_hours']<=r['p90_hours']
