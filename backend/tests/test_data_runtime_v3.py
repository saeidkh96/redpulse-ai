from app.data_runtime_v3.quality import DataQualityGate
from app.data_runtime_v3.pipeline import ReplayBuffer, PipelineEvent
from app.data_runtime_v3.lineage import LineageRegistry, LineageEntry

def test_quality():
    assert DataQualityGate().validate({"a":1}, {"a"})["valid"]
    assert not DataQualityGate().validate({"a":None}, {"a"})["valid"]

def test_replay_and_lineage():
    b = ReplayBuffer()
    b.append(PipelineEvent("t","k",{"x":1}))
    assert len(b.replay("t")) == 1
    r = LineageRegistry()
    r.record(LineageEntry("s","d1","f1","m1","p1"))
    assert r.entries[0].prediction_id == "p1"
