from dataclasses import dataclass


@dataclass(frozen=True)
class DatabricksEnvironment:
    name: str
    mode: str
    workspace_profile: str
    production: bool = False


@dataclass(frozen=True)
class ProductionJobSpec:
    name: str
    task_path: str
    target: str


class ProductionDeploymentService:
    targets = {
        "dev": DatabricksEnvironment(
            "dev", "development", "redpulse-dev"
        ),
        "staging": DatabricksEnvironment(
            "staging", "development", "redpulse-staging"
        ),
        "prod": DatabricksEnvironment(
            "prod", "production", "redpulse-prod", True
        ),
    }

    def get_target(self, target: str) -> DatabricksEnvironment:
        if target not in self.targets:
            raise ValueError(
                f"Unsupported Databricks target: {target}"
            )
        return self.targets[target]

    def validate_job(self, job: ProductionJobSpec) -> bool:
        self.get_target(job.target)

        if not job.name or not job.task_path:
            raise ValueError(
                "Databricks job requires name and task_path"
            )

        return True

    def deployment_readiness(
        self,
        target: str,
        jobs: list[ProductionJobSpec],
    ) -> dict:
        target_config = self.get_target(target)
        results = [self.validate_job(job) for job in jobs]

        return {
            "target": target_config.name,
            "mode": target_config.mode,
            "production": target_config.production,
            "jobs_valid": all(results) if jobs else False,
            "ready": bool(jobs) and all(results),
        }


production_deployment_service = ProductionDeploymentService()
