from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
import pandas as pd
import requests
from sqlalchemy import create_engine

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

GROUP_NUMBER = 5
DAY = "Tuesday"

BASE_URL = "http://10.43.101.108:80"
DATA_URL = f"{BASE_URL}/data?group_number={GROUP_NUMBER}&day={DAY}"
RESTART_URL = f"{BASE_URL}/restart_data_generation?group_number={GROUP_NUMBER}&day={DAY}"

def load_api_data_to_postgres():
    def fetch_data():
        response = requests.get(DATA_URL)
        print(f"[fetch_data] Status: {response.status_code}, Body: {response.text}")
        if response.status_code != 200:
            print("Error en petición. Lanzando excepción...")
            raise Exception(f"Error en petición: {response.status_code} - {response.text}")
        return pd.DataFrame(response.json())

    # Intentar reinicio preventivo
    print("Ejecutando reinicio preventivo...")
    restart = requests.get(RESTART_URL)
    print(f"[reinicio] Status: {restart.status_code}, Body: {restart.text}")
    if restart.status_code != 200:
        raise Exception(f"Error al reiniciar generación de datos: {restart.status_code} - {restart.text}")

    # Primer intento de carga de datos
    df = fetch_data()

    if df.empty:
        raise Exception("Sin datos incluso después de reiniciar")

    # Expandir columna 'data' a columnas normales
    df_expanded = pd.json_normalize(df["data"])

    # Conexión y carga a PostgreSQL
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')
    df_expanded.to_sql('raw_data', engine, index=False, if_exists='append')

    print(f"{len(df_expanded)} filas insertadas exitosamente en 'raw_data'.")

with DAG(
    dag_id='load_data',
    default_args=default_args,
    description="Carga datos desde API y reinicia si está vacío",
    schedule_interval=None,
    catchup=False
) as dag:

    load_data = PythonOperator(
        task_id='load_data_with_auto_restart',
        python_callable=load_api_data_to_postgres
    )
    
    trigger_preprocess_dag = TriggerDagRunOperator(
        task_id='trigger_preprocess_data_dag',
        trigger_dag_id='preprocess_data'
    )


    load_data  >> trigger_preprocess_dag

