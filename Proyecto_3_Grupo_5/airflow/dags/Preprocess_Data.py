from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

import pandas as pd
from sqlalchemy import create_engine, text

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def preprocess_data():
    # Conectarse a la base de datos PostgreSQL
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')

    with engine.connect() as conn:
        # Eliminar tabla si ya existe
        conn.execute(text("DROP TABLE IF EXISTS diabetic_data_clean"))

        # Leer datos desde la tabla original
        df = pd.read_sql('SELECT * FROM diabetic_data', con=conn)

        # Reemplazar "?" y "None" (cadena) por "no aplica"
        df = df.replace({"?": "no aplica", "None": "no aplica"})

        # También reemplazar valores None reales (NaN) si los hay
        df = df.fillna("no aplica")

        # Crear tabla con todas las columnas como tipo VARCHAR
        columns_str = ", ".join([f'"{col}" VARCHAR' for col in df.columns])
        conn.execute(text(f"CREATE TABLE diabetic_data_clean ({columns_str});"))

        # Cargar los datos
        df.to_sql('diabetic_data_clean', con=conn, index=False, if_exists='append')
        print(f"Datos preprocesados guardados en la tabla 'diabetic_data_clean'. Total filas: {len(df)}")

with DAG(
    dag_id='Preprocess_Data',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    preprocess_task = PythonOperator(
        task_id='preprocess_task',
        python_callable=preprocess_data
    )

    trigger_train_dag = TriggerDagRunOperator(
        task_id='trigger_train_dag',
        trigger_dag_id='Train_Model'
    )

    preprocess_task >> trigger_train_dag

