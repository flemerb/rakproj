from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.http_sensor import HttpSensor
from datetime import datetime, timedelta
import requests

default_args = {"owner": "airflow", "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="retrain_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Admin-triggered only
    catchup=False,
    params={"epochs": 10, "batch_size": 32},
) as dag:

    def trigger_training(**context):
        epochs = context["params"].get("epochs", 10)
        batch_size = context["params"].get("batch_size", 32)
        response = requests.post(
            "http://training_service:5002/train/start",
            json={"epochs": epochs, "batch_size": batch_size},
            timeout=30
        )
        print(f"Training started: {response.json()}")

    def wait_for_training(**context):
        import time
        for _ in range(360):  # wait up to 1 hour
            resp = requests.get("http://training_service:5002/train/status").json()
            if not resp["training_status"]["is_training"]:
                print("Training complete!")
                return
            time.sleep(10)
        raise Exception("Training timed out")

    preprocess = BashOperator(
        task_id="preprocess_new_data",
        bash_command='curl -s -X POST http://data_service:5001/data/preprocess -H "Content-Type: application/json" -d \'{"text_columns": ["description"]}\'',
    )

    start_training = PythonOperator(
        task_id="start_training",
        python_callable=trigger_training,
    )

    wait_training = PythonOperator(
        task_id="wait_for_training_completion",
        python_callable=wait_for_training,
    )

    reload_model = BashOperator(
        task_id="reload_model_in_prediction_service",
        bash_command='curl -s -X POST http://prediction_service:5003/model/load',
    )

    preprocess >> start_training >> wait_training >> reload_model
