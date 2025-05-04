from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.hooks.base import BaseHook
from airflow.models import Connection
from airflow.settings import Session
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.exceptions import AirflowException
import mysql.connector

# Definir los argumentos del DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Crear la conexión a MySQL 
def create_mysql_connection():
    session = Session()
    conn_id = "mysql_default"
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    if not existing_conn:
        new_conn = Connection(
            conn_id=conn_id,
            conn_type="mysql",
            host= "10.43.101.195",
            login= "admin",
            password= "admingrupo5",
            schema= "data_db",
            port=3308
        )
        session.add(new_conn)
        session.commit()
        print("Conexión a MySQL creada correctamente.")
    else:
        print("La conexión a MySQL ya existe.")
        session.close()

# Eliminar la tabla si existe
def eliminar_tabla():
    try:
        db_config = {
            "host": "10.43.101.195",
            "user": "admin",
            "password": "admingrupo5",
            "database": "data_db",
            "port": 3308
        }
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS covertype;")
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabla 'covertype' eliminada si existía.")
    except Exception as e:
        print(f"Error al eliminar la tabla: {e}")
        raise AirflowException(f"Error al eliminar la tabla: {e}")

def crear_tabla():
    try:
        db_config = {
            "host": "10.43.101.195",
            "user": "admin",
            "password": "admingrupo5",
            "database": "data_db",
            "port": 3308
        }
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE covertype (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Elevation INT NOT NULL,
                Aspect INT NOT NULL,
                Slope INT NOT NULL,
                Horizontal_Distance_To_Hydrology INT NOT NULL,
                Vertical_Distance_To_Hydrology INT NOT NULL,
                Horizontal_Distance_To_Roadways INT NOT NULL,
                Hillshade_9am INT NOT NULL,
                Hillshade_Noon INT NOT NULL,
                Hillshade_3pm INT NOT NULL,
                Horizontal_Distance_To_Fire_Points INT NOT NULL,
                Wilderness_Area VARCHAR(50) NOT NULL,
                Soil_Type VARCHAR(50) NOT NULL,
                Cover_Type INT NOT NULL
            );
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabla 'covertype' creada exitosamente.")
    except Exception as e:
        raise AirflowException(f"Error al crear la tabla: {e}")

# Definición del DAG
with DAG(
    dag_id='Drop_And_Create_Table',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    # Tareas en el DAG

    create_mysql_connection = PythonOperator(
        task_id='create_mysql_connection',
        python_callable=create_mysql_connection
    )

    tarea_eliminar_tabla = PythonOperator(
        task_id='eliminar_tabla',
        python_callable=eliminar_tabla,
        dag=dag
    )

    tarea_crear_tabla = PythonOperator(
        task_id='crear_tabla',
        python_callable=crear_tabla,
        dag=dag
    )

    trigger_siguiente_tarea= TriggerDagRunOperator(
        task_id='trigger_Drop_And_Create_Table',
        trigger_dag_id='Load_Data',  # Nombre del DAG a ejecutar
        wait_for_completion=False  # Si True, espera a que el segundo DAG termine antes de completar este DAG
    )
    
    # Definir el orden de las tareas
    create_mysql_connection >> tarea_eliminar_tabla >> tarea_crear_tabla >> trigger_siguiente_tarea
