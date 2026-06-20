from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="riskflow_drift_check",
    description="Weekly PSI-based model drift check for RiskFlow",
    default_args=default_args,
    schedule_interval="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["riskflow", "monitoring"],
) as dag:

    check_drift = BashOperator(
        task_id="check_model_drift",
        bash_command="cd /opt/airflow/backend && python check_model_drift.py",
    )
