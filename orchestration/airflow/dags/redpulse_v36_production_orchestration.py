from __future__ import annotations

from datetime import datetime, timedelta

from app.orchestration_v36.pipelines import telemetry_intelligence_pipeline
from app.orchestration_v36.service import ProductionOrchestrationService

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:
    DAG = None
    PythonOperator = None


def _run_stage(stage_name: str) -> None:
    """
    Airflow execution boundary for RedPulse production orchestration.

    Domain service execution is intentionally delegated to the RedPulse
    application runtime. This DAG owns scheduling, ordering, retries,
    and dependency enforcement.
    """
    print(f"RedPulse orchestration stage ready: {stage_name}")


if DAG is not None:
    pipeline = telemetry_intelligence_pipeline()
    plan = ProductionOrchestrationService().build_plan(pipeline)

    default_args = {
        "owner": "redpulse",
        "depends_on_past": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    }

    with DAG(
        dag_id="redpulse_v36_production_orchestration",
        start_date=datetime(2026, 1, 1),
        schedule=pipeline.schedule,
        catchup=False,
        max_active_runs=1,
        default_args=default_args,
        tags=["redpulse", "v3.6", "production-platform"],
    ) as dag:
        tasks = {
            stage_name: PythonOperator(
                task_id=stage_name,
                python_callable=_run_stage,
                op_kwargs={"stage_name": stage_name},
            )
            for stage_name in plan.ordered_stages
        }

        stages_by_name = {stage.name: stage for stage in pipeline.stages}

        for stage_name in plan.ordered_stages:
            stage = stages_by_name[stage_name]

            for dependency in stage.depends_on:
                tasks[dependency] >> tasks[stage_name]
