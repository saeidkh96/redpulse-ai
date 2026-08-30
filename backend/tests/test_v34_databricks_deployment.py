from app.databricks_deploy_v34.production import (
    ProductionDeploymentService,
    ProductionJobSpec,
)


def test_production_deployment_targets() -> None:
    service = ProductionDeploymentService()

    assert service.get_target("dev").production is False
    assert service.get_target("prod").production is True


def test_production_deployment_readiness() -> None:
    service = ProductionDeploymentService()

    jobs = [
        ProductionJobSpec(
            name="bronze-to-silver",
            task_path="databricks/jobs/bronze_to_silver.py",
            target="staging",
        ),
        ProductionJobSpec(
            name="silver-to-gold",
            task_path="databricks/jobs/silver_to_gold.py",
            target="staging",
        ),
    ]

    report = service.deployment_readiness(
        "staging",
        jobs,
    )

    assert report["ready"] is True
    assert report["jobs_valid"] is True
