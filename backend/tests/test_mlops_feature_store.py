from app.mlops.feature_store import FeatureStore


def test_feature_store_round_trip(tmp_path):
    store = FeatureStore(tmp_path / "features.json")
    store.put("machine-1", "health", {"risk": 0.8})
    assert store.get("machine-1", "health")["risk"] == 0.8
