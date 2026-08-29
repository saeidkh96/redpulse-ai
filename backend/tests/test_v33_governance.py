from app.governance_v33.core import GovernanceService

def test_tenant_aware_governance():
    service = GovernanceService()
    service.grant("catalog.redpulse.telemetry", "engineer", ["SELECT"], "plant-a")
    assert service.can_access("catalog.redpulse.telemetry", "engineer", "SELECT", "plant-a")
    assert not service.can_access("catalog.redpulse.telemetry", "engineer", "SELECT", "plant-b")

def test_lineage():
    service = GovernanceService()
    edge = service.add_lineage("bronze.telemetry", "silver.telemetry", "clean_validate")
    assert edge.target == "silver.telemetry"
