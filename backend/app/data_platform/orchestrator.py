from app.data_platform.contracts import AnalyticsJobResult

class DataPlatformOrchestrator:
    def execute(self, job):
        if job.engine != "spark":
            raise ValueError(f"Unsupported analytics engine: {job.engine}")

        if job.name == "telemetry-aggregation":
            from analytics.spark.telemetry_job import aggregate_telemetry
            metadata = aggregate_telemetry(job.input_path, job.output_path)
        elif job.name == "feature-engineering":
            from analytics.spark.feature_job import build_distributed_features
            metadata = build_distributed_features(job.input_path, job.output_path)
        elif job.name == "fleet-analytics":
            from analytics.spark.fleet_job import build_fleet_analytics
            metadata = build_fleet_analytics(job.input_path, job.output_path)
        else:
            raise ValueError(f"Unsupported analytics job: {job.name}")

        return AnalyticsJobResult(
            job_name=job.name,
            status="completed",
            output_path=job.output_path,
            metadata=metadata,
        )
