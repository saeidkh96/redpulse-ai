from app.fleet.peer_groups import peer_group_engine
from app.fleet.similarity import MachineBehaviorProfile, machine_similarity_engine


def profile(mid, model="x1", dna=None, operating=None):
    return MachineBehaviorProfile(
        machine_id=mid,
        machine_type="cnc",
        manufacturer="acme",
        model=model,
        dna=dna or {"vibration": 1.0, "temperature": 0.5},
        operating_profile=operating or {"load": 0.8, "speed": 0.6},
    )


def test_identical_behavior_is_highly_similar():
    result = machine_similarity_engine.compare(profile("a"), profile("b"))
    assert result.score > 0.95


def test_peer_group_filters_dissimilar_machines():
    target = profile("target")
    close = profile("close")
    far = profile(
        "far",
        model="x9",
        dna={"vibration": -1.0, "temperature": -0.5},
        operating={"load": -0.8, "speed": -0.6},
    )
    group = peer_group_engine.build(
        target, [close, far], minimum_similarity=0.70
    )
    assert [p.machine_id for p in group.peers] == ["close"]
