from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass

from .contracts import OrchestrationPipeline, PipelineRunState


@dataclass(frozen=True, slots=True)
class OrchestrationPlan:
    pipeline: str
    ordered_stages: tuple[str, ...]


class ProductionOrchestrationService:
    def build_plan(self, pipeline: OrchestrationPipeline) -> OrchestrationPlan:
        indegree = {stage.name: 0 for stage in pipeline.stages}
        graph: dict[str, list[str]] = defaultdict(list)

        for stage in pipeline.stages:
            for dependency in stage.depends_on:
                graph[dependency].append(stage.name)
                indegree[stage.name] += 1

        queue = deque(stage.name for stage in pipeline.stages if indegree[stage.name] == 0)
        ordered: list[str] = []

        while queue:
            current = queue.popleft()
            ordered.append(current)
            for child in graph[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        if len(ordered) != len(pipeline.stages):
            raise ValueError("pipeline contains a dependency cycle")

        return OrchestrationPlan(pipeline=pipeline.name, ordered_stages=tuple(ordered))

    @staticmethod
    def can_run(stage_name: str, pipeline: OrchestrationPipeline, states: dict[str, PipelineRunState]) -> bool:
        stage = next((s for s in pipeline.stages if s.name == stage_name), None)
        if stage is None:
            raise KeyError(f"unknown stage: {stage_name}")
        return all(states.get(dep) == PipelineRunState.SUCCEEDED for dep in stage.depends_on)
