from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import pandas as pd
import mysql.connector
import os

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

data_file = '/data/penguins_size.csv'

def FileValidator():
    """
    Verifica si el CSV existe en /data/penguins_size.csv
    """
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"El archivo {data_file} no existe. No se puede continuar.")
    print(f"El archivo {data_file} existe. Proceed.")

def LoadData():
    """
    Carga datos desde penguins_size.csv a la tabla 'penguins'
    """
    conn = None
    cursor = None
    try:
        df = pd.read_csv(data_file)
        df = df.dropna()  # elimina filas con nulos para evitar errores en MySQL

        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="airflow"
        )
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO penguins 
            (species, island, culmen_length_mm, 
             culmen_depth_mm, flipper_length_mm, 
             body_mass_g, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        for _, row in df.iterrows():
            cursor.execute(insert_query, (
                row['species'],
                row['island'],
                row['culmen_length_mm'],
                row['culmen_depth_mm'],
                row['flipper_length_mm'],
                row['body_mass_g'],
                row['sex']
            ))
        conn.commit()
        print("Datos cargados correctamente en 'penguins'.")
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a MySQL cerrada correctamente.")

with DAG(
    dag_id='Load_Data',
    description='Carga datos en la tabla penguins',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    tarea_validar_archivo = PythonOperator(
        task_id='validar_archivo',
        python_callable=FileValidator
    )

    tarea_cargar_datos = PythonOperator(
        task_id='cargar_datos',
        python_callable=LoadData
    )

    # Dispara siguiente DAG (Preprocess_Data)
    trigger_preprocess = TriggerDagRunOperator(
        task_id='trigger_preprocess_dag',
        trigger_dag_id='Preprocess_Data',
        wait_for_completion=False
    )

    tarea_validar_archivo >> tarea_cargar_datos >> trigger_preprocess
