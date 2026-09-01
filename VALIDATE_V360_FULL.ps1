$ErrorActionPreference = "Stop"

Write-Host "`n===== REDPULSE AI v3.6.0 PLATFORM CONSOLIDATION VALIDATION ====="

Write-Host "`n===== PYTHON COMPILE ====="
python -m compileall backend\app
python -m compileall backend\tests
python -m compileall orchestration
python -m compileall analytics
python -m compileall simulator

Write-Host "`n===== V3.6 CONSOLIDATION TESTS ====="
python -m pytest backend\tests\test_v36_platform_consolidation.py -q

Write-Host "`n===== FULL TEST SUITE ====="
python -m pytest backend\tests simulator\tests -q

Write-Host "`n===== ALEMBIC ====="
Push-Location backend
python -m alembic upgrade head
Pop-Location

Write-Host "`n===== GIT DIFF CHECK ====="
git diff --check

Write-Host "`n===== STATUS ====="
git status
