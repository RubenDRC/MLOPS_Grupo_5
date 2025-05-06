from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import pandas as pd
from sqlalchemy import create_engine

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def load_csv_to_postgres():
    # Ruta del archivo CSV dentro del contenedor
    csv_path = "/opt/airflow/data/diabetic_data.csv"

    # Leer CSV
    df = pd.read_csv(csv_path)

    # Eliminar columnas 'encounter_id' y 'patient_nbr'
    df = df.drop(columns=['encounter_id', 'patient_nbr'])

    # Estandarizar nombres de columnas: minúsculas y reemplazo de guiones por guión bajo
    df.columns = [col.lower().replace('-', '_') for col in df.columns]


    # Conexión a la base de datos PostgreSQL
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')

    # Cargar a la tabla 'diabetic_data'
    df.to_sql('diabetic_data', engine, index=False, if_exists='append')
    print(f"Se cargaron {len(df)} filas limpias en la tabla 'diabetic_data'.")

with DAG(
    dag_id='Load_Data',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    load_csv = PythonOperator(
        task_id='load_csv_to_postgres',
        python_callable=load_csv_to_postgres
    )

    trigger_preprocess_data = TriggerDagRunOperator(
        task_id='trigger_preprocess_data',
        trigger_dag_id='Preprocess_Data'
    )

    load_csv >> trigger_preprocess_data

