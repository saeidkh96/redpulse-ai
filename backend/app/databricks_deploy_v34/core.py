class BundleDeploymentService:
    targets = {"dev", "staging", "prod"}
    def validate_target(self, target: str) -> bool:
        if target not in self.targets:
            raise ValueError(f"Unsupported target: {target}")
        return True
bundle_deployment_service = BundleDeploymentService()
