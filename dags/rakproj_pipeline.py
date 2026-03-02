from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="rakproj_ml_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",   # or None for manual triggers
    catchup=False,
) as dag:

    data_import = BashOperator(
        task_id="data_import",
        bash_command="cd /opt/airflow/project && python src/data/import_raw_data.py",
    )

    preprocess = BashOperator(
        task_id="preprocess",
        bash_command="cd /opt/airflow/project && python src/data/make_dataset.py data/raw data/preprocessed",
    )

    train = BashOperator(
        task_id="train",
        bash_command="cd /opt/airflow/project && python src/main.py",
    )

    data_import >> preprocess >> train
