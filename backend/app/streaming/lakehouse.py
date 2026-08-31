from __future__ import annotations

from dataclasses import dataclass

from app.streaming_scale_v35.core import SparkWorkloadSpec


@dataclass(frozen=True, slots=True)
class LakehouseHandoff:
    source_topic: str
    bronze_table: str
    silver_table: str
    gold_table: str
    workload: SparkWorkloadSpec


class StreamingLakehousePlanner:
    def telemetry_pipeline(
        self,
        partitions: int = 8,
    ) -> LakehouseHandoff:
        if partitions <= 0:
            raise ValueError("partitions must be > 0")

        return LakehouseHandoff(
            source_topic="redpulse.telemetry",
            bronze_table="bronze.telemetry",
            silver_table="silver.telemetry_features",
            gold_table="gold.fleet_intelligence",
            workload=SparkWorkloadSpec(
                name="telemetry-streaming-pipeline",
                input_table="bronze.telemetry",
                output_table="silver.telemetry_features",
                partitions=partitions,
            ),
        )
