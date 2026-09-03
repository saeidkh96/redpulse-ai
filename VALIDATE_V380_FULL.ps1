$ErrorActionPreference = "Stop"
Write-Host "=== RedPulse AI v3.8.0 validation ==="
python -m pytest backend\tests\test_v38_platform_consolidation.py -q
python -m pytest backend\tests simulator\tests -q
Push-Location backend
python -m alembic current
python -m alembic heads
Pop-Location
git diff --check
git status --short
