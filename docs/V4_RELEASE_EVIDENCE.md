# v4.0.0 Release Evidence Matrix

| Evidence | Repository artifact | Expected validation |
|---|---|---|
| Architecture hardening | `backend/app/platform_v40/hardening.py` | v4 tests |
| Distributed streaming | `backend/app/platform_v40/streaming.py` | schema/replay/consumer-group tests |
| MLOps lifecycle | `backend/app/platform_v40/mlops.py` | champion/challenger/drift/rollback tests |
| Unified intelligence | `backend/app/platform_v40/intelligence.py` | deterministic pipeline tests |
| Human-approved agents | `backend/app/platform_v40/agents.py` | approval gate tests |
| Enterprise integration | `backend/app/platform_v40/integrations.py` | retry/signature/idempotency tests |
| Security/governance/SRE | `backend/app/platform_v40/governance.py`, `observability.py` | policy/audit/rate-limit/metric tests |
| Evaluation/benchmarking | `backend/app/platform_v40/evaluation.py` | metric and benchmark tests |
| API surface | `backend/app/api/v1/v40_platform.py` | API regression tests |
| Kubernetes deployment | `infra/k8s/redpulse-v40-platform.yaml` | YAML/schema/kubectl validation when available |
| Dashboard | `monitoring/grafana/dashboards/redpulse-v40-overview.json` | JSON parse and Grafana import |
| Full regression | `VALIDATE_V400_FULL.ps1`, `scripts/validate_v400.py` | all backend/simulator tests |

A release candidate is ready only when every required evidence field passed to `/api/v1/platform/v40/release-gate` is true.
