from app.streaming.realtime import StreamingMachineSignal, StreamingWindowEngine

def test_streaming_window_engine_builds_summary():
    engine = StreamingWindowEngine(window_size=3)
    engine.ingest(StreamingMachineSignal("m1", "vibration", 1.0))
    engine.ingest(StreamingMachineSignal("m1", "vibration", 2.0))
    summary = engine.ingest(StreamingMachineSignal("m1", "temperature", 3.0))
    assert summary.sample_count == 3
    assert "vibration" in summary.sensor_means
    assert "temperature" in summary.sensor_means
