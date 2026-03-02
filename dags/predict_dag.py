from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

default_args = {"owner": "airflow", "retries": 1, "retry_delay": timedelta(minutes=1)}

with DAG(
    dag_id="predict_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Only triggered via API
    catchup=False,
    params={"text": ""},
) as dag:

    def call_prediction(**context):
        text = context["params"].get("text", "")
        response = requests.post(
            "http://prediction_service:5003/predict",
            json={"text": text},
            timeout=30
        )
        result = response.json()
        print(f"Prediction result: {result}")
        return result

    load_model = BashOperator(
        task_id="ensure_model_loaded",
        bash_command='curl -s -X POST http://prediction_service:5003/model/load || true',
    )

    predict = PythonOperator(
        task_id="predict",
        python_callable=call_prediction,
    )

    load_model >> predict
