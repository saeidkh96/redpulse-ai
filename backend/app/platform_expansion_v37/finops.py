from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AIUsageRecord:
    tenant_id: str
    workload: str
    provider: str
    units: float
    cost_usd: float

    def __post_init__(self) -> None:
        if self.units < 0 or self.cost_usd < 0:
            raise ValueError("usage units and cost must be non-negative")


@dataclass(frozen=True, slots=True)
class CostBudget:
    tenant_id: str
    limit_usd: float
    warning_ratio: float = 0.80

    def __post_init__(self) -> None:
        if self.limit_usd <= 0:
            raise ValueError("limit_usd must be positive")
        if not 0 < self.warning_ratio <= 1:
            raise ValueError("warning_ratio must be within (0, 1]")


@dataclass(slots=True)
class AICostLedger:
    records: list[AIUsageRecord] = field(default_factory=list)

    def record(self, usage: AIUsageRecord) -> None:
        self.records.append(usage)

    def tenant_cost(self, tenant_id: str) -> float:
        return round(sum(x.cost_usd for x in self.records if x.tenant_id == tenant_id), 6)

    def by_workload(self, tenant_id: str) -> dict[str, float]:
        totals: dict[str, float] = {}
        for item in self.records:
            if item.tenant_id != tenant_id:
                continue
            totals[item.workload] = totals.get(item.workload, 0.0) + item.cost_usd
        return {name: round(value, 6) for name, value in sorted(totals.items())}

    def evaluate_budget(self, budget: CostBudget) -> dict[str, float | bool | str]:
        spent = self.tenant_cost(budget.tenant_id)
        ratio = spent / budget.limit_usd
        if ratio >= 1.0:
            state = "exceeded"
        elif ratio >= budget.warning_ratio:
            state = "warning"
        else:
            state = "healthy"
        return {
            "spent_usd": round(spent, 6),
            "limit_usd": round(budget.limit_usd, 6),
            "utilization_ratio": round(ratio, 6),
            "within_budget": ratio <= 1.0,
            "state": state,
        }
