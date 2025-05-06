import os
import mlflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

# Argumentos por defecto del DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Función para configurar MLflow
def configurar_mlflow():
    try:
        # Configuración de MinIO (almacenamiento de artefactos)
        os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
        os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'

        # Tracking server de MLflow
        mlflow.set_tracking_uri("http://mlflow:5000")

        # Definir el experimento
        mlflow.set_experiment("Proyecto_3_Diabetes_Readmission")

        # Autologging para scikit-learn
        mlflow.sklearn.autolog(
            log_model_signatures=True,
            log_input_examples=True,
            registered_model_name="RandomForest_Diabetes"
        )

        print("MLflow configurado correctamente.")

    except Exception as e:
        print(f"Error en la configuración de MLflow: {e}")
        raise

# Definición del DAG
with DAG(
    dag_id='Mlflow_Configuration',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["setup", "mlflow"]
) as dag:

    tarea_configurar_mlflow = PythonOperator(
        task_id='configurar_mlflow',
        python_callable=configurar_mlflow
    )

    trigger_drop_create_table = TriggerDagRunOperator(
        task_id='trigger_drop_create_table',
        trigger_dag_id='Drop_And_Create_Table',
        wait_for_completion=False
    )

    tarea_configurar_mlflow >> trigger_drop_create_table

