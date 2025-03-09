from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Connection
from airflow.settings import Session
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import mysql.connector

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def create_mysql_connection():
    """
    Crea la conexión en Airflow (mysql_default) si no existe
    """
    session = Session()
    conn_id = "mysql_default"
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    if not existing_conn:
        new_conn = Connection(
            conn_id=conn_id,
            conn_type="mysql",
            host="mysql",
            schema="airflow",
            login="airflow",
            password="airflow",
            port=3306
        )
        session.add(new_conn)
        session.commit()
        print("Conexión a MySQL creada correctamente (mysql_default).")
    else:
        print("La conexión 'mysql_default' ya existe.")
    session.close()

def DropAndCreate():
    """
    Elimina la tabla 'penguins' si existe y la crea de nuevo.
    """
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
        cursor.execute("DROP TABLE IF EXISTS penguins;")
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
        print("Tabla 'penguins' creada correctamente.")
    except Exception as e:
        print(f"Error al crear/reiniciar la tabla: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a MySQL cerrada correctamente.")

with DAG(
    dag_id='Drop_And_Create_Table',
    description='Elimina y crea tabla en MySQL',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    crear_conexion_mysql = PythonOperator(
        task_id='crear_conexion_mysql',
        python_callable=create_mysql_connection
    )

    eliminar_crear_tabla = PythonOperator(
        task_id='Eliminar_Crear_tabla',
        python_callable=DropAndCreate
    )

    # Dispara el DAG Load_Data
    trigger_load_data = TriggerDagRunOperator(
        task_id='trigger_load_data_dag',
        trigger_dag_id='Load_Data',
        wait_for_completion=False
    )

    crear_conexion_mysql >> eliminar_crear_tabla >> trigger_load_data
