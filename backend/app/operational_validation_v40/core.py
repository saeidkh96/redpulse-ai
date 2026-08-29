from dataclasses import dataclass
@dataclass(frozen=True)
class OperationalEvidence: ci_passed:bool; migrations_passed:bool; docker_build_passed:bool; security_scan_passed:bool; load_test_passed:bool=False; recovery_drill_passed:bool=False; deployment_verified:bool=False
@dataclass(frozen=True)
class GoLiveGate: required:tuple[str,...]=('ci_passed','migrations_passed','docker_build_passed','security_scan_passed')
class OperationalValidator:
 def evaluate(self,evidence,gate=None):
  gate=gate or GoLiveGate(); checks={n:bool(getattr(evidence,n)) for n in gate.required}; optional={n:bool(getattr(evidence,n)) for n in ('load_test_passed','recovery_drill_passed','deployment_verified')}
  return {'required_checks':checks,'optional_checks':optional,'ready':all(checks.values()),'production_validated':all(checks.values()) and all(optional.values())}
