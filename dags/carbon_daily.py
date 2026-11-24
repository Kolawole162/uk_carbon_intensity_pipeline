"""Run the UK carbon intensity pipeline once a day."""
from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

with DAG(
    dag_id="uk_carbon_intensity_daily",
    description="Extract yesterday's UK regional carbon intensity, transform it and load it into Postgres",
    schedule="0 6 * * *",  # every day at 06:00 UTC
    start_date=datetime(2026, 11, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["etl", "energy"],
) as dag:
    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command=(
            "cd /opt/airflow && PYTHONPATH=/opt/airflow/src "
            "/home/airflow/pipeline-venv/bin/python -m carbon_etl.pipeline "
            "{{ dag_run.run_after | ds }}"
        ),
    )