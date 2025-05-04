# Config_MLFlow.py
import os, mlflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

default_args = {"start_date": days_ago(1), "retries": 1}

def configurar_mlflow():
    # MinIO
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
    os.environ["AWS_ACCESS_KEY_ID"]      = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"]  = "supersecret"

    # Tracking Server (Service mlflow:5000)
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("Proyecto_3_Diabetes_Readmission")
    mlflow.sklearn.autolog(
        log_model_signatures=True,
        log_input_examples=True,
        registered_model_name="RandomForest_Diabetes"
    )
    print(" MLflow configurado contra mlflow:5000 y MinIO.")

with DAG(
    dag_id="Mlflow_Configuration",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["setup","mlflow"]
) as dag:

    tarea = PythonOperator(
        task_id="configurar_mlflow",
        python_callable=configurar_mlflow
    )

    trigger = TriggerDagRunOperator(
        task_id="lanzar_drop_create",
        trigger_dag_id="Drop_And_Create_Table",
        wait_for_completion=False
    )

    tarea >> trigger
