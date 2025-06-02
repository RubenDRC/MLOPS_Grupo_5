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
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')

    with engine.connect() as conn:
        # Leer datos crudos
        df = pd.read_sql('SELECT * FROM raw_data', con=conn)

        # Limpieza básica
        df.dropna(inplace=True)

        # Conversión de tipos
        df['price'] = df['price'].astype(float)
        df['bed'] = df['bed'].astype(int)
        df['bath'] = df['bath'].astype(int)
        df['acre_lot'] = df['acre_lot'].astype(float)
        df['house_size'] = df['house_size'].astype(int)
        df['prev_sold_date'] = pd.to_datetime(df['prev_sold_date'], errors='coerce')

        # Verificar si ya existe la tabla
        table_exists = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clean_data');")
        ).scalar()

        if not table_exists:
            conn.execute(text("""
                CREATE TABLE clean_data (
                    brokered_by VARCHAR,
                    status VARCHAR,
                    price FLOAT,
                    bed INTEGER,
                    bath INTEGER,
                    acre_lot FLOAT,
                    street VARCHAR,
                    city VARCHAR,
                    state VARCHAR,
                    zip_code VARCHAR,
                    house_size INTEGER,
                    prev_sold_date DATE
                );
            """))
            print("Tabla 'clean_data' creada con tipos correctos.")

        # Insertar los datos limpios
        df.to_sql('clean_data', con=conn, index=False, if_exists='append')
        print(f"Se insertaron {len(df)} filas en 'clean_data'.")

with DAG(
    dag_id='preprocess_data',
    default_args=default_args,
    description="Limpia datos de 'raw_data' manteniendo tipos y los guarda en 'clean_data'",
    schedule_interval=None,
    catchup=False
) as dag:

    preprocess_task = PythonOperator(
        task_id='preprocess_task',
        python_callable=preprocess_data
    )

    trigger_train_dag = TriggerDagRunOperator(
        task_id='trigger_train_model_dag',
        trigger_dag_id='train_model'
    )

    preprocess_task >> trigger_train_dag

