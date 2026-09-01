from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class PipelineRunState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    retry_delay_seconds: int = 60
    exponential_backoff: bool = True

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be non-negative")


@dataclass(frozen=True, slots=True)
class OrchestrationStage:
    name: str
    depends_on: tuple[str, ...] = ()
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: int = 1800

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("stage name must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True, slots=True)
class OrchestrationPipeline:
    name: str
    schedule: str
    stages: tuple[OrchestrationStage, ...]
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("pipeline name must not be empty")
        if not self.schedule.strip():
            raise ValueError("pipeline schedule must not be empty")

        names = [stage.name for stage in self.stages]
        if len(names) != len(set(names)):
            raise ValueError("pipeline stage names must be unique")

        known = set(names)
        for stage in self.stages:
            missing = set(stage.depends_on) - known
            if missing:
                raise ValueError(f"unknown dependencies for {stage.name}: {sorted(missing)}")
            if stage.name in stage.depends_on:
                raise ValueError("stage cannot depend on itself")
