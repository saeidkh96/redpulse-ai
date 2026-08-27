import asyncio
import uuid
from types import SimpleNamespace

from app.services.cross_machine import CrossMachineLearningService


def machine(machine_id, machine_type="cnc", manufacturer="acme", model="x1"):
    return SimpleNamespace(
        id=machine_id,
        machine_type=machine_type,
        manufacturer=manufacturer,
        model=model,
    )


def test_metadata_similarity_prefers_matching_model_and_manufacturer():
    service = CrossMachineLearningService()
    target = machine(uuid.uuid4())
    exact = machine(uuid.uuid4())
    different = machine(uuid.uuid4(), manufacturer="other", model="x2")

    assert service._metadata_similarity(target, exact) == 1.0
    assert service._metadata_similarity(target, different) == 0.5


def test_service_rejects_missing_machine(monkeypatch):
    async def run():
        service = CrossMachineLearningService()

        async def fake_get(*args, **kwargs):
            return None

        monkeypatch.setattr(
            "app.services.cross_machine.cross_machine_repository.get_machine",
            fake_get,
        )

        try:
            await service.analyze(object(), machine_id=uuid.uuid4())
        except LookupError:
            return
        raise AssertionError("Expected LookupError")

    asyncio.run(run())
