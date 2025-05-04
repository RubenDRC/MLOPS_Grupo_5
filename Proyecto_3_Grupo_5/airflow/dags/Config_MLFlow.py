import os
import mlflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

# Definir los argumentos del DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Función para configurar MLflow
def configurar_mlflow():
    try:
        # Configuración de las variables de entorno de S3 y AWS
        os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://10.43.101.195:9000"
        os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'

        # Configuración de MLflow para apuntar al servidor de seguimiento
        mlflow.set_tracking_uri("http://10.43.101.195:5000")  # Verifica que MLflow esté en ejecución

        # Configuración del experimento en MLflow
        mlflow.set_experiment("Proyecto_2_Grupo_5")

        # Configuración del autologging para modelos de scikit-learn
        mlflow.sklearn.autolog(log_model_signatures=True, log_input_examples=True, registered_model_name="RandomForestModel")

        print("MLflow configurado correctamente")
    except Exception as e:
        print(f"Error en la configuración de MLflow: {e}")
        raise

# Definición del DAG para configurar MLflow
with DAG(
    dag_id='Mlflow_Configuration',
    default_args=default_args,
    schedule_interval=None,  # Esto asegura que el DAG se ejecute manualmente
    catchup=False
) as dag:

    # Tarea para configurar MLflow
    tarea_configurar_mlflow = PythonOperator(
        task_id='configurar_mlflow',
        python_callable=configurar_mlflow,
        dag=dag
    )

    # Tarea para disparar el siguiente DAG automáticamente
    trigger_drop_create_table= TriggerDagRunOperator(
        task_id='trigger_Config_MLFlow',
        trigger_dag_id= 'Drop_And_Create_Table',  # Nombre del DAG a ejecutar
        wait_for_completion=False  # Si True, espera a que el segundo DAG termine antes de completar este DAG
    )

    tarea_configurar_mlflow >> trigger_drop_create_table
