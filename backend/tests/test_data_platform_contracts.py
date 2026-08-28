from app.data_platform.contracts import AnalyticsJob, DataTier, TelemetryStoragePlan

def test_data_platform_contracts():
    plan = TelemetryStoragePlan()
    assert plan.hot_store == "timescaledb"
    assert DataTier.COLD.value == "cold"
    job = AnalyticsJob(name="fleet-analytics", input_path="in", output_path="out")
    assert job.engine == "spark"
