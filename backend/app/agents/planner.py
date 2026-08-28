class MaintenancePlanner:
    def plan(self, objective: str) -> list[dict]:
        return [
            {"step": 1, "action": "collect_machine_context", "objective": objective},
            {"step": 2, "action": "retrieve_maintenance_evidence"},
            {"step": 3, "action": "evaluate_failure_and_health_risk"},
            {"step": 4, "action": "propose_maintenance_action"},
            {"step": 5, "action": "request_human_approval"},
            {"step": 6, "action": "dispatch_approved_action"},
            {"step": 7, "action": "verify_post_maintenance_outcome"},
        ]
