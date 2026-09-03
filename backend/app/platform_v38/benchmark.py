from dataclasses import dataclass
from time import perf_counter

@dataclass(frozen=True)
class BenchmarkResult:
    operations:int; elapsed_seconds:float; operations_per_second:float
class BenchmarkHarness:
    def run(self,operations:int,fn)->BenchmarkResult:
        if operations<1: raise ValueError("operations must be positive")
        start=perf_counter()
        for i in range(operations): fn(i)
        elapsed=max(perf_counter()-start,1e-12)
        return BenchmarkResult(operations,elapsed,operations/elapsed)
