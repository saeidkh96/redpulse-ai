def create_spark_session(app_name="RedPulseTelemetryAnalytics"):
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise RuntimeError("Install backend/requirements-streaming.txt for Spark support.") from exc
    return SparkSession.builder.appName(app_name).getOrCreate()

def aggregate_telemetry(input_path, output_path):
    spark = create_spark_session()
    frame = spark.read.parquet(input_path)
    required = {"machine_id", "sensor", "value"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing telemetry columns: {sorted(missing)}")
    from pyspark.sql import functions as F
    result = frame.groupBy("machine_id", "sensor").agg(
        F.count("*").alias("sample_count"),
        F.avg("value").alias("mean_value"),
        F.stddev_pop("value").alias("std_value"),
        F.min("value").alias("min_value"),
        F.max("value").alias("max_value"),
    )
    result.write.mode("overwrite").parquet(output_path)
    count = result.count()
    spark.stop()
    return {"output_path": output_path, "row_count": count}
