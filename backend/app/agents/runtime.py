from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import time
import uuid

class RunStatus(str, Enum):
    PENDING = "pending"
    WAITING_APPROVAL = "waiting_approval"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentRun:
    run_id: str
    objective: str
    status: RunStatus = RunStatus.PENDING
    steps: list[dict[str, Any]] = field(default_factory=list)
    audit: list[dict[str, Any]] = field(default_factory=list)

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def call(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name](**kwargs)

    def names(self) -> list[str]:
        return sorted(self._tools)

class AgentRuntime:
    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools
        self.runs: dict[str, AgentRun] = {}

    def create(self, objective: str) -> AgentRun:
        run = AgentRun(run_id=str(uuid.uuid4()), objective=objective)
        self.runs[run.run_id] = run
        self._audit(run, "run_created", {"objective": objective})
        return run

    def require_approval(self, run: AgentRun, reason: str) -> None:
        run.status = RunStatus.WAITING_APPROVAL
        self._audit(run, "approval_required", {"reason": reason})

    def approve(self, run_id: str, actor: str) -> AgentRun:
        run = self.runs[run_id]
        run.status = RunStatus.RUNNING
        self._audit(run, "approved", {"actor": actor})
        return run

    def execute_tool(self, run_id: str, tool: str, **kwargs: Any) -> Any:
        run = self.runs[run_id]
        if run.status == RunStatus.WAITING_APPROVAL:
            raise PermissionError("run requires human approval")
        run.status = RunStatus.RUNNING
        result = self.tools.call(tool, **kwargs)
        run.steps.append({"tool": tool, "input": kwargs, "result": result})
        self._audit(run, "tool_executed", {"tool": tool})
        return result

    def complete(self, run_id: str) -> AgentRun:
        run = self.runs[run_id]
        run.status = RunStatus.COMPLETED
        self._audit(run, "run_completed", {})
        return run

    @staticmethod
    def _audit(run: AgentRun, event: str, payload: dict[str, Any]) -> None:
        run.audit.append({"timestamp": time.time(), "event": event, "payload": payload})
