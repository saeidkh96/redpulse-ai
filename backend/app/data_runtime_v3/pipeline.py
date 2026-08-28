from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class PipelineEvent:
    topic: str
    key: str
    payload: dict[str, Any]

class ReplayBuffer:
    def __init__(self) -> None:
        self.events: list[PipelineEvent] = []

    def append(self, event: PipelineEvent) -> None:
        self.events.append(event)

    def replay(self, topic: str | None = None) -> list[PipelineEvent]:
        return [e for e in self.events if topic is None or e.topic == topic]
