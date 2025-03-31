from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
import requests
import pandas as pd
import mysql.connector
import json

# Configuraciones
group_number = 5  # <-- Ajusta esto a tu número de grupo
API_URL = f"http://10.43.101.195:80/data?group_number={group_number}"

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Función para obtener datos desde la API y cargarlos a MySQL
def fetch_and_load_data():
    conn = None
    cursor = None
    try:
        # Obtener datos desde la API
        response = requests.get(API_URL)
        response.raise_for_status()

        data_json = response.json()
        data = data_json['data']

        # Definir columnas según lo entregado por la API
        columns = [
            "Elevation", "Aspect", "Slope",
            "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology",
            "Horizontal_Distance_To_Roadways", "Hillshade_9am", "Hillshade_Noon",
            "Hillshade_3pm", "Horizontal_Distance_To_Fire_Points",
            "Wilderness_Area", "Soil_Type", "Cover_Type"
        ]

        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=columns)

        # Conexión a MySQL
        conn = mysql.connector.connect(
            host="10.43.101.195",
            user="admin",
            password="admingrupo5",
            database="data_db",
            port=3308
        )
        cursor = conn.cursor()

        # Preparar consulta de inserción
        insert_query = """
            INSERT INTO covertype (
                Elevation, Aspect, Slope,
                Horizontal_Distance_To_Hydrology, Vertical_Distance_To_Hydrology,
                Horizontal_Distance_To_Roadways, Hillshade_9am, Hillshade_Noon,
                Hillshade_3pm, Horizontal_Distance_To_Fire_Points,
                Wilderness_Area, Soil_Type, Cover_Type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data_tuples = list(df.itertuples(index=False, name=None))
        cursor.executemany(insert_query, data_tuples)
        conn.commit()

        print(f"Datos insertados correctamente. Total registros: {cursor.rowcount}")

    except Exception as e:
        print(f"Error en la carga de datos: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        print("Conexión a MySQL cerrada.")

# DAG
with DAG(
    dag_id='Load_Data',
    description='Carga datos desde API del profesor a tabla covertype en MySQL',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    cargar_datos = PythonOperator(
        task_id='fetch_and_load_data',
        python_callable=fetch_and_load_data
    )

    trigger_siguiente_dag = TriggerDagRunOperator(
        task_id='trigger_next_step',
        trigger_dag_id='Preprocess_Data',  # Ajusta este DAG si no lo has creado aún
        wait_for_completion=False
    )

    cargar_datos >> trigger_siguiente_dag

