from __future__ import annotations

from dataclasses import dataclass, field

from app.data_runtime_v3.lineage import LineageEntry, LineageRegistry


@dataclass(frozen=True, slots=True)
class DecisionTrace:
    tenant_id: str
    machine_id: str
    telemetry_source: str
    dataset_version: str
    feature_version: str
    model_version: str
    prediction_id: str
    maintenance_decision_id: str | None = None
    outcome_id: str | None = None


@dataclass(slots=True)
class OperationalEvidenceLedger:
    lineage: LineageRegistry = field(default_factory=LineageRegistry)
    traces: list[DecisionTrace] = field(default_factory=list)

    def record(self, trace: DecisionTrace) -> None:
        self.traces.append(trace)
        self.lineage.record(
            LineageEntry(
                source=trace.telemetry_source,
                dataset_version=trace.dataset_version,
                feature_version=trace.feature_version,
                model_version=trace.model_version,
                prediction_id=trace.prediction_id,
            )
        )

    def for_tenant(self, tenant_id: str) -> list[DecisionTrace]:
        return [trace for trace in self.traces if trace.tenant_id == tenant_id]

    @staticmethod
    def complete(trace: DecisionTrace) -> bool:
        return all(
            (
                trace.tenant_id,
                trace.machine_id,
                trace.telemetry_source,
                trace.dataset_version,
                trace.feature_version,
                trace.model_version,
                trace.prediction_id,
            )
        )
