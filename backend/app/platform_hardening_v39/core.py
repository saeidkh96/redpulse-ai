from dataclasses import dataclass
@dataclass(frozen=True)
class ReliabilityPolicy: max_retries:int=3; circuit_breaker_threshold:int=5; request_timeout_seconds:float=10.0
@dataclass(frozen=True)
class QuotaPolicy: requests_per_minute:int=600; concurrent_jobs:int=20
@dataclass(frozen=True)
class SLO: availability_target:float=.995; max_p95_latency_ms:float=750.0
class PlatformHardening:
 @staticmethod
 def evaluate_slo(availability,p95_latency_ms,slo): return {'availability_ok':availability>=slo.availability_target,'latency_ok':p95_latency_ms<=slo.max_p95_latency_ms,'ready':availability>=slo.availability_target and p95_latency_ms<=slo.max_p95_latency_ms}
