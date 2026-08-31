from app.streaming.health import StreamingHealthService
from app.streaming.lakehouse import StreamingLakehousePlanner
from app.streaming.metrics import StreamingMetrics


def test_streaming_health_is_ready_when_metrics_are_clean():
    metrics = StreamingMetrics()
    metrics.record_published("redpulse.telemetry", 10)
    metrics.record_consumed(10)
    metrics.set_consumer_lag("redpulse-telemetry-processors", 0)

    health = StreamingHealthService(metrics).snapshot()

    assert health.status == "ok"
    assert health.ready is True
    assert health.total_consumer_lag == 0


def test_streaming_health_degrades_on_large_consumer_lag():
    metrics = StreamingMetrics()
    metrics.set_consumer_lag("redpulse-telemetry-processors", 150)

    health = StreamingHealthService(metrics).snapshot()

    assert health.status == "degraded"
    assert health.ready is False
    assert health.total_consumer_lag == 150


def test_streaming_health_degrades_on_dlq_event():
    metrics = StreamingMetrics()
    metrics.record_dead_letter()

    health = StreamingHealthService(metrics).snapshot()

    assert health.status == "degraded"
    assert health.ready is False
    assert health.dead_lettered == 1


def test_streaming_lakehouse_pipeline_maps_to_medallion_layers():
    plan = StreamingLakehousePlanner().telemetry_pipeline(partitions=12)

    assert plan.source_topic == "redpulse.telemetry"
    assert plan.bronze_table == "bronze.telemetry"
    assert plan.silver_table == "silver.telemetry_features"
    assert plan.gold_table == "gold.fleet_intelligence"
    assert plan.workload.partitions == 12


def test_streaming_lakehouse_pipeline_rejects_invalid_partition_count():
    planner = StreamingLakehousePlanner()

    try:
        planner.telemetry_pipeline(partitions=0)
    except ValueError as exc:
        assert "partitions must be > 0" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
