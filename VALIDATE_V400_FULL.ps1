$ErrorActionPreference = "Stop"

Write-Host "=== REDPULSE AI v4.0.0 RELEASE VALIDATION ==="
python scripts/validate_v400.py
python -m pytest backend\tests simulator\tests -q
python -m alembic -c backend\alembic.ini heads
Write-Host "=== V4.0.0 VALIDATION COMPLETE ==="
