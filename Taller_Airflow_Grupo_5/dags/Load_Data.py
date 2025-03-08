from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import pandas as pd
import mysql.connector
import os

# Definir los argumentos del DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Ruta del archivo CSV
data_file = '/data/penguins_size.csv'

# Función para validar la existencia del archivo
def FileValidator():
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"El archivo {data_file} no existe. No se puede continuar con la carga de datos.")
    print(f"El archivo {data_file} existe. Se procederá con la carga de datos.")

# Función para cargar los datos de pingüinos en la base de datos
def LoadData():
    conn = None
    cursor = None
    try:
        # Cargar los datos desde el CSV
        df = pd.read_csv(data_file)

        # Eliminar nulls  para evitar el error en MySQL
        df = df.dropna()



        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="airflow"
        )
        cursor = conn.cursor()
        
        # Insertar los datos en la tabla
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO penguins (species, island, culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, sex) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (row['species'], row['island'], row['culmen_length_mm'], row['culmen_depth_mm'], row['flipper_length_mm'], row['body_mass_g'], row['sex'])
            )
        
        conn.commit()
        print("Datos de pingüinos cargados correctamente en la base de datos.")
    except Exception as e:
        print(f"Error al cargar los datos: {e}")        
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a MySQL cerrada correctamente.")

# Definir el DAG
with DAG(
    dag_id='Load_Data',    
    description='Elimina y crea tabla en MySql',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:


    # Tarea para validar la existencia del archivo
    tarea_validar_archivo = PythonOperator(
        task_id='validar_archivo',
        python_callable=FileValidator
    )

    # Tarea para cargar los datos en la base de datos
    tarea_cargar_datos = PythonOperator(
        task_id='cargar_datos',
        python_callable=LoadData
    )

    # Tarea para disparar el siguiente DAG automáticamente
    '''
    trigger_siguiente_tarea= TriggerDagRunOperator(
        task_id='trigger_Load_Data',
        trigger_dag_id='Preprocesing_Data',  # Nombre del DAG a ejecutar
        wait_for_completion=False  # Si True, espera a que el segundo DAG termine antes de completar este DAG
    )
    '''

    tarea_validar_archivo >> tarea_cargar_datos
