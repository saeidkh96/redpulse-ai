def build_fleet_analytics(input_path, output_path):
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
    except ImportError as exc:
        raise RuntimeError("Install backend/requirements-streaming.txt for Spark support.") from exc

    spark = SparkSession.builder.appName("RedPulseFleetAnalytics").getOrCreate()
    frame = spark.read.parquet(input_path)
    required = {"fleet_id", "machine_id", "health_score", "failure_risk", "drift_score"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing fleet columns: {sorted(missing)}")

    result = frame.groupBy("fleet_id").agg(
        F.countDistinct("machine_id").alias("machine_count"),
        F.avg("health_score").alias("fleet_health_score"),
        F.avg("failure_risk").alias("fleet_risk_score"),
        F.avg("drift_score").alias("fleet_drift_score"),
        F.sum(
            F.when(
                (F.col("health_score") < 35) | (F.col("failure_risk") >= 0.80),
                1,
            ).otherwise(0)
        ).alias("critical_machine_count"),
    )
    result.write.mode("overwrite").parquet(output_path)
    count = result.count()
    spark.stop()
    return {"output_path": output_path, "row_count": count}
