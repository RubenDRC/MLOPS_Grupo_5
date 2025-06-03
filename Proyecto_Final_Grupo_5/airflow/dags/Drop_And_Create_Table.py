from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import psycopg2

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def create_raw_table():
    conn = psycopg2.connect(
        host="postgres-data",
        database="data_db",
        user="admin",
        password="admingrupo5",
        port=5432
    )
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS raw_data;")
    cursor.execute("""
        CREATE TABLE raw_data (
            brokered_by FLOAT,
            status TEXT,
            price FLOAT,
            bed FLOAT,
            bath FLOAT,
            acre_lot FLOAT,
            street FLOAT,
            city TEXT,
            state TEXT,
            zip_code FLOAT,
            house_size FLOAT,
            prev_sold_date TEXT
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabla 'raw_data' creada exitosamente.")

with DAG(
    dag_id='drop_and_create_raw_table',
    default_args=default_args,
    description='DAG para reiniciar la tabla raw_data y lanzar DAG de carga',
    schedule_interval=None,
    catchup=False
) as dag:

    drop_create_table = PythonOperator(
        task_id='drop_create_raw_data_table',
        python_callable=create_raw_table
    )

    trigger_load_data = TriggerDagRunOperator(
        task_id='trigger_load_data_dag',
        trigger_dag_id='load_data'
    )

    drop_create_table >> trigger_load_data

