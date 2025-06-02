from airflow import DAG
from airflow.operators.python import PythonOperator
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
        if response.status_code != 200:
            raise Exception(f"Error en petición: {response.status_code}")
        return pd.DataFrame(response.json())

    df = fetch_data()

    if df.empty:
        print("No se recibieron datos. Reiniciando generación y reintentando...")
        restart = requests.get(RESTART_URL)
        if restart.status_code != 200:
            raise Exception("Error al reiniciar generación de datos")

        df = fetch_data()
        if df.empty:
            raise Exception("Sin datos incluso después de reiniciar")

    # Conexión y carga a PostgreSQL
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')
    df.to_sql('raw_data', engine, index=False, if_exists='append')

    print(f"{len(df)} filas insertadas exitosamente en 'raw_data'.")

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

    load_data

