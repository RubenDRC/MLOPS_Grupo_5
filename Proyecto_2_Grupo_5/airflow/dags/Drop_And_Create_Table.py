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
            user= "admin",
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
        # Crear la tabla
        cursor.execute('''
            CREATE TABLE covertype (
                id INT AUTO_INCREMENT PRIMARY KEY,
                elevation INT NOT NULL,  -- Elevación en metros
                aspect INT NOT NULL,  -- Azimut en grados
                slope INT NOT NULL,  -- Pendiente en grados
                horz_dist_to_hydrology INT NOT NULL,  -- Distancia horizontal al agua
                vert_dist_to_hydrology INT NOT NULL,  -- Distancia vertical al agua
                horz_dist_to_roadways INT NOT NULL,  -- Distancia horizontal a carreteras
                hillshade_9am INT NOT NULL,  -- Índice de sombra a las 9am (0-255)
                hillshade_noon INT NOT NULL,  -- Índice de sombra al mediodía (0-255)
                hillshade_3pm INT NOT NULL,  -- Índice de sombra a las 3pm (0-255)
                horz_dist_to_fire_points INT NOT NULL,  -- Distancia horizontal a puntos de incendio
                horz_dist_to_wildfire_ignition INT NOT NULL,  -- Distancia a puntos de ignición de incendios
                wilderness_area_1 BIT NOT NULL,  -- Área de wilderness, columna binaria
                wilderness_area_2 BIT NOT NULL,  -- Área de wilderness, columna binaria
                wilderness_area_3 BIT NOT NULL,  -- Área de wilderness, columna binaria
                wilderness_area_4 BIT NOT NULL,  -- Área de wilderness, columna binaria
                soil_type_1 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_2 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_3 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_4 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_5 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_6 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_7 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_8 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_9 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_10 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_11 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_12 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_13 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_14 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_15 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_16 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_17 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_18 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_19 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_20 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_21 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_22 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_23 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_24 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_25 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_26 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_27 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_28 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_29 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_30 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_31 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_32 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_33 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_34 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_35 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_36 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_37 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_38 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_39 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                soil_type_40 BIT NOT NULL,  -- Tipo de suelo, columna binaria
                cover_type INT NOT NULL,  -- Tipo de cobertura forestal (1 a 7)
            );
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabla 'covertype' creada exitosamente.")
    except Exception as e:
        print(f"Error al crear la tabla: {e}")
        raise AirflowException(f"Error al crear la tabla: {e}")

# Definición del DAG
with DAG(
    dag_id='mysql_covertype_table_dag',
    start_date=datetime(2025, 3, 28),
    schedule_interval = None,
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
