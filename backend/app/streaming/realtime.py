from collections import defaultdict, deque
from dataclasses import dataclass
from statistics import mean

@dataclass(frozen=True)
class StreamingMachineSignal:
    machine_id: str
    sensor: str
    value: float

@dataclass(frozen=True)
class StreamingWindowSummary:
    machine_id: str
    sample_count: int
    sensor_means: dict[str, float]
    anomaly_pressure: float

class StreamingWindowEngine:
    def __init__(self, window_size=50):
        if window_size < 2:
            raise ValueError("window_size must be at least 2")
        self.window_size = window_size
        self.buffers = defaultdict(lambda: deque(maxlen=window_size))

    def ingest(self, signal):
        buffer = self.buffers[signal.machine_id]
        buffer.append(signal)
        grouped = defaultdict(list)
        for item in buffer:
            grouped[item.sensor].append(item.value)
        means = {k: round(mean(v), 4) for k, v in grouped.items()}
        values = [abs(x.value) for x in buffer]
        mx = max(values) if values else 0.0
        avg = mean(values) if values else 0.0
        pressure = 0.0 if mx == 0 else min(1.0, avg / mx)
        return StreamingWindowSummary(signal.machine_id, len(buffer), means, round(pressure, 4))
