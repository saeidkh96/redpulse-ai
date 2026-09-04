from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Callable


@dataclass(frozen=True)
class EventSchema:
    name: str
    version: int
    required_fields: tuple[str, ...]

    def validate(self, payload: dict) -> None:
        if self.version < 1:
            raise ValueError("schema version must be >= 1")
        missing = [field for field in self.required_fields if field not in payload]
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")


class SchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, int], EventSchema] = {}

    def register(self, schema: EventSchema) -> EventSchema:
        key = (schema.name, schema.version)
        if key in self._schemas and self._schemas[key] != schema:
            raise ValueError("schema version already registered with a different contract")
        self._schemas[key] = schema
        return schema

    def get(self, name: str, version: int) -> EventSchema:
        return self._schemas[(name, version)]


@dataclass(frozen=True)
class StreamRecord:
    topic: str
    key: str
    payload: dict
    schema_name: str
    schema_version: int
    offset: int
    event_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ReplayableEventLog:
    """Deterministic in-memory contract mirroring Kafka append/replay semantics for tests and local demos."""

    def __init__(self, registry: SchemaRegistry) -> None:
        self.registry = registry
        self._topics: dict[str, list[StreamRecord]] = {}

    def append(self, topic: str, key: str, payload: dict, schema_name: str, schema_version: int, event_id: str | None = None) -> StreamRecord:
        if not topic or not key:
            raise ValueError("topic and key are required")
        self.registry.get(schema_name, schema_version).validate(payload)
        records = self._topics.setdefault(topic, [])
        stable = event_id or sha256(f"{topic}:{key}:{len(records)}:{payload}".encode()).hexdigest()[:24]
        record = StreamRecord(topic, key, dict(payload), schema_name, schema_version, len(records), stable)
        records.append(record)
        return record

    def replay(self, topic: str, from_offset: int = 0) -> list[StreamRecord]:
        return list(self._topics.get(topic, [])[max(0, from_offset):])


class ConsumerGroup:
    def __init__(self, group_id: str) -> None:
        if not group_id:
            raise ValueError("group_id is required")
        self.group_id = group_id
        self._offsets: dict[str, int] = {}
        self._seen: set[str] = set()

    def consume(self, log: ReplayableEventLog, topic: str, handler: Callable[[StreamRecord], object]) -> list[object]:
        start = self._offsets.get(topic, 0)
        results: list[object] = []
        for record in log.replay(topic, start):
            if record.event_id not in self._seen:
                results.append(handler(record))
                self._seen.add(record.event_id)
            self._offsets[topic] = record.offset + 1
        return results

    def rewind(self, topic: str, offset: int = 0) -> None:
        self._offsets[topic] = max(0, offset)

    def lag(self, log: ReplayableEventLog, topic: str) -> int:
        return max(0, len(log.replay(topic, 0)) - self._offsets.get(topic, 0))
