from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from time import perf_counter
from typing import Callable


@dataclass(frozen=True)
class ClassificationMetrics:
    precision: float
    recall: float
    f1: float
    false_alarm_rate: float
    missed_failure_rate: float


class Evaluator:
    @staticmethod
    def classification(y_true: list[int], y_pred: list[int]) -> ClassificationMetrics:
        if len(y_true) != len(y_pred) or not y_true:
            raise ValueError("y_true and y_pred must have equal non-zero length")
        tp = sum(1 for y, p in zip(y_true, y_pred) if y == 1 and p == 1)
        fp = sum(1 for y, p in zip(y_true, y_pred) if y == 0 and p == 1)
        fn = sum(1 for y, p in zip(y_true, y_pred) if y == 1 and p == 0)
        tn = sum(1 for y, p in zip(y_true, y_pred) if y == 0 and p == 0)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return ClassificationMetrics(precision, recall, f1, fp / (fp + tn) if fp + tn else 0.0, fn / (fn + tp) if fn + tp else 0.0)

    @staticmethod
    def early_warning_lead_time(failure_times: list[float], warning_times: list[float]) -> float:
        if len(failure_times) != len(warning_times) or not failure_times:
            raise ValueError("failure_times and warning_times must have equal non-zero length")
        return mean(max(0.0, failure - warning) for failure, warning in zip(failure_times, warning_times))


@dataclass(frozen=True)
class LoadBenchmark:
    operations: int
    elapsed_seconds: float
    throughput_ops_s: float
    mean_latency_ms: float


class PerformanceBenchmark:
    def run(self, operations: int, operation: Callable[[int], object]) -> LoadBenchmark:
        if operations < 1:
            raise ValueError("operations must be positive")
        latencies: list[float] = []
        started = perf_counter()
        for i in range(operations):
            each = perf_counter(); operation(i); latencies.append((perf_counter() - each) * 1000)
        elapsed = max(perf_counter() - started, 1e-12)
        return LoadBenchmark(operations, elapsed, operations / elapsed, mean(latencies))
