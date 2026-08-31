$ErrorActionPreference = "Stop"

Write-Host "`n===== COMPILE ====="
python -m compileall backend\app backend\tests orchestration analytics simulator

Write-Host "`n===== V3.5 STREAMING TESTS ====="
python -m pytest `
  backend\tests\test_v35_streaming_scale.py `
  backend\tests\test_v35_streaming_reliability.py `
  backend\tests\test_v35_kafka_reliability.py `
  backend\tests\test_v35_streaming_health_lakehouse.py `
  backend\tests\test_kafka_adapter_optional.py `
  backend\tests\test_realtime_streaming.py `
  backend\tests\test_streaming_events.py -q

Write-Host "`n===== FULL TESTS ====="
python -m pytest backend\tests simulator\tests -q

Write-Host "`n===== STATUS ====="
git --no-pager status
