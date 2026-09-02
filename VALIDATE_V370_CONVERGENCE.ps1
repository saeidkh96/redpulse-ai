$ErrorActionPreference = "Stop"

Write-Host "[v3.7.0] Compile platform expansion"
python -m compileall backend/app/platform_expansion_v37

Write-Host "[v3.7.0] Run dedicated consolidation tests"
python -m pytest backend/tests/test_v37_full_roadmap_consolidation.py -q

Write-Host "[v3.7.0] Run full regression suite"
python -m pytest backend/tests simulator/tests -q

Write-Host "[v3.7.0] Validate Alembic migrations"
Push-Location backend
python -m alembic upgrade head
Pop-Location

Write-Host "[v3.7.0] Validate Git diff"
git diff --check

git status --short
