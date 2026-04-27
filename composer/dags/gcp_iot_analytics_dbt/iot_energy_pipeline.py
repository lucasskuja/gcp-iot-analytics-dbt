from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator


GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "demo-project")
GCP_REGION = os.getenv("GCP_REGION", "us-central1")
DAG_ROOT = os.path.dirname(os.path.abspath(__file__))
DBT_DIR = os.path.join(DAG_ROOT, "dbt_project")
DBT_PROFILES_DIR = DBT_DIR
DBT_TARGET = os.getenv("DBT_TARGET", "dev")
INGESTION_JOB_NAME = os.getenv("INGESTION_CLOUD_RUN_JOB", "iot-energy-ingestion-job")


def emit_metrics() -> None:
    print("pipeline_status=success")
    print("metric_records_ingested=mocked")
    print("metric_dbt_models_built=mocked")
    print("metric_dbt_tests_executed=mocked")
    print("alert_channel=mock-slack")


default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="iot_energy_end_to_end",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["gcp", "bigquery", "dbt", "composer", "cloud-run", "iot"],
) as dag:
    ingest_task = CloudRunExecuteJobOperator(
        task_id="run_ingestion_cloud_run_job",
        project_id=GCP_PROJECT_ID,
        region=GCP_REGION,
        job_name=INGESTION_JOB_NAME,
        overrides={
            "container_overrides": [
                {
                    "args": [
                        "--execution-date",
                        "{{ ds }}T00:00:00",
                        "--intervals",
                        "96",
                        "--output-dir",
                        "/tmp/iot-energy-data",
                    ]
                }
            ]
        },
    )

    dbt_deps_task = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_DIR} && dbt deps --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    dbt_run_task = BashOperator(
        task_id="dbt_run_models",
        bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    dbt_snapshot_task = BashOperator(
        task_id="dbt_snapshot_status",
        bash_command=f"cd {DBT_DIR} && dbt snapshot --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    dbt_test_task = BashOperator(
        task_id="dbt_test_models",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}",
    )

    observability_task = PythonOperator(
        task_id="emit_pipeline_metrics",
        python_callable=emit_metrics,
    )

    ingest_task >> dbt_deps_task >> dbt_run_task >> dbt_snapshot_task >> dbt_test_task >> observability_task
