def build_distributed_features(input_path, output_path):
    try:
        from pyspark.sql import SparkSession, Window
        from pyspark.sql import functions as F
    except ImportError as exc:
        raise RuntimeError("Install backend/requirements-streaming.txt for Spark support.") from exc

    spark = SparkSession.builder.appName("RedPulseDistributedFeatures").getOrCreate()
    frame = spark.read.parquet(input_path)
    required = {"machine_id", "sensor", "value", "timestamp"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing telemetry columns: {sorted(missing)}")

    window = Window.partitionBy("machine_id", "sensor").orderBy("timestamp").rowsBetween(-9, 0)
    features = (
        frame
        .withColumn("rolling_mean_10", F.avg("value").over(window))
        .withColumn("rolling_std_10", F.stddev_pop("value").over(window))
        .withColumn("rolling_min_10", F.min("value").over(window))
        .withColumn("rolling_max_10", F.max("value").over(window))
    )
    features.write.mode("overwrite").parquet(output_path)
    count = features.count()
    spark.stop()
    return {"output_path": output_path, "row_count": count}
