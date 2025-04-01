from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.hooks.base import BaseHook
from airflow.models import Connection
from airflow.settings import Session
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import mysql.connector

# Definir los argumentos del DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Crear la conexión a MySQL si no existe
def create_mysql_connection():
    session = Session()
    conn_id = "mysql_default"
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    if not existing_conn:
        new_conn = Connection(
            conn_id=conn_id,
            conn_type="mysql",
            host="mysql",  # Nombre del servicio en Docker
            schema="airflow",
            login="airflow",
            password="airflow",
            port=3306
        )
        session.add(new_conn)
        session.commit()
        print("Conexión a MySQL creada correctamente.")
    else:
        print("La conexión a MySQL ya existe.")
    session.close()


# Función para verificar y resetear la tabla
def DropAndCreate():
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
        
        # Verificar si la tabla existe y eliminarla
        cursor.execute("DROP TABLE IF EXISTS penguins;")
        
        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE penguins (
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
        print("Tabla 'penguins' creada correctamente o reiniciada.")
    except Exception as e:
        print(f"Error al crear/reiniciar la tabla: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a MySQL cerrada correctamente.")


# Definir el DAG
with DAG(
    dag_id='Drop_And_Create_Table',
    description='Elimina y crea tabla en MySql',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False #No ejecutar procesos historicos o anteriores a la fecha
) as dag:


     # Tarea con PythonOperator para crear la conexión si no existe
    crear_conexion_mysql = PythonOperator(
        task_id='crear_conexion_mysql',
        python_callable=create_mysql_connection
    )


    # Tarea con PythonOperator para verificar y reiniciar la tabla
    Eliminar_crear_tabla = PythonOperator(
        task_id='Eliminar_Crear_tabla',
        python_callable=DropAndCreate
    )

     # Tarea para disparar el siguiente DAG automáticamente
    trigger_siguiente_tarea= TriggerDagRunOperator(
        task_id='trigger_Drop_And_Create_Table',
        trigger_dag_id='Load_Data',  # Nombre del DAG a ejecutar
        wait_for_completion=False  # Si True, espera a que el segundo DAG termine antes de completar este DAG
    )

    crear_conexion_mysql >> Eliminar_crear_tabla >> trigger_siguiente_tarea
