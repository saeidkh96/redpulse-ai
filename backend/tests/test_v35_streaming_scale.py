from app.streaming_scale_v35.core import (
    EventEnvelope,
    FleetPartitionPlanner,
    MicroBatchProcessor,
    SparkWorkloadSpec,
)


def test_event_envelope() -> None:
    event = EventEnvelope(
        topic="redpulse.telemetry",
        key="machine-001",
        payload={
            "machine_id": "machine-001",
            "sensor": "vibration",
            "value": 2.4,
        },
    )

    assert event.topic == "redpulse.telemetry"
    assert event.key == "machine-001"
    assert event.payload["machine_id"] == "machine-001"


def test_fleet_partitioning_is_deterministic() -> None:
    machine_ids = [
        "machine-001",
        "machine-002",
        "machine-003",
        "machine-004",
    ]

    first = FleetPartitionPlanner.partition(machine_ids, 3)
    second = FleetPartitionPlanner.partition(machine_ids, 3)

    assert first == second
    assert sum(len(items) for items in first.values()) == len(machine_ids)


def test_micro_batch_processor() -> None:
    processor = MicroBatchProcessor(batch_size=2)

    events = [1, 2, 3, 4, 5]

    batches = processor.run(
        events,
        lambda batch: list(batch),
    )

    assert batches == [
        [1, 2],
        [3, 4],
        [5],
    ]


def test_spark_workload_spec() -> None:
    workload = SparkWorkloadSpec(
        name="fleet-telemetry",
        input_table="bronze.telemetry",
        output_table="silver.telemetry",
        partitions=8,
    )

    assert workload.name == "fleet-telemetry"
    assert workload.partitions == 8
