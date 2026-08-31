from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class TopicContract:
    name: str
    partition_field: str
    consumer_group: str
    dead_letter_topic: str


TELEMETRY: Final = TopicContract(
    name="redpulse.telemetry",
    partition_field="machine_id",
    consumer_group="redpulse-telemetry-processors",
    dead_letter_topic="redpulse.telemetry.dlq",
)

ALERTS: Final = TopicContract(
    name="redpulse.alerts",
    partition_field="machine_id",
    consumer_group="redpulse-alert-processors",
    dead_letter_topic="redpulse.alerts.dlq",
)

MAINTENANCE: Final = TopicContract(
    name="redpulse.maintenance",
    partition_field="machine_id",
    consumer_group="redpulse-maintenance-processors",
    dead_letter_topic="redpulse.maintenance.dlq",
)


CONTRACTS: Final = {
    TELEMETRY.name: TELEMETRY,
    ALERTS.name: ALERTS,
    MAINTENANCE.name: MAINTENANCE,
}


def get_contract(topic: str) -> TopicContract:
    try:
        return CONTRACTS[topic]
    except KeyError as exc:
        raise ValueError(f"Unsupported streaming topic: {topic}") from exc


def partition_key(topic: str, event: dict) -> str:
    contract = get_contract(topic)

    value = event.get(contract.partition_field)
    if value is None or str(value).strip() == "":
        raise ValueError(
            f"Event for {topic} requires partition field "
            f"{contract.partition_field!r}"
        )

    return str(value)
