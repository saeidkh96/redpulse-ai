
import httpx

from simulator.models import MachineSnapshot


class RedPulseClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8001",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def send_snapshot(
        self,
        snapshot: MachineSnapshot,
    ) -> int:
        measurements = []

        for reading in snapshot.readings:
            measurements.append(
                {
                    "machine_id": snapshot.machine_id,
                    "timestamp": reading.timestamp.isoformat(),
                    "sensor": reading.sensor,
                    "value": reading.value,
                    "unit": reading.unit,
                }
            )

        response = httpx.post(
            f"{self.base_url}/api/v1/telemetry/batch",
            json={
                "measurements": measurements,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        return int(payload["inserted"])
