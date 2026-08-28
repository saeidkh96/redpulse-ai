from .automation_runtime import AutomationRuntime, ApprovalStore
from .governance import DecisionTrail
from .predictive_ai import ModelServingRouter
from .data_platform import DatasetCatalog, LineageStore
from .observability import MetricsRegistry, TraceBuffer
from .validation import ProductionValidator
from .models import ReadinessReport
class ProductionControlPlane:
    VERSION="2.0.0"
    def __init__(self):
        self.automation=AutomationRuntime(); self.approvals=ApprovalStore(); self.governance=DecisionTrail()
        self.models=ModelServingRouter(); self.datasets=DatasetCatalog(); self.lineage=LineageStore()
        self.metrics=MetricsRegistry(); self.traces=TraceBuffer(); self.validator=ProductionValidator()
    def readiness(self)->ReadinessReport:
        checks=self.validator.validate({"automation":True,"governance":True,"predictive_ai":True,"data_platform":True,"observability":True})
        return ReadinessReport(self.VERSION,all(c.ok for c in checks),checks)
