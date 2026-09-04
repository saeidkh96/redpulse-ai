from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    ROOT / "backend/app/platform_v40/hardening.py",
    ROOT / "backend/app/platform_v40/streaming.py",
    ROOT / "backend/app/platform_v40/mlops.py",
    ROOT / "backend/app/platform_v40/intelligence.py",
    ROOT / "backend/app/platform_v40/agents.py",
    ROOT / "backend/app/platform_v40/integrations.py",
    ROOT / "backend/app/platform_v40/governance.py",
    ROOT / "backend/app/platform_v40/evaluation.py",
    ROOT / "backend/app/platform_v40/observability.py",
    ROOT / "backend/app/platform_v40/release.py",
    ROOT / "backend/app/api/v1/v40_platform.py",
    ROOT / "docs/releases/v4.0.0.md",
    ROOT / "docs/V4_RELEASE_EVIDENCE.md",
    ROOT / "docs/V4_LIMITATIONS.md",
    ROOT / "infra/k8s/redpulse-v40-platform.yaml",
    ROOT / "monitoring/grafana/dashboards/redpulse-v40-overview.json",
]

missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
if missing:
    print(json.dumps({"ready": False, "missing": missing}, indent=2))
    sys.exit(1)

with (ROOT / "monitoring/grafana/dashboards/redpulse-v40-overview.json").open(encoding="utf-8") as handle:
    json.load(handle)

print(json.dumps({"ready": True, "artifacts": len(REQUIRED), "version": "4.0.0"}, indent=2))
