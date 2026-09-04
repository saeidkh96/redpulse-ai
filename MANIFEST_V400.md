# RedPulse AI v4.0.0 Implementation Manifest

This bundle is based on the v3.8.0 consolidated source snapshot and implements final phases A through I.

## Added

- `backend/app/platform_v40/` — production hardening, streaming, MLOps, unified intelligence, agent workflows, integrations, governance, observability, evaluation and release gate.
- `backend/app/api/v1/v40_platform.py` — v4 capabilities, unified intelligence evaluation and release-gate API.
- `backend/tests/test_v40_final_platform.py` — phase A–I regression coverage.
- `docs/releases/v4.0.0.md` — final release documentation.
- `docs/architecture/v4.0.0-target.md` — target architecture.
- `docs/V4_RELEASE_EVIDENCE.md` — release evidence matrix.
- `docs/V4_LIMITATIONS.md` — explicit limitations and non-claims.
- `infra/k8s/redpulse-v40-platform.yaml` — v4 API deployment/service contract.
- `monitoring/grafana/dashboards/redpulse-v40-overview.json` — operational dashboard definition.
- `scripts/validate_v400.py` and `VALIDATE_V400_FULL.ps1` — artifact/full validation.
- `scripts/demo_v400.py` — deterministic end-to-end maintenance scenario.

## Updated

- application version to `4.0.0`;
- v4 API router registration;
- correlation/security response headers;
- v4 platform configuration defaults;
- stale root-version assertion in `backend/tests/test_health.py`;
- README and CHANGELOG.

## Validation performed in bundle-generation environment

- v4 artifact validator: PASS;
- Python compile validation: PASS;
- v4 core tests excluding API/infrastructure-dependent test: `8 passed`;
- full repository suite: not executable in the bundle-generation environment because required repository runtime dependencies `asyncpg` and `redis` were not installed and network package installation was unavailable.

No claim is made that the complete repository regression suite has passed until `VALIDATE_V400_FULL.ps1` is executed in the project's configured environment.
