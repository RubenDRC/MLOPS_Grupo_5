"""
Preprocesa los datos de la tabla penguins, limpia
y guarda en penguins_clean
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import pandas as pd
import mysql.connector

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def preprocess_data():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="airflow"
        )
        cursor = conn.cursor()

        # Leer todos los registros de 'penguins'
        cursor.execute("SELECT * FROM penguins")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        print("Rows en 'penguins':", df.shape[0])

        # Limpieza de datos: dropna en columnas relevantes
        df.dropna(subset=[
            'culmen_length_mm',
            'culmen_depth_mm',
            'flipper_length_mm',
            'body_mass_g',
            'sex'
        ], inplace=True)
        print("Rows después de dropna:", df.shape[0])

        # Crear/Resetear la tabla 'penguins_clean'
        cursor.execute("DROP TABLE IF EXISTS penguins_clean;")
        cursor.execute('''
            CREATE TABLE penguins_clean (
                id INT AUTO_INCREMENT PRIMARY KEY,
                species VARCHAR(50),
                island VARCHAR(50),
                culmen_length_mm FLOAT,
                culmen_depth_mm FLOAT,
                flipper_length_mm FLOAT,
                body_mass_g FLOAT,
                sex VARCHAR(10)
            );
        ''')
        conn.commit()

        insert_query = """
            INSERT INTO penguins_clean
            (species, island, culmen_length_mm, 
             culmen_depth_mm, flipper_length_mm, 
             body_mass_g, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for _, row in df.iterrows():
            values = (
                row['species'],
                row['island'],
                row['culmen_length_mm'],
                row['culmen_depth_mm'],
                row['flipper_length_mm'],
                row['body_mass_g'],
                row['sex']
            )
            cursor.execute(insert_query, values)
        conn.commit()
        print(f"Se insertaron {df.shape[0]} filas en 'penguins_clean'.")

    except Exception as e:
        print("Error en preprocesamiento:", e)
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a MySQL cerrada.")

with DAG(
    dag_id='Preprocess_Data',
    description='Preprocesa datos de penguins y los deja en penguins_clean',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    tarea_preprocess = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocess_data
    )

    trigger_train_model = TriggerDagRunOperator(
        task_id='trigger_train_model_dag',
        trigger_dag_id='Train_Model',
        wait_for_completion=False
    )

    tarea_preprocess >> trigger_train_model
