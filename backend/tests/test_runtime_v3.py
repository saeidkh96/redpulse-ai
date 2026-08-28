from pathlib import Path
from app.runtime_v3.engine import PersistentJobRuntime
from app.runtime_v3.persistence import JsonRuntimeRepository
from app.runtime_v3.models import RuntimeStatus
from app.runtime_v3.idempotency import idempotency_key

def test_persistent_job_runtime(tmp_path: Path):
    repo = JsonRuntimeRepository(tmp_path / "runtime.json")
    runtime = PersistentJobRuntime(repo)
    rec = runtime.submit("t1", "demo", {"x": 1})
    out = runtime.run(rec.record_id, lambda r: {"ok": True})
    assert out.status == RuntimeStatus.SUCCEEDED
    assert repo.get(rec.record_id).payload["result"]["ok"] is True

def test_idempotency_is_stable():
    assert idempotency_key("x", {"b":2,"a":1}) == idempotency_key("x", {"a":1,"b":2})
