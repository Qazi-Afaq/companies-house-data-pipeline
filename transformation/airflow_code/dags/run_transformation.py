from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime
from airflow.sdk import DAG

DBT_PROJECT = "/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline/transformation/company_filings"
DBT_BIN = "/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline/project-venv/bin/dbt"

with DAG(
    "run_dbt_models",
    max_active_runs=1,
    start_date=datetime(2026, 6, 23),
) as dag:

    t1 = BashOperator(
        task_id="stg_filings",
        bash_command=(
            f"cd {DBT_PROJECT} "
            f"&& {DBT_BIN} run --select stg_filings"
        ),
    )

    t2 = BashOperator(
        task_id="mart_filings",
        bash_command=(
            f"cd {DBT_PROJECT} "
            f"&& {DBT_BIN} run --select mart_filings"
        ),
    )

    t1 >> t2