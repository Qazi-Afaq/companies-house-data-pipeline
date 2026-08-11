from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG, TaskGroup
from datetime import datetime

DBT_PROJECT = "/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline/transformation/company_filings"
DBT_BIN = "/home/afaq/learning/learning-de/projects/finance-de-projects/financial-statements-pipeline/project-venv/bin/dbt"

with DAG(
    "run_dbt_models",
    max_active_runs=1,
    start_date=datetime(2026, 6, 23),
    schedule=None,
    catchup=False,
) as dag:
    # --------- STAGING -------------
    with TaskGroup("staging") as staging:
        st1 = BashOperator(
            task_id="stg_filings",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select stg_filings"
            ),
        )
        st2 = BashOperator(
            task_id="stg_profiles",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select stg_profiles"
            ),
        )
        st3 = BashOperator(
            task_id="stg_psc",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select stg_psc"
            ),
        )
    # --------- INTERMEDIATE -------------
    with TaskGroup("intermediate") as intermediate:
        it1 = BashOperator(
            task_id="int_companies",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select int_companies"
            ),
        )
        it2 = BashOperator(
            task_id="int_psc_gender",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select int_psc_gender"
            ),
        )
        it3 = BashOperator(
            task_id="int_psc_nature_of_control",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select int_psc_nature_of_control"
            ),
        )
    # --------- MARTS -------------
    with TaskGroup("marts") as marts:
        mt1 = BashOperator(
            task_id="fct_filings",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select fct_filings"
            ),
        )
        mt2 = BashOperator(
            task_id="fct_filings_enriched",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select fct_filings_enriched"
            ),
        )
        mt3 = BashOperator(
            task_id="fct_filings_industry_rankings",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select fct_filings_industry_rankings"
            ),
        )
        mt4 = BashOperator(
            task_id="fct_psc_gender_distribution",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select fct_psc_gender_distribution"
            ),
        )
        mt5 = BashOperator(
            task_id="fct_psc_natures_of_control",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select fct_psc_natures_of_control"
            ),
        )
        mt6 = BashOperator(
            task_id="dim_companies",
            bash_command=(
                f"cd {DBT_PROJECT} "
                f"&& {DBT_BIN} run --select dim_companies"
            ),
        )

    # --------- DEPENDENCIES -------------
    # stg_profiles >> [dim_companies, int_companies]
    # int_companies >> fct_filings_industry_rankings
    st2 >> [mt6, it1]
    it1 >> mt3

    # stg_psc >> int_psc_gender >> fct_psc_gender_dist
    # stg_psc >> int_psc_noc >> fct_psc_noc
    st3 >> it2 >> mt4
    st3 >> it3 >> mt5

    # stg_filings >> fct_filings >> fct_filings_enriched
    # fct_filings_enriched >> fct_filings_industry_rankings
    st1 >> mt1 >> mt2
    mt2 >> mt3