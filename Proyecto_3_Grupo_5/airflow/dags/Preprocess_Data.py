import mysql.connector
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowException
from airflow.operators.trigger_dagrun import TriggerDagRunOperator



default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Configuración de la base de datos
DB_CONFIG = {
    "host": "10.43.101.195",
    "user": "admin",
    "password": "admingrupo5",
    "database": "data_db",
    "port": 3308
}

# Función de preprocesamiento
def preprocesar_datos():
    try:
        # Conexión a MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Extraer datos
        cursor.execute("SELECT * FROM covertype")
        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        # Eliminar valores nulos
        df.dropna(inplace=True)


        # Eliminar tabla si existe
        cursor.execute("DROP TABLE IF EXISTS covertype_clean")

        # Crear nueva tabla limpia (sin variables codificadas)
        cursor.execute('''
            CREATE TABLE covertype_clean (
                Elevation INT,
                Aspect INT,
                Slope INT,
                Horizontal_Distance_To_Hydrology INT,
                Vertical_Distance_To_Hydrology INT,
                Horizontal_Distance_To_Roadways INT,
                Hillshade_9am INT,
                Hillshade_Noon INT,
                Hillshade_3pm INT,
                Horizontal_Distance_To_Fire_Points INT,
                Wilderness_Area VARCHAR(50),
                Soil_Type VARCHAR(50),
                Cover_Type INT
            );
        ''')

        # Seleccionar columnas que deseas mantener
        columnas = [
            'Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology',
            'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways',
            'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm',
            'Horizontal_Distance_To_Fire_Points', 'Wilderness_Area',
            'Soil_Type', 'Cover_Type'
        ]
        df = df[columnas]

        # Convertir a lista de tuplas
        data = list(map(tuple, df.values))

        # Insertar en la tabla nueva
        insert_query = f"""
            INSERT INTO covertype_clean (
                {', '.join(columnas)}
            ) VALUES (
                {', '.join(['%s'] * len(columnas))}
            )
        """
        cursor.executemany(insert_query, data)
        conn.commit()

        print(f"Datos preprocesados e insertados correctamente. Registros: {cursor.rowcount}")

        # Cerrar conexión
        cursor.close()
        conn.close()

    except Exception as e:
        raise AirflowException(f"Error en preprocesamiento: {e}")

# DAG
with DAG(
    dag_id='Preprocess_Data',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    preprocesar_datos_task = PythonOperator(
        task_id='preprocesar_datos',
        python_callable=preprocesar_datos
    )

    trigger_train_model = TriggerDagRunOperator(
        task_id='trigger_train_model_dag',
        trigger_dag_id='Train_Model',
        wait_for_completion=False
    )

    preprocesar_datos_task >> trigger_train_model

