from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineDefinition:
    pipeline_id: str
    schedule: str
    tasks: list[str]


class AirflowAdapter:
    def build_dag(self, definition: PipelineDefinition):
        try:
            from airflow import DAG
            from airflow.operators.python import PythonOperator
        except ImportError as exc:
            raise RuntimeError(
                "Airflow integration requires the optional MLOps dependencies."
            ) from exc

        dag = DAG(
            dag_id=definition.pipeline_id,
            schedule=definition.schedule,
            catchup=False,
        )

        for task_id in definition.tasks:
            PythonOperator(
                task_id=task_id,
                python_callable=lambda task=task_id: {"task": task, "status": "completed"},
                dag=dag,
            )
        return dag
